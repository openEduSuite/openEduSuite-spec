<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Secret Management Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate opendesk-edu from `derivePassword` + `sha1sum` to SOPS (age) encrypted secrets for production, retaining derivePassword for dev.

**Architecture:** Four-phase approach: (0) harden existing scheme with sha256sum + required MASTER_PASSWORD, (1) install SOPS tooling + age keys + helmfile integration, (2) encrypt P0 secrets (postgresql + keycloak), (3) encrypt remaining secrets per-category. No chart template changes needed — all integration is at the helmfile values layer.

**Tech Stack:** Mozilla SOPS, age encryption, helmfile glob patterns, ArgoCD CMP sidecar

**Design spec:** `specs/automation/2026-07-08-secret-management-design.md`

**Main repo:** `/srv/openedusuite/`
**Spec repo:** `/srv/openedusuite/openEduSuite-spec/`

---

## File Inventory

### Files Modified
| File | What Changes |
|---|---|
| `helmfile/environments/default/secrets.yaml.gotmpl` | Phase 0: sha1sum→sha256sum, remove default password |
| `helmfile_generic.yaml.gotmpl` | Phase 1: add `*.enc.yaml` to values glob |

### Files Created
| File | What It Is |
|---|---|
| `.sops.yaml` (repo root) | SOPS config — creation rules, age public key reference |
| `.sops-age.pub` (repo root) | Public age key committed to git |
| `helmfile/environments/default/secrets.prod.enc.yaml` | SOPS-encrypted production secrets (initially P0, grows by category) |

### Files NOT Changed (intentionally)
| File | Rationale |
|---|---|
| Any `chart/**/secret.yaml` | No template changes needed — `.Values.secrets.*` resolves identically |
| Any app `values.yaml.gotmpl` | Still references `.Values.secrets.*` — no change |
| Any `helmfile-child.yaml.gotmpl` | Values loading is at the parent level only |

---

## Phase 0 — Harden Current Scheme

### Task 0.1: Bulk replace sha1sum → sha256sum in secrets.yaml.gotmpl

**Files:**
- Modify: `opendesk-edu/helmfile/environments/default/secrets.yaml.gotmpl`

- [ ] **Replace sha1sum with sha256sum**

Run:
```bash
cd /srv/openedusuite
sed -i 's/sha1sum/sha256sum/g' helmfile/environments/default/secrets.yaml.gotmpl
```

Verify only the hash function changed, not the structure:
```bash
grep -c 'sha256sum' helmfile/environments/default/secrets.yaml.gotmpl
# Expected: 157 (every secret line)
grep -c 'sha1sum' helmfile/environments/default/secrets.yaml.gotmpl
# Expected: 0
```

- [ ] **Check for non-standard derivations (b64enc, printf, trunc)**

Some secrets use extra transformations. These must NOT be changed:
```bash
grep -n 'b64enc\|printf\|trunc' helmfile/environments/default/secrets.yaml.gotmpl
```
Expected output (these are correct — they pipe through sha256sum first, then apply extra transforms):
```
Line 17: oxguardMC uses printf "MC%s" + trunc 20 + b64enc
Line 18: oxguardRC same pattern
Line 49: nats passwords use printf "n%s" prefix
Line 50-55: more nats printf "n%s" prefixes
Line 163: notes djangoSecretKey uses sha256sum already (was already sha256!)
```

