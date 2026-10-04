<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Secret Management Architecture — SOPS + age Migration

**Status**: Design approved
**Date**: 2026-07-08
**Author**: Sisyphus (AI)
**Repository**: opendesk-edu

---

## Overview

Replace the current `derivePassword` + `sha1sum` secret derivation scheme in
`opendesk-edu` with a **gradual, two-tier** approach:

1. **Phase 0 (immediate)**: Harden the existing scheme (`sha1sum → sha256sum`,
   remove weak default password)
2. **Phases 1–3 (gradual)**: Layer Mozilla SOPS with age encryption on top,
   migrating secrets per-category from derivePassword to encrypted YAML files

The derivePassword scheme is kept for **dev/test** environments where
deterministic secret derivation from a single `MASTER_PASSWORD` env var is
convenient. **Production** secrets move to SOPS-encrypted `.enc.yaml` files
committed to git, decrypted at deploy time via the age private key.

---

## Current State

### Secret Flow

```
secrets.yaml.gotmpl  (source of truth: derivePassword expressions)
         │
         ▼
helmfile_generic.yaml.gotmpl  (loads default/*.yaml.gotmpl via YAML anchor)
         │
         ▼
.Values.secrets.*  (templated values)
         │
         ▼
per-app values.yaml.gotmpl  (maps .Values.secrets.* to .Values.app.*)
         │
         ▼
chart templates/secret.yaml  (creates K8s Secret resource)
```

### Current Weaknesses

| Issue | Impact |
|---|---|
| `sha1sum` for password derivation | Cryptographically weak — SHA1 is deprecated |
| Default `MASTER_PASSWORD="sovereign-workplace"` | Known plaintext — anyone who reads git can compute ALL secrets |
| Simple salt pattern: `<app>_<key>` | Deterministic rainbow-table resistance is minimal |
| One master password = all secrets | No granular rotation — change MASTER_PASSWORD, change everything |
| Recipe is in git | The derivation formula is public (but actual values require MASTER_PASSWORD) |
| No audit trail | No `git blame` on individual secret values — only on the recipe |
| No rotation without redeploy | Changing one secret requires changing MASTER_PASSWORD and redeploying everything |

### Secret Inventory (157 secrets in 25 categories)

| Category | Count | Example Secrets |
|---|---|---|
| `postgresql.*` | 12 | DB users: keycloak, nextcloud, openproject, xwiki, matrix, etc. |
| `keycloak.clientSecret.*` | 14 | OIDC clients: portal, dovecot, matrix, jitsi, openproject, xwiki, opencloud, etc. |
| `keycloak.adminPassword` | 1 | Keycloak admin |
| `mariadb.*` | 4 | root, xwiki, openxchange, nextcloud |
| `minio.*` | 8 | root, dovecot, nextcloud, notes, openproject, etc. |
| `nubus.*` | ~20 | masterpassword, ldap, portal, selfservice, provisioning, NATS |
| `oxAppSuite.*` | 11 | admin, basicAuth, sessiond, oxguard, etc. |
| `jitsi.*` | 7 | jwtAppSecret, jibri, jicofo, jvb |
| `opencloud.*` | 6 | jwtSecret, transferSecret, apiKeys |
| `nextcloud.*` | 3 | admin, metricsToken, statusPassword |
| Other (synapse, matrix, dovecot, redis, etc.) | ~70 | Various service passwords |

---

## Design

### Architecture (Post-Migration)

```
┌──────────────────────────────────────────────────────────────────┐
│                        Git Repository                             │
│                                                                    │
│  helmfile/environments/default/                                    │
│   ├── secrets.yaml.gotmpl        ← derivePassword (DEV only)      │
│   ├── secrets.prod.enc.yaml      ← SOPS/age encrypted (PROD)      │
│   └── ... (37 other .yaml.gotmpl files)                           │
│                                                                    │
│  .sops.yaml                    ← SOPS config                      │
│  .sops-age.pub                 ← public age key (committed)        │
│                                                                    │
│  age private key              ← NOT in git (~/.age/ or env var)    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │   helmfile sync               │
               │   │                            │
               │   ├── default/*.yaml.gotmpl    │
               │   │   (templated, dev secrets)  │
               │   └── default/*.enc.yaml       │
               │       (SOPS-decrypted, prod)    │
               └──────────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   ArgoCD             │
                    │   CMP sidecar        │
                    │   (sops-age)         │
                    └──────────┬──────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │   K3s Cluster    │
                     │   K8s Secrets    │
                     └─────────────────┘
```

### Key Design Decisions

1. **Same YAML structure, different content**:
   - Dev `secrets.yaml.gotmpl`: `postgres_password: {{ derivePassword 1 "long" ... | sha256sum }}`
   - Prod `secrets.prod.enc.yaml`: `postgres_password: "actual-64-char-random-string"`
   - Both resolve to the same `.Values.secrets.postgresql.postgres_password` — **zero chart template changes**

