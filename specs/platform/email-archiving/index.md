<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Email Archiving (Exchange Verwaltung)

## Purpose

Defines the archiving capability for the suite's long-tail mailboxes: the
Verwaltung (administration) operates Microsoft Exchange with **shared
mailboxes and public folders**, the largest mailboxes exceeding 500 GB. An
open-source, sovereign archive SHALL capture, retain, and make searchable
the full Exchange message flow (including shared-mailbox and public-folder
content), decouple compliance retention from live mailbox growth, and feed
the existing cold-storage/backup regime.

## Current Situation

- **Verwaltung**: Microsoft Exchange (**on-prem**, confirmed 2026-11-17); heavy
  reliance on shared mailboxes and public folders; single mailboxes up to
  500+ GB — primary mail store growth is the driver for archiving.
- **Faculty & students**: Dovecot/Postfix (spec `../services/dovecot-postfix`)
  — not the archival pain point; unaffected by this capability.
- **Suite mail**: Stalwart (`../services/stalwart`) with SOGo6 as webmail
  (`../services/sogo`) — the suite's own SMTP/IMAP/JMAP stack; not the
  Exchange archive target (kept as future consolidation context only).
- No archive solution exists today; retention today = do nothing (live store
  grows unbounded).

## Scope

- ✅ **In scope**: complete capture of Verwaltung Exchange traffic (in/out/
  internal, incl. mail-enabled public folders), shared-mailbox + public-
  folder backfill of existing long-tail (500+ GB) stores, retention
  classes (*Aufbewahrungsfristen*), legal hold, tamper-evidence + audit log,
  full-text search, eDiscovery export, SSO (Keycloak/LDAP), cold-tier
  storage, backup/DR integration
- ❌ **Out of scope**: replacing Exchange itself (migration is a separate
  effort), archiving Dovecot faculty/student mailboxes, fighting spam/
  phishing, preserving contacts/calendars as structured records (email only)

## Non-Goals

- Real-time mailbox migration tooling for Exchange
- Replacing the university records/registry system (interface instead:
  preservation-grade transfers, see Decision)
- Archiving instant-messaging/admin-chat platforms

## Requirements

### Requirement: Complete flow capture (journaling)

The archive SHALL capture every message transiting the Verwaltung Exchange
— inbound, outbound and internal — including messages posted to mail-enabled
public folders, independent of what users later delete from their mailboxes.
On-prem Exchange journaling (standard/premium journal rule → archive SMTP
target) is the capture mechanism.

#### Scenario: Deleted mail is still archived

- GIVEN Exchange journaling is configured to forward a copy of all traffic
  to the archive
- WHEN a message is delivered and a user deletes it from the live mailbox
- THEN the archive retains an intact copy with original envelope headers
- AND the deletion has no effect on the archived copy

### Requirement: Shared-mailbox and public-folder coverage

The archive SHALL include the content of shared mailboxes and of the public
folder tree, since the Verwaltung depends on both for its daily workflow.

#### Scenario: Shared content reaches the archive

- GIVEN a message is posted to a shared mailbox or a public folder
- WHEN the archive ingests it (journal copy and/or structured export)
- THEN the message is searchable with its original recipient/folder context
- AND access to the archived copy is scoped by the addresses involved

### Requirement: Backfill of existing long-tail stores (500+ GB)

The archive SHALL ingest the pre-existing contents of large shared
mailboxes and public folders (hundreds of GB per store) via on-prem
`New-MailboxExportRequest` (MRS → PST, folder-split for stores >50 GB)
followed by `readpst` → mbox bulk import, without requiring user
interaction.

#### Scenario: Historical backfill

- GIVEN an existing shared mailbox or public-folder tree larger than any
  single ingest can process
- WHEN an administrator triggers an export+import
- THEN the content lands in the archive with folder structure preserved
- AND old messages become searchable alongside new ones

### Requirement: Retention classes

The archive SHALL enforce configurable retention classes (per folder,
per domain, per administrative category) aligned with German
*Aufbewahrungsfristen*; expired items SHALL be purged, but never while a
legal hold applies.

#### Scenario: Retention expiry

- GIVEN a retention class with a defined retention period
- WHEN an archived message exceeds that period
- THEN the message is purged from the archive
- AND messages under legal hold are exempted from purging

### Requirement: Legal hold

The archive SHALL place legal holds on individual messages, mailboxes or
whole domains; a held item SHALL survive any retention expiry and any
administrative purge until the hold is lifted.

#### Scenario: Hold overrides retention

- GIVEN a legal hold is active for a mailbox
- WHEN that mailbox's retention period expires
- THEN the messages remain fully searchable and intact
- AND the hold status is recorded in the audit log