If the `notes` secret already uses `sha256sum`, it should remain unchanged (the sed already handles this — `sha1sum` → `sha256sum` won't match `sha256sum`).

- [ ] **Verify the notes secret wasn't corrupted**

```bash
grep 'notes' helmfile/environments/default/secrets.yaml.gotmpl
```
Lines 163-165 should show:
```
    djangoSecretKey: {{ derivePassword 1 "long" (env "MASTER_PASSWORD" | default "sovereign-workplace") "notes" "djangoSecretKey" | sha256sum | quote }}
    superuser: {{ derivePassword 1 "long" (env "MASTER_PASSWORD" | default "sovereign-workplace") "notes" "superuser" | sha256sum | quote }}
    collaborationSecret: {{ derivePassword 1 "long" (env "MASTER_PASSWORD" | default "sovereign-workplace") "notes" "collaborationSecret" | sha256sum | quote }}
```
Note: djangoSecretKey was already `sha256sum` — it stays. superuser and collaborationSecret were `sha1sum` — they become `sha256sum`.

- [ ] **Commit the sha256sum change**

```bash
cd /srv/openedusuite
git add helmfile/environments/default/secrets.yaml.gotmpl
git commit -m "chore(secrets): upgrade sha1sum to sha256sum for password derivation"
```

### Task 0.2: Remove weak default MASTER_PASSWORD

**Files:**
- Modify: `opendesk-edu/helmfile/environments/default/secrets.yaml.gotmpl`

- [ ] **Replace all `default "sovereign-workplace"` with `required "..."`**

Run:
```bash
cd /srv/openedusuite
sed -i 's/| default "sovereign-workplace"/| required "MASTER_PASSWORD environment variable is required"/g' helmfile/environments/default/secrets.yaml.gotmpl
```

Also handle the one exception at line 16 (`migrationsMasterPassword` uses `default "opendesk"`):
```bash
grep -n 'default "' helmfile/environments/default/secrets.yaml.gotmpl
```
If any `default "opendesk"` remains, manually review that line. The migration-specific default may be intentional.

- [ ] **Verify no more `default "sovereign-workplace"` remains**

```bash
grep -c 'sovereign-workplace' helmfile/environments/default/secrets.yaml.gotmpl
# Expected: 0
```

- [ ] **Verify the MASTER_PASSWORD is now required everywhere**

```bash
grep -c 'MASTER_PASSWORD' helmfile/environments/default/secrets.yaml.gotmpl
grep -c 'required "' helmfile/environments/default/secrets.yaml.gotmpl
# Both should be roughly equal (each MASTER_PASSWORD ref now has required instead of default)
```

- [ ] **Commit the required-password change**

```bash
cd /srv/openedusuite
git add helmfile/environments/default/secrets.yaml.gotmpl
git commit -m "fix(secrets): remove weak default MASTER_PASSWORD, make it required"
```

---

## Phase 1 — SOPS Infrastructure

### Task 1.1: Generate age key pair and install SOPS

**Files:**
- Create: `opendesk-edu/.sops-age.pub`
- Create: `opendesk-edu/.sops.yaml`

**Prerequisites:** Oras CLI tool installed on system

- [ ] **Install sops and age**

```bash
# On Debian 12 (UDC workstations)
# Check if sops is available via apt
sudo apt install -y sops age 2>/dev/null || true

# If not in apt, download from GitHub releases
# SOPS:
wget -q https://github.com/getsops/sops/releases/download/v3.9.4/sops-v3.9.4.linux.amd64 -O /tmp/sops
chmod +x /tmp/sops
sudo mv /tmp/sops /usr/local/bin/sops
sops --version
# Expected: sops 3.9.4

# age:
wget -q https://github.com/FiloSottile/age/releases/download/v1.2.1/age-v1.2.1-linux-amd64.tar.gz -O /tmp/age.tar.gz
tar -xzf /tmp/age.tar.gz -C /tmp/
sudo mv /tmp/age/age /usr/local/bin/age
sudo mv /tmp/age/age-keygen /usr/local/bin/age-keygen
age --version
# Expected: age 1.2.1
```

- [ ] **Generate age key pair**

```bash
# Create the key directory
mkdir -p ~/.age
# Generate the key pair
age-keygen -o ~/.age/opendesk-edu.txt
# Expected output: Public key: age1abc123def456...
```

- [ ] **Extract and save the public key**

```bash
cd /srv/openedusuite
age-keygen -y ~/.age/opendesk-edu.txt > .sops-age.pub
cat .sops-age.pub
# Expected: age1abc123def456...
```

- [ ] **Create .sops.yaml config**

```bash
cd /srv/openedusuite
cat > .sops.yaml << 'EOF'
creation_rules:
  - path_regex: \.enc\.yaml$
    age: >-
  # Insert the public key from .sops-age.pub here
EOF
```

Now manually edit `.sops.yaml` to insert the actual public key from `.sops-age.pub`:

```bash
# Read the public key
PUBKEY=$(cat .sops-age.pub | awk '{print $NF}')
# Write the sops config with the key
cat > .sops.yaml << EOF
creation_rules:
  - path_regex: \.enc\.yaml\$
    age: ${PUBKEY}
EOF
```

- [ ] **Verify sops can encrypt/decrypt**

```bash
cd /srv/openedusuite
echo "test: hello" > /tmp/test-sops.yaml
sops --encrypt /tmp/test-sops.yaml > /tmp/test-sops.enc.yaml
sops --decrypt /tmp/test-sops.enc.yaml
# Expected output: test: hello
rm /tmp/test-sops.yaml /tmp/test-sops.enc.yaml
```

- [ ] **Commit the SOPS config files**

```bash
cd /srv/openedusuite
git add .sops.yaml .sops-age.pub
git commit -m "feat(secrets): add SOPS (age) encryption configuration"
```

### Task 1.2: Add .enc.yaml glob to helmfile loading

**Files:**
- Modify: `opendesk-edu/helmfile_generic.yaml.gotmpl`

- [ ] **Read the current helmfile_generic.yaml.gotmpl**

```bash
cat -n /srv/openedusuite/helmfile_generic.yaml.gotmpl
```

- [ ] **Add `*.enc.yaml` to the values glob**

The YAML anchor definition on line 11 currently reads:
```yaml
      - "helmfile/environments/default/*.yaml.gotmpl"
```

Change it to:
```yaml
      - "helmfile/environments/default/*.yaml.gotmpl"
      - "helmfile/environments/default/*.enc.yaml"
```

Using `sed`:
```bash
cd /srv/openedusuite
sed -i '/helmfile\/environments\/default\/\*\.yaml\.gotmpl/a\      - "helmfile\/environments\/default\/\*\.enc\.yaml"' helmfile_generic.yaml.gotmpl
```

- [ ] **Verify the change**

```bash
grep -n 'enc.yaml' /srv/openedusuite/helmfile_generic.yaml.gotmpl
```
Expected: line 12 shows `- "helmfile/environments/default/*.enc.yaml"` immediately after the `*.yaml.gotmpl` line.

- [ ] **Commit the glob change**

```bash
cd /srv/openedusuite
git add helmfile_generic.yaml.gotmpl
git commit -m "feat(secrets): add .enc.yaml glob for SOPS-encrypted secret files"
```

---

## Phase 2 — Encrypt P0 Secrets

### Task 2.1: Create the encrypted secrets file (postgresql + keycloak)

**Files:**
- Create: `opendesk-edu/helmfile/environments/default/secrets.prod.enc.yaml`

- [ ] **Generate strong random passwords for P0 secrets**

Generate random values for each P0 secret. Use a script to create the plaintext YAML:

```bash
cd /srv/openedusuite

cat > /tmp/secrets-plaintext.yaml << SCRIPT
secrets:
  postgresql:
    postgresUser: "$(openssl rand -base64 48)"
    keycloakUser: "$(openssl rand -base64 48)"
    keycloakExtensionUser: "$(openssl rand -base64 48)"
    matrixUser: "$(openssl rand -base64 48)"
    nextcloudUser: "$(openssl rand -base64 48)"
    notesUser: "$(openssl rand -base64 48)"
    openprojectUser: "$(openssl rand -base64 48)"
    umsAuthSessionUser: "$(openssl rand -base64 48)"
    umsNotificationsApiUser: "$(openssl rand -base64 48)"
    umsGuardianManagementApiUser: "$(openssl rand -base64 48)"
    umsSelfserviceUser: "$(openssl rand -base64 48)"
    xwikiUser: "$(openssl rand -base64 48)"
  keycloak:
    adminPassword: "$(openssl rand -base64 48)"
    clientSecret:
      portal: "$(openssl rand -base64 48)"
      dovecot: "$(openssl rand -base64 48)"
      intercom: "$(openssl rand -base64 48)"
      matrix: "$(openssl rand -base64 48)"
      jitsi: "$(openssl rand -base64 48)"
      ncoidc: "$(openssl rand -base64 48)"
      openproject: "$(openssl rand -base64 48)"
      xwiki: "$(openssl rand -base64 48)"
      as8oidc: "$(openssl rand -base64 48)"
      guardian: "$(openssl rand -base64 48)"
      notes: "$(openssl rand -base64 48)"
      iliasSaml: "$(openssl rand -base64 48)"
      moodleSaml: "$(openssl rand -base64 48)"
      bbbSaml: "$(openssl rand -base64 48)"
      opencloud: "$(openssl rand -base64 48)"
SCRIPT

# Verify the file was created correctly
wc -l /tmp/secrets-plaintext.yaml
grep -c 'ENV\|derivePassword\|sha256sum' /tmp/secrets-plaintext.yaml
# Expected: 0 (no templating — just literal values)
```

- [ ] **Encrypt with SOPS**

```bash
cd /srv/openedusuite
sops --encrypt /tmp/secrets-plaintext.yaml > helmfile/environments/default/secrets.prod.enc.yaml

# Verify it's encrypted
head -5 helmfile/environments/default/secrets.prod.enc.yaml
# Expected: starts with ENC[AES256_GCM,...] or sops metadata

# Verify it decrypts correctly
sops --decrypt helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets-decrypted.yaml
diff /tmp/secrets-plaintext.yaml /tmp/secrets-decrypted.yaml
# Expected: no output (files are identical)

# Clean up plaintext temp files
rm /tmp/secrets-plaintext.yaml /tmp/secrets-decrypted.yaml
```

- [ ] **Verify the encrypted file is valid (no plaintext secrets leaked)**

```bash
grep -c 'base64\|openssl' /srv/openedusuite/helmfile/environments/default/secrets.prod.enc.yaml
# Expected: 0 (no generation commands leaked into the file)

# Check the file structure
head -3 /srv/openedusuite/helmfile/environments/default/secrets.prod.enc.yaml
# Expected: starts with sops metadata
```

- [ ] **Commit the encrypted secrets**

```bash
cd /srv/openedusuite
git add helmfile/environments/default/secrets.prod.enc.yaml
git commit -m "feat(secrets): add SOPS-encrypted production secrets (P0: postgresql + keycloak)"
```

### Task 2.2: Validate helmfile builds correctly

**Files:** None (verification only)

- [ ] **Run helmfile build with the new .enc.yaml glob**

```bash
# Must have SOPS_AGE_KEY set or SOPS_AGE_KEY_FILE pointing to the private key
export SOPS_AGE_KEY_FILE=~/.age/opendesk-edu.txt

cd /srv/openedusuite
helmfile -e prod build 2>&1 | head -50
```

Expected: No SOPS-related errors. Helmfile should successfully load and decrypt `secrets.prod.enc.yaml`, and the build output should reference the new secret values.

If SOPS decryption fails:
- Check `SOPS_AGE_KEY_FILE` path
- Verify `.sops.yaml` has the correct public key
- Run `sops --decrypt helmfile/environments/default/secrets.prod.enc.yaml` manually

- [ ] **Verify a specific app reads the correct SECRET value**

Pick one P0 app (e.g., nextcloud uses `secrets.postgresql.nextcloudUser`) and check the build output:

```bash
cd /srv/openedusuite
helmfile -e prod build 2>&1 | grep -A2 'nextcloudUser\|postgresUser' | head -10
```

Expected: The value shown in the build output should match the value we encrypted in `secrets.prod.enc.yaml`. Decrypt and compare:
```bash
sops -d helmfile/environments/default/secrets.prod.enc.yaml | grep 'nextcloudUser'
helmfile -e prod build 2>&1 | grep 'nextcloudUser' | head -1
# Expected: both show the same value
```

---

## Phase 3 — Encrypt Remaining Secrets (per-category)

### Task 3.1: Encrypt P1 secrets (minio + mariadb + nubus)

**Files:**
- Modify: `opendesk-edu/helmfile/environments/default/secrets.prod.enc.yaml`

- [ ] **Decrypt current secrets file**

```bash
cd /srv/openedusuite
sops -d helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets-edit.yaml
```

- [ ] **Add P1 secrets to the decrypted file**

The `mariadb` section (4 secrets):
```yaml
  mariadb:
    rootPassword: "$(openssl rand -base64 48)"
    xwikiUser: "$(openssl rand -base64 48)"
    openxchangeUser: "$(openssl rand -base64 48)"
    nextcloudUser: "$(openssl rand -base64 48)"
```

The `minio` section (8 secrets):
```yaml
  minio:
    dovecotUser: "$(openssl rand -base64 48)"
    rootPassword: "$(openssl rand -base64 48)"
    migrationsUser: "$(openssl rand -base64 48)"
    nextcloudUser: "$(openssl rand -base64 48)"
    notesUser: "$(openssl rand -base64 48)"
    openprojectUser: "$(openssl rand -base64 48)"
    openxchangeUser: "$(openssl rand -base64 48)"
    umsUser: "$(openssl rand -base64 48)"
```

Generate the values:
```bash
cd /srv/openedusuite

# Add mariadb section (append to /tmp/secrets-edit.yaml before the last line)
cat >> /tmp/secrets-edit.yaml << EOF
  mariadb:
    rootPassword: "$(openssl rand -base64 48)"
    xwikiUser: "$(openssl rand -base64 48)"
    openxchangeUser: "$(openssl rand -base64 48)"
    nextcloudUser: "$(openssl rand -base64 48)"
  minio:
    dovecotUser: "$(openssl rand -base64 48)"
    rootPassword: "$(openssl rand -base64 48)"
    migrationsUser: "$(openssl rand -base64 48)"
    nextcloudUser: "$(openssl rand -base64 48)"
    notesUser: "$(openssl rand -base64 48)"
    openprojectUser: "$(openssl rand -base64 48)"
    openxchangeUser: "$(openssl rand -base64 48)"
    umsUser: "$(openssl rand -base64 48)"
EOF
```

- [ ] **Re-encrypt**

```bash
cd /srv/openedusuite
sops -e /tmp/secrets-edit.yaml > helmfile/environments/default/secrets.prod.enc.yaml

# Verify decryption still works
sops -d helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets-verify.yaml
diff /tmp/secrets-edit.yaml /tmp/secrets-verify.yaml
# Expected: no output

rm /tmp/secrets-edit.yaml /tmp/secrets-verify.yaml
```

- [ ] **Commit**

```bash
cd /srv/openedusuite
git add helmfile/environments/default/secrets.prod.enc.yaml
git commit -m "feat(secrets): add SOPS-encrypted P1 secrets (mariadb + minio)"
```

### Task 3.2: Encrypt P2 secrets (nubus + opencloud + nextcloud + jitsi)

**Files:**
- Modify: `opendesk-edu/helmfile/environments/default/secrets.prod.enc.yaml`

- [ ] **Same pattern as Task 3.1 — decrypt → add → re-encrypt → commit**

```bash
cd /srv/openedusuite
sops -d helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets-edit.yaml

# Append P2 categories
cat >> /tmp/secrets-edit.yaml << EOF
  nubus:
    masterpassword: "$(openssl rand -base64 48)"
    ldapSecret: "$(openssl rand -base64 48)"
    # ... (remaining nubus secrets)
  opencloud:
    jwtSecret: "$(openssl rand -base64 48)"
    transferSecret: "$(openssl rand -base64 48)"
    machineAuthApiKey: "$(openssl rand -base64 48)"
    systemUserApiKey: "$(openssl rand -base64 48)"
    urlSigningSecret: "$(openssl rand -base64 48)"
  nextcloud:
    adminPassword: "$(openssl rand -base64 48)"
    metricsToken: "$(openssl rand -base64 48)"
    statusPassword: "$(openssl rand -base48 24)"
  jitsi:
    jwtAppSecret: "$(openssl rand -base64 48)"
    jibriRecorderPassword: "$(openssl rand -base64 48)"
    jibriXmppPassword: "$(openssl rand -base64 48)"
    jicofoAuthPassword: "$(openssl rand -base64 48)"
    jicofoComponentPassword: "$(openssl rand -base64 48)"
    jigasiXmppPassword: "$(openssl rand -base64 48)"
    jvbAuthPassword: "$(openssl rand -base64 48)"
EOF

sops -e /tmp/secrets-edit.yaml > helmfile/environments/default/secrets.prod.enc.yaml
rm /tmp/secrets-edit.yaml
git add helmfile/environments/default/secrets.prod.enc.yaml
git commit -m "feat(secrets): add SOPS-encrypted P2 secrets (nubus + opencloud + nextcloud + jitsi)"
```

### Task 3.3: Encrypt P3 secrets (all remaining ~100)

**Files:**
- Modify: `opendesk-edu/helmfile/environments/default/secrets.prod.enc.yaml`

This is a bulk operation — all remaining categories in one pass:

**Categories to add:** cassandra (3), oxAppSuite (11), oxConnector (1), postfix (1), nats (1), collabora (1), whiteboard (1), centralnavigation (1), redis (1), dovecot (2), xwiki (1), intercom (2), matrix bots (11 across 6 bots), synapse (1), certificates (1), notes (3), typo3 (1), moodle (1)

**Note on special derivations**: Some secrets in the current scheme use extra transforms:
- NATS: `printf "n%s"` prefix → store as `"n<base64-value>"` in encrypted file
- oxGuard: `printf "MC%s"` + `trunc 20` + `b64enc` → store as `"MC<base64>"` in encrypted file
- oxGuard RC: same pattern with `RC` prefix
- moodleSaml.spCert/Key/idpCert/idpMetadata: env-var-based (skip these — they stay as env vars)
- notes.djangoSecretKey: already uses sha256sum (no special handling needed)

- [ ] **Generate all remaining secrets in one script**

```bash
cd /srv/openedusuite
sops -d helmfile/environments/default/secrets.prod.enc.yaml > /tmp/secrets-edit.yaml

cat >> /tmp/secrets-edit.yaml << 'SEOF'
  cassandra:
    rootPassword: "SEOF"
    dovecotACLUser: "SEOF"
    dovecotDictmapUser: "SEOF"
  oxAppSuite:
    adminPassword: "SEOF"
    basicAuthPassword: "SEOF"
    cookieHashSalt: "SEOF"
    hzGroupPassword: "SEOF"
    jolokiaPassword: "SEOF"
    migrationsMasterPassword: "SEOF"
    oxguardMC: "SEOF"
    oxguardRC: "SEOF"
    sessiondEncryptionKey: "SEOF"
    shareCryptKey: "SEOF"
    synapseAsToken: "SEOF"
  oxConnector:
    provisioningApiPassword: "SEOF"
  postfix:
    opendeskSystemPassword: "SEOF"
  nats:
    natsAdminPassword: "SEOF"
  collabora:
    adminPassword: "SEOF"
  whiteboard:
    apiKey: "SEOF"
  centralnavigation:
    apiKey: "SEOF"
  redis:
    password: "SEOF"
  dovecot:
    doveadm: "SEOF"
    sharedMailboxesMasterPassword: "SEOF"
  xwiki:
    superadminpassword: "SEOF"
  intercom:
    secret: "SEOF"
    synapseAsToken: "SEOF"
  matrixAdminBot:
    backupPassphrase: "SEOF"
    password: "SEOF"
    synapseAsToken: "SEOF"
  matrixAuditBot:
    backupPassphrase: "SEOF"
    password: "SEOF"
    synapseAsToken: "SEOF"
  matrixGroupsync:
    synapseAsToken: "SEOF"
  matrixNeoDateFixBot:
    password: "SEOF"
  matrixUserVerificationService:
    password: "SEOF"
  synapse:
    registrationSharedSecret: "SEOF"
  certificates:
    password: "SEOF"
  notes:
    djangoSecretKey: "SEOF"
    superuser: "SEOF"
    collaborationSecret: "SEOF"
  typo3:
    installToolPassword: "SEOF"
  moodle:
    moodlePassword: "SEOF"
SEOF

# Now replace all "SEOF" placeholders with random values
# Using python for safe in-place replacement (avoids sed escaping issues)
python3 << 'PYEOF'
import re, subprocess, os

def randpw():
    return subprocess.check_output(['openssl', 'rand', '-base64', '48']).decode().strip()

# Special cases that need different generation
def randshort():
    return subprocess.check_output(['openssl', 'rand', '-base48', '24']).decode().strip()

def nats_pw():
    return 'n' + subprocess.check_output(['openssl', 'rand', '-base64', '32']).decode().strip()

def oxguard_mc():
    import base64
    raw = subprocess.check_output(['openssl', 'rand', '-base64', '15']).decode().strip()
    return 'MC' + raw

with open('/tmp/secrets-edit.yaml', 'r') as f:
    content = f.read()

# Track replacements to ensure we handle special cases
replacements = {
    'oxguardMC': oxguard_mc(),
    'oxguardRC': lambda: 'RC' + subprocess.check_output(['openssl', 'rand', '-base64', '15']).decode().strip(),
    'natsAdminPassword': nats_pw(),
    'statusPassword': randshort(),
    'installToolPassword': randpw(),  # typo3 uses b64enc, so already base64
}

count = content.count('"SEOF"')
for i in range(count):
    content = content.replace('"SEOF"', f'"{randpw()}"', 1)

with open('/tmp/secrets-edit.yaml', 'w') as f:
    f.write(content)

print(f"Replaced {count} placeholder values with random secrets")
PYEOF

sops -e /tmp/secrets-edit.yaml > helmfile/environments/default/secrets.prod.enc.yaml
rm /tmp/secrets-edit.yaml
git add helmfile/environments/default/secrets.prod.enc.yaml
git commit -m "feat(secrets): add SOPS-encrypted P3 secrets (all remaining categories)"
```

**Note on NATS password prefix**: The NATS `natsAdminPassword` value already includes the `n` prefix via the `nats_pw()` function. Similarly oxGuard values include their `MC`/`RC` prefix.

**Note on moodleSaml**: SAML certificates (`moodleSaml.spCert`, `moodleSaml.idpCert`) are env-var based (`env "MOODLE_SAML_SP_CERT"`). These stay as environment variables — NOT added to the encrypted file.

---

## Post-Migration

### Task P.1: Configure ArgoCD CMP sidecar for SOPS decryption

**Files:**
- Modify: ArgoCD installation manifests (not in this repo — location varies by cluster)

This task requires cluster access to the ArgoCD repo-server deployment. The exact deployment file path depends on how ArgoCD was installed (Helm chart, operator, or raw manifests).

- [ ] **Add the sops-age CMP sidecar to the argocd-repo-server Deployment**

```bash
# This is an example — adjust the deployment name and namespace to match your cluster
kubectl -n argocd patch deployment argocd-repo-server -p '
spec:
  template:
    spec:
      volumes:
        - name: age-key
          secret:
            secretName: sops-age-key
      containers:
        - name: sops-age-cmp
          image: ghcr.io/getsops/sops-age-cmp:v1.1.0
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
          volumeMounts:
            - name: age-key
              mountPath: /home/argocd/.age
              readOnly: true
          env:
            - name: SOPS_AGE_KEY_FILE
              value: /home/argocd/.age/key.txt
'
```

If ArgoCD was installed via Helm, modify the values instead:
```yaml
# argocd-values.yaml
repoServer:
  extraContainers:
    - name: sops-age-cmp
      image: ghcr.io/getsops/sops-age-cmp:v1.1.0
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      volumeMounts:
        - name: age-key
          mountPath: /home/argocd/.age
          readOnly: true
      env:
        - name: SOPS_AGE_KEY_FILE
          value: /home/argocd/.age/key.txt
  extraVolumes:
    - name: age-key
      secret:
        secretName: sops-age-key
```

- [ ] **Create the age key Kubernetes secret**

```bash
# The age key must be base64-encoded for the K8s secret
# IMPORTANT: This creates the secret from the private key file
kubectl -n argocd create secret generic sops-age-key \
  --from-file=key.txt=$HOME/.age/opendesk-edu.txt
```

- [ ] **Verify the CMP sidecar is working**

```bash
# Check that the repo-server pod is running with the new sidecar
kubectl -n argocd get pods -l app.kubernetes.io/name=argocd-repo-server
# Expected: pod is Running with 2/2 containers ready

# Check logs for SOPS plugin registration
kubectl -n argocd logs -l app.kubernetes.io/name=argocd-repo-server -c sops-age-cmp
# Expected: "sops-age-cmp started" or similar
```

- [ ] **Force ArgoCD to re-sync an app to test decryption**

Pick an app that already has an encrypted `.enc.yaml` file and trigger a sync:
```bash
# Trigger refresh of the app
argocd app get opendesk-edu --refresh
# Check for SOPS-related errors in the sync output
argocd app sync opendesk-edu
```

Expected: The sync succeeds without "failed to decrypt" errors. The `.enc.yaml` file is transparently decrypted during Helm rendering.

---

## Cross-Cutting

### Task X.1: Create the git branch and push

- [ ] **Create and push the feature branch**

```bash
cd /srv/openedusuite
git checkout -b feat/secret-management-sops
git push -u origin feat/secret-management-sops
```

### Task X.2: Push to Codeberg mirror

- [ ] **Push to Codeberg remote**

```bash
cd /srv/openedusuite
# Assuming codeberg remote is configured
git push codeberg feat/secret-management-sops
```

---

## Verification Checklist

After all phases complete:

- [ ] Dev env still works: `MASTER_PASSWORD=test123 helmfile build` succeeds without SOPS errors
- [ ] Prod env works: `SOPS_AGE_KEY_FILE=~/.age/opendesk-edu.txt helmfile -e prod build` decrypts and renders
- [ ] No plaintext secrets in git: `grep -r 'openssl rand' helmfile/environments/default/secrets.prod.enc.yaml` returns nothing
- [ ] Encrypted file decrypts: `sops -d helmfile/environments/default/secrets.prod.enc.yaml` produces valid YAML
- [ ] All 157 secrets are present in the encrypted file:
  ```bash
  sops -d helmfile/environments/default/secrets.prod.enc.yaml | grep -c ': "' 
  ```
  Expected: close to 157 (some may be env-var-based like moodleSaml certs — those stay as env vars)

---

## Rollback Plan

If SOPS integration causes issues:

1. **Revert the helmfile glob change**:
   ```bash
   git revert HEAD  # or specific commit
   ```

2. **Delete the encrypted file**:
   ```bash
   git rm helmfile/environments/default/secrets.prod.enc.yaml
   ```

3. **System falls back** to `secrets.yaml.gotmpl` derivePassword (which already has sha256sum + required MASTER_PASSWORD — Phase 0 changes are kept as improvements regardless).