2. **Glob-based loading order**:
   - `.enc.yaml` files are loaded AFTER `.yaml.gotmpl` files
   - Prod overrides dev defaults via later merge
   - If no age key is present, `*.enc.yaml` is treated as plain YAML or skipped

3. **Dual load is intentional**:
   - Both `secrets.yaml.gotmpl` (dev defaults) and `secrets.prod.enc.yaml` (prod overrides)
     are loaded simultaneously via the glob `helmfile/environments/default/*.{yaml.gotmpl,enc.yaml}`
   - In **prod**: `.enc.yaml` values override `.yaml.gotmpl` values. The derivePassword
     expressions in `.yaml.gotmpl` are still evaluated but immediately overwritten
     by the encrypted values. This is harmless — the template engine evaluates both,
     and the last writer wins.
   - In **dev**: If no `.enc.yaml` exists or SOPS is not configured, only `.yaml.gotmpl`
     values are used. The glob simply doesn't match any `.enc.yaml` file.

4. **Per-category migration (not all-at-once)**:
   - Start with P0: `postgresql.*` and `keycloak.*` (most critical, 27 secrets)
   - Each category gets its own commit and ArgoCD sync cycle
   - Rollback = revert the commit

5. **Age over GPG**:
   - Simpler key management (single file, no key servers)
   - Smaller encrypted payloads
   - Modern crypto (X25519)

6. **OIDC client secrets**:
   - SOPS provides the **initial seed** for Keycloak client registration
   - After Keycloak registers the client (which may regenerate the secret), the
     `sync-oidc-secret-job` pattern (already in SOGo chart) syncs the actual secret
     from Keycloak → K8s Secret
   - This pattern should be expanded to all OIDC-consuming apps

### SOPS File Format

```yaml
# secrets.prod.enc.yaml (plaintext view, before encryption)
secrets:
  postgresql:
    postgresUser: "a1b2c3d4e5f6g7h8i9j0..."
    keycloakUser: "b2c3d4e5f6g7h8i9j0k1..."
    # ...
  keycloak:
    adminPassword: "c3d4e5f6g7h8i9j0k1l2..."
    clientSecret:
      portal: "d4e5f6g7h8i9j0k1l2m3..."
      # ...
```

After `sops --encrypt`, each value becomes an encrypted envelope:
```yaml
secrets:
  postgresql:
    postgresUser: ENC[AES256_GCM,data:...,iv:...,tag:...,type:str]
```

---

## Implementation Phases

### Phase 0 — Harden Current Scheme (~30min)

**Files changed**: `helmfile/environments/default/secrets.yaml.gotmpl`

1. Replace all `sha1sum` → `sha256sum` (single bulk sed)
2. Replace `env "MASTER_PASSWORD" | default "sovereign-workplace"` → `env "MASTER_PASSWORD" | required "MASTER_PASSWORD env var is required"`

**Risk**: All derived secrets change on next `helmfile sync`. Must coordinate:
- Update Keycloak OIDC client secrets after deployment
- Update any external service that has manually-configured credentials

### Phase 1 — SOPS Infrastructure (~1h)

**New files**:
- `.sops.yaml` — SOPS configuration file
- `.sops-age.pub` — Public age key (committed)

**Changed files**:
- `helmfile_generic.yaml.gotmpl` — Add `*.enc.yaml` to the values glob

**Steps**:
1. Generate age key pair on deployer workstation
2. Create `.sops.yaml` pointing to the public key
3. Modify `helmfile_generic.yaml.gotmpl` to load `*.enc.yaml` files
4. Install `sops` CLI on all deployer workstations
5. Configure ArgoCD CMP sidecar for SOPS decryption

### Phase 2 — Encrypt P0 Secrets (~2h)

**New files**:
- `helmfile/environments/default/secrets.prod.enc.yaml` (initially: postgresql + keycloak sections only)

**Steps**:
1. Generate strong random passwords using `openssl rand -base64 48`
2. Create plaintext YAML with the same structure as `secrets.yaml.gotmpl` but with literal values
3. Encrypt with `sops --encrypt`
4. Verify: `helmfile -e prod build` produces correct values
5. Deploy and verify all database connections and Keycloak SSO

### Phase 3 — Encrypt Remaining Secrets (~3h, per-category)

**Steps** (per category):
1. Generate secrets for the category
2. Add to `secrets.prod.enc.yaml`
3. Deploy and verify
4. Repeat for P1 (minio, mariadb, nubus), then P2-P3

### Post-Migration

- **Dev workflows**: Unchanged — set `MASTER_PASSWORD` and run `helmfile sync`
- **Prod workflows**: `helmfile -e prod sync` uses SOPS-decrypted values
- **Rotation**: `sops -d → edit → sops -e → git commit → deploy`
- **Disaster recovery**: Restore age private key from backup, re-deploy