### Requirement: Tamper-evidence and audit trail

The archive SHALL cryptographically fingerprint archived messages (digest
and signature verification where available) and SHALL keep an append-only
audit log of archive access, searches and exports.

#### Scenario: Integrity can be proven

- GIVEN an archived message
- WHEN its integrity is verified
- THEN the stored digest matches the message
- AND search/export/access events are present in the audit log

### Requirement: Full-text search

The archive SHALL provide full-text search over headers, body and
attachments with simple and expert (field/facet) query support and
sub-second response on the archived corpus.

#### Scenario: Finding an old message

- GIVEN a user with access
- WHEN they search for text or a header criterion that occurs in an
  archived message
- THEN the message is returned with surrounding metadata
- AND attachments are included in the index

### Requirement: eDiscovery export

The archive SHALL allow authorized auditors to search the complete corpus
(including other users' mail) and export result sets in open formats (EML/
MBOX); regular users SHALL only see messages in which their own addresses
appear.

#### Scenario: Auditor export

- GIVEN an auditor account with the audit/legal role
- WHEN the auditor runs a search and exports the result
- THEN a complete, tamper-verifiable export is produced
- AND regular users' searches never expose other users' messages

### Requirement: SSO and access control

The archive SHALL authenticate via the suite identity layer (Keycloak OIDC
or LDAP) and SHALL derive per-user visibility from the addresses found in
the messages; administrators/auditors SHALL have explicit roles.

#### Scenario: SSO login and scoping

- GIVEN a user authenticated against Keycloak or LDAP
- WHEN they open the archive
- THEN they can only search their own message set
- AND admins and auditors authenticate the same way with elevated roles

### Requirement: Durable cold tier and backup integration

The archive SHALL store message blobs on cheap object/cold storage (S3-compatible/MinIO) and SHALL be integrated into the existing k8up→restic→S3
backup and mirror regime (including the institutional mirror), with a DR
restore path that does not lose archived content.

#### Scenario: Cold storage and restore

- GIVEN archived content on the cold/object tier
- WHEN the archive is restored after a disaster
- THEN metadata, index and blobs are restored consistently
- AND a restore drill confirms searches and exports work again

## Evaluation (2026-11 research)

| Option | License | Exchange feeding | Public folders | Assessment |
|--------|---------|------------------|----------------|------------|
| **Piler** (`jsuto/piler` v1.4.9) | GPLv3 | SMTP journaling target + bulk import (EML/MBOX/Maildir/IMAP) | via journaling + PST→mbox backfill | **Chosen core**: retention, legal hold, SHA-256 dedup, AES-256, tamper fingerprinting + audit log, Manticore FTS, LDAP/SSO. OSS edition = single server, filesystem blob store (S3 is enterprise-only — acceptable, PVC tier). |
| **Open Archiver** | AGPLv3 (young, v0.x) | M365/Google/IMAP/PST; on-prem Exchange journaling = open feature request | no (Graph gap) | Modern (Meilisearch, S3), but public-folder-blind and rapidly changing. |
| **Mail-Archiver** (`s1t5`) | GPLv3 | IMAP + M365 Graph + OAuth; deletion lock | no (Graph gap) | Simple (Postgres/Docker), polling-based — misses messages deleted between syncs; no tamper story. |
| **MailArchiva (OSS)** | GPL (open core) | journaling/IMAP | partial | Free tier capped at 9 mailboxes — irrelevant at suite scale. |
| **Stalwart multi-store/S3** | AGPLv3 | n/a (suite mail server) | n/a | Not an archive. Future cold-tier option if Verwaltung ever consolidates onto the suite. |
| **Archivematica** | AGPL/GPL OAIS | PST→mbox (readpst), Maildir; PREMIS/METS AIPs | via PST/EWS export | **Preservation tier** for records-grade transfers (HArchG), not the daily search tool. |

### Decision (2026-11-17, on-prem confirmed)

- **Two-layer approach**: Piler as the access/compliance archive (journaling
  capture + backfill + retention/legal-hold/search/export), Archivematica as
  the preservation tier for official-records transfers.
- **Verwaltung runs ON-PREM Exchange** (confirmed) → the full-fidelity feed
  path is available and remains viable long-term:
  - Ongoing capture: on-prem Exchange journaling rule (standard or premium)
    → journal mailbox / direct SMTP forward → archive SMTP target (Piler
    journaling). Captures inbound/outbound/internal traffic incl. messages
    posted to mail-enabled public folders.
  - Backfill (shared mailboxes AND public-folder mailboxes): on-prem-only
    `New-MailboxExportRequest` (MRS → PST) — for stores >50 GB split into
    multiple requests via `-IncludeFolders`/`-ExcludeFolders`/`-ContentFilter`;
    public-folder mailbox exported as `-Mailbox "<PF mailbox>"`, hierarchy
    preserved as PST folder tree. PST → `readpst` (libpst) → mbox → bulk
    import; on-prem EWS export scripts remain an alternative since EWS is
    NOT retired for on-prem.
