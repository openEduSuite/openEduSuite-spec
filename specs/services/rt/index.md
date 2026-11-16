<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# RT (Request Tracker)

## Purpose

Request/ticket tracking platform for internal support and operations
workflows of the suite (incident handling, service requests, task queues).
Authenticated via the central Keycloak IdP through the standard oauth2-proxy
gateway pattern; users and groups are bootstrapped from the identity layer by
a provisioning job.

## Scope

- ✅ **In scope**: RT deployment (RT 6.0.4), oauth2-proxy SSO (Keycloak
  OIDC), MariaDB Galera backend, user/group provisioning job, periodic DB
  backup
- ❌ **Out of scope**: replacing the suite's project management (OpenProject)
  or process orchestration (Operaton); email-into-ticket plumbing beyond RT's
  own mail gateway

## Non-Goals

- Replacing OpenProject (project management) or the issue trackers of
  individual services
- Being a general CRM

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

RT SHALL be reachable only through the per-app oauth2-proxy
(`oauth2-proxy-rt`, provider `oidc`, Keycloak); no local RT passwords for
regular users.

#### Scenario: User reaches RT via SSO

- GIVEN a user opening the RT route
- WHEN the oauth2-proxy finds no valid session cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to the ticket queue

### Requirement: Identity provisioning

RT users/groups SHALL be bootstrapped from the identity layer by the
`rt-provision` job so that SSO-authenticated identities map to RT accounts.

#### Scenario: Provisioned accounts

- WHEN the provisioning job runs against the identity directory
- THEN support users and groups exist in RT matching suite identities
- AND tickets can be assigned to provisioned groups

### Requirement: Persistence

Tickets, queues and attachments SHALL persist in the MariaDB Galera cluster
(`mariadb-galera` database); the periodic `rt-db-backup` cronjob SHALL
protect the database.

#### Scenario: Tickets survive restart

- WHEN an rt pod is recreated
- THEN ticket data persists via the MariaDB Galera backend
- AND nightly/periodic DB backups continue via the backup cronjob

### Requirement: Pinned image

RT SHALL run from the pinned mirrored image
(`openedusuite-nix/rt:6.0.4-trixie`, RT 6.0.4 on Debian trixie); `latest`
is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is the pinned mirrored tag
- AND configuration is mounted read-only from the `rt-config` ConfigMap

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| rt | RT web application (`:8080`) | 1 | (DB-backed via MariaDB Galera) |
| rt-provision | user/group bootstrap job | on-demand | — |
| oauth2-proxy | OIDC SSO gateway | 1 | — |
| rt-db-backup | periodic DB backup cronjob | scheduled | backup target |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| rt web | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `openedusuite-nix/rt:6.0.4-trixie` (mirrored, pinned) |
| Route | `rt.<cluster-domain>` → oauth2-proxy → `:8080` |
| Database | MariaDB Galera (`mariadb-galera`), credentials via secrets |
| Provisioning | `rt-provision` job + `rt-lib` scripts |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- MariaDB Galera cluster (ticket store)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-rt`)
- Identity directory (user/group provisioning)
- Support operations (ticket lifecycle for suite services)

## SLO

**Tier**: Standard (internal support-critical, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `rt-config` ConfigMap
- **User data**: MariaDB Galera backup (via the rt DB-backup cronjob) under
  the existing backup regime
- **Recovery order**: restore RT database → redeploy from GitOps → run
  provisioning → verify SSO via oauth2-proxy