---

## Rotation Workflow

```bash
# 1. Decrypt current secrets
sops -d helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets.yaml

# 2. Edit the value to rotate
vim /tmp/secrets.yaml  # change postgresql.keycloakUser

# 3. Re-encrypt
sops -e /tmp/secrets.yaml > helmfile/environments/default/secrets.prod.enc.yaml

# 4. Commit with descriptive message
git add helmfile/environments/default/secrets.prod.enc.yaml
git commit -m "rotation: rotate postgresql.keycloakUser"

# 5. Deploy
git push  # ArgoCD syncs
# Or: helmfile -e prod sync
```

**For DB passwords**: The rotation requires either:
- A dual-validity window (old + new password both work during rollout)
- OR: execute `ALTER USER ... PASSWORD` in the database BEFORE rolling out the new secret
- OR: accept brief authentication failures during pod rolling restart

The existing `update-password/` Helm Job pattern (in mariadb sub-charts for ILIAS, Limesurvey, Bookstack) handles this — it runs `ALTER USER` as a pre-upgrade hook before the chart updates the K8s Secret.

---

## Disaster Recovery

**If the cluster is lost but git + age key survive**:
1. Install K3s on new nodes
2. Deploy ArgoCD with SOPS CMP sidecar, mount the age private key
3. Point ArgoCD at the same git repo
4. ArgoCD syncs everything — SOPS decrypts `.enc.yaml` → Helm renders → K8s Secrets are created with identical values

**If the age private key is lost but the cluster survives**:
1. Generate a new age key pair
2. Re-encrypt all `.enc.yaml` files with the new public key:
   ```bash
   sops -d secrets.prod.enc.yaml | sops --encrypt --age NEW_PUBKEY > secrets.prod.enc.yaml
   ```
3. Commit and re-deploy

**Prevention**: Store the age private key in the team's shared password manager (Bitwarden/Vaultwarden) and in an offline backup (USB stick in a fireproof safe). Never store it only on a single laptop.

---

## Integration Points

| Component | What Changes |
|---|---|
| `helmfile.yaml.gotmpl` | Environment-specific `*.enc.yaml` glob added |
| `helmfile_generic.yaml.gotmpl` | `*.enc.yaml` added to the values YAML anchor |
| `secrets.yaml.gotmpl` | Phase 0: sha256sum + required. Phase 2-3: retained for dev only |
| `secrets.prod.enc.yaml` | **New**: SOPS-encrypted production secrets |
| `.sops.yaml` | **New**: SOPS configuration (creation rules, key) |
| `.sops-age.pub` | **New**: Public age key committed to repo |
| App `values.yaml.gotmpl` | **No changes** — still references `.Values.secrets.*` |
| Chart `secret.yaml` | **No changes** — still creates K8s Secret from `.Values.*` |
| ArgoCD repo-server | **New**: CMP sidecar container for SOPS decryption |
| CI/CD pipeline | Pre-deploy step: verify age key is available |
| Developer workstation | Install `sops` + `age` CLI tools |

---

## Security Considerations

1. **age private key at rest**: Stored on deployer workstation and ArgoCD server. Protected by filesystem permissions (0600). Backed up to offline storage.

2. **Secrets in transit**: `helmfile sync` decrypts locally and sends plaintext to the K8s API over TLS. The K8s API stores secrets in etcd (encrypted at rest if configured).

3. **Secrets in ArgoCD**: The CMP sidecar decrypts in-memory during rendering. Decrypted values are not written to disk on the ArgoCD server (they exist only in the Helm template output stream).

4. **Git history**: Once a `secrets.prod.enc.yaml` is committed, it's encrypted. However, if an earlier commit contained plaintext secrets, they remain in git history. Use `git filter-repo` to scrub if needed.

5. **Audit trail**: `git log --follow secrets.prod.enc.yaml` with commit messages like `rotation: rotate postgresql.keycloakUser` provides a full audit trail. The age key cannot produce a valid signature, but git author identity + commit message convention fills this gap.

---

## Open Questions / Future Work

1. **CI/CD integration**: If CI runs `helmfile sync`, where does it get the age private key? Options: CI secret store (GitHub Actions secrets, GitLab CI variables), or only deploy from workstations.

2. **SAML certificates**: Moodle SAML certs (`moodleSaml.spCert`, `moodleSaml.idpCert`) are PEM-encoded certificates, not passwords. These are large strings that may exceed SOPS's per-field limits for inline encryption. May need a separate encrypted file or a different approach (store as separate files, encrypt with SOPS).

3. **NATS password prefix**: The current scheme adds `printf "n%s"` prefix to some NATS passwords. This prefix is derived, not stored. In the SOPS file, the prefixed value must be stored directly (not the raw base).

4. **ArgoCD CMP sidecar testing**: The sops-age CMP image needs validation on the actual cluster before production use. Plan a dry run on a staging namespace first.