- **Public-folder risk only re-materializes on future EXO migration**: the
  2026/2027 EWS retirement applies to Exchange Online only. If Verwaltung
  later migrates, archive-export public folders during the on-prem window
  and plan migration of live public folders to shared mailboxes (which all
  open-source paths can reach).

## Component Reference (planned)

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| piler | archive daemon/web UI (SMTP capture, rules, search) | 1 | blob store (cold tier) |
| piler-smtp | built-in SMTP journaling target | 1 | — |
| manticore | full-text search index | 1 | index PVC |
| mariadb | archive metadata, retention/legal-hold state, audit log | 1 | RWO PVC |
| readpst/libpst | PST→mbox conversion for backfill | job | — |
| archivematica | OAIS preservation transfers (official records) | 1+ | AIP store (cold tier) |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| archive components | non-root | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Ingest | on-prem Exchange journaling (SMTP) + bulk import (PST via `readpst` → mbox/EML) |
| Search | Manticore full-text index |
| Auth | Keycloak OIDC or LDAP (suite identity) |
| Retention | per-folder/per-domain classes (*Aufbewahrungsfristen*) + legal hold |
| Storage | archive blobs on cold/object tier; metadata+index on PVC |
| Backup | k8up → restic → S3 (+ institutional mirror) |

## Deployment Sketch (planned)

Target: UDC K3s cluster, `openedusuite` namespace, following suite
conventions (HAProxy ingress, cert-manager, oauth2-proxy gateway,
k8up→restic→S3 backup, local registry mirrors, Kyverno-compliant
`securityContext`: `runAsNonRoot`, `drop: [ALL]`,
`allowPrivilegeEscalation: false`, seccomp `RuntimeDefault` — aligned with
`../platform/security` so no PolicyException is required).

### Components

| Component | Image source | Role |
|-----------|--------------|------|
| mariadb | suite MariaDB image (mirror) | archive metadata, retention/legal-hold state, audit log |
| manticore | manticore image (mirror) | RT full-text index (headers/body/attachments) |
| piler-web | jsuto/piler distro (mirror; php-fpm + nginx sidecar) | web UI, search, export, admin |
| piler-smtp | jsuto/piler (mirror) | built-in SMTP journaling target |
| piler-worker | jsuto/piler (mirror) | message parse/store, rules, index feed |
| piler-import | jsuto/piler tools + `readpst` (libpst) | batch backfill (PST → mbox → import) |
| oauth2-proxy-archive | suite oauth2-proxy image | AuthN front (Keycloak OIDC) |

### Topology

```text
[on-prem Exchange Verwaltung]
   ├─ journaling rule → archive SMTP addr (port 25, source-IP restricted)
   │      └─→ HAProxy ingress → piler-smtp:2525 → queue → worker
   │              → blobs (cold PVC) + metadata (MariaDB) + index (Manticore)
   └─ New-MailboxExportRequest (PST, MRS, folder-split >50 GB)
          └─→ PST share → piler-import job (readpst → mbox → import)

[Users/auditors] → Keycloak OIDC → oauth2-proxy-archive
      └─→ piler-web (nginx/php-fpm) → MariaDB + Manticore
```

### Networking & identity

- **FQDN**: `archive.openedusuite.org` (HAProxy ingress, ssl-redirect,
  cert-manager TLS).
- **SMTP feed**: journaling from on-prem Exchange lands on the cluster SMTP
  entry point (`:25`), **source-IP restricted** to the Exchange servers and
  the suite MTAs (journaling must never be an open relay); internally
  forwarded to `piler-smtp:2525`. Alternative: pre-relay via the suite
  Postfix/Stalwart relay to keep port 25 off the archive Service directly.
- **AuthN**: suite oauth2-proxy pattern (`--skip-provider-button=true`,
  per-app cookie `_oauth2_proxy_archive`, provider `oidc` → Keycloak),
  passing the authenticated mail address (e.g. `X-Auth-Request-Email`)
  into piler's header/REMOTE_USER SSO seam.
- **AuthZ stays inside piler**: address-scoped visibility for regular users
  (own From/To/Cc), auditor role view-all mapped from an LDAP group
  (ums-ldap bind). Fallback if the header-SSO seam is unavailable: piler
  native LDAP/IMAP authentication.

### Storage map + sizing

| Mount | PVC / backend | Backend | Initial size |
|-------|---------------|---------|--------------|
| piler blobs (compressed + AES-256 message/attachment store) | RWO PVC, cold/cheaper storage class | corpus × ~0.6 (dedup+compression) + 30 % headroom ⇒ ≈1.5–2 TB for a 2 TB corpus |
| manticore index | RWO PVC (fast disk) | ~10–15 % of indexable corpus |
| mariadb data | RWO PVC | 100 GB (metadata for millions of messages, re-grow on demand) |
| PST/mbox import staging | RWX temp volume | bounded per wave |

All PVCs `k8up.io/backup: "true"` → restic → S3 + institutional mirror.

### Resources (initial fleet ≈ 10 vCPU / 30 GB RAM)

| Component | CPU | RAM |
|-----------|-----|-----|
| mariadb | 2 | 4 GB |
| manticore | 4 | 8–16 GB (disk-backed RT index, cache) |
| piler-web (nginx/php-fpm) | 2 | 2 GB |
| piler-smtp + worker | 1–2 | 2 GB |

### Secrets (kubectl-applied, NOT in git — suite convention)

- `archive-mariadb`: DB_USERNAME / DB_PASSWORD / root
- `piler-key`: master AES key + IV — **backup discipline: never lose, never
  change the IV** (lost key = unreadable archive)
- `piler-ldap`: bind credentials (`ums-ldap-server-admin` pattern)
- `archive-s3`: restic/S3 credentials (or reuse suite backup secrets)

### Bring-up sequence

1. Secrets + ConfigMaps (`piler.conf`, journaling rule documentation)
2. MariaDB → 3. Manticore → 4. piler core (smtp/worker/web)
5. oauth2-proxy + ingress + TLS
6. Connect journaling: Exchange rule → archive SMTP target; start in
   dry-run / small pilot scope before going live
7. Backfill: readpst/piler-import jobs in waves (folder-split >50 GB),
   reconcile counts with Exchange export statistics
8. Validation (below) → 9. switch journaling live, enable monitoring

### Validation checklist (maps 1:1 to the 10 scenarios)

- R1: journal a test message, delete it from the mailbox → archived copy
  intact
- R2: post to a shared mailbox and a mail-enabled public folder → both
  archived with correct recipient context
- R3: import one >50 GB store → folder structure preserved, counts match
  Exchange export stats
- R4/R5: retention class expiry purges; legal hold overrides purge
- R6: fingerprint verify passes; audit log contains login/search/export
- R7: expert search on a known header, P95 < 2 s
- R8: auditor exports full result set; regular user sees only own mail
- R9: Keycloak SSO login via oauth2-proxy; roles respected
- R10: k8up run succeeds (restic list), restore drill reproduces search +
  export

### Operational notes

- **piler master key**: offsite + K8s Secret copies, included in the restore
  drill; never re-key in place.
- **Capture completeness**: daily archived-count vs Exchange SMTP message
  tracking log, alert on drift (journalling feed must never silently stop).
- Retention scheduler + legal-hold review cadence; auditor role lifecycle
  via the LDAP group.
- Manticore index health (background reindex fallback); pinned images,
  state backup before any upgrade.

## Depends On

- Identity layer (Keycloak / LDAP)
- MariaDB (`../services/mariadb`-style backend or dedicated)
- Object/cold storage (`../platform/storage`)
- k8up/restic backup + mirror (`../platform/backup`)
- Mail transport access to the Verwaltung Exchange (journaling target)

## Integrates With

- Exchange (Verwaltung, **on-prem**): journaling rule + `New-MailboxExportRequest` (MRS→PST, folder-split >50 GB) → `readpst` → archive import
- Suite identity (Keycloak OIDC)
- SOGo6/stalwart specs only as future-consolidation context
  (`../services/stalwart`, `../services/sogo`)
- Platform backup/storage/security (`../platform/backup`,
  `../platform/storage`, `../platform/security`)

## SLO

**Tier**: Standard (archive availability; no dependence by live mail flow
once journaling is queued)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Capture completeness** | 100% of journaled traffic | audit counts vs MTA logs |
| **Search latency (P95)** | <2 s | archive web UI |
| **Restore (DR)** | ≤24 h RTO, RPO near-zero | restore drill |

## Disaster Recovery

**Tier**: Standard (RPO: near-zero via journaling, RTO: ≤24 h)

- **Configuration**: GitOps-managed manifests + archive secrets
- **Data**: metadata/index PVC + cold-tier blobs via the existing backup
  regime (k8up → restic → S3 + institutional mirror)
- **Recovery order**: restore metadata + index + blobs → redeploy archive →
  verify search/export → re-establish journaling feed
