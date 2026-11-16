<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Indico (Event Management)

## Purpose

Event management platform for conferences, workshops and lecture-series
administration: event scheduling, abstract submission/review, registration,
and participant management. Authenticated via the central Keycloak IdP
through the standard oauth2-proxy gateway pattern.

## Scope

- ✅ **In scope**: Indico deployment (web + Celery workers), dedicated
  PostgreSQL and Redis backends, oauth2-proxy SSO (Keycloak OIDC), file
  attachments persistence, Nginx termination
- ❌ **Out of scope**: multi-tenant SaaS hosting, replacing the suite's
  calendar/booking surfaces (SOGo, BBB)

## Non-Goals

- Hosting third-party event platforms
- Replacing SOGo calendar or BBB booking flows

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Indico SHALL be reachable only through the per-app oauth2-proxy instance
(`oauth2-proxy-indico`, provider `oidc`, Keycloak), with no local login for
regular users.

#### Scenario: User reaches Indico via SSO

- GIVEN a user opening `indico.<cluster-domain>`
- WHEN the oauth2-proxy finds no valid `_oauth2_proxy_indico` cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to Indico

### Requirement: Persistence

Indico SHALL persist events, registrations and attachments in the dedicated
PostgreSQL database (`indico-db`, postgres 17.x) and PVC; Redis SHALL serve
as the Celery cache/queue backend.

#### Scenario: Data survives restart

- WHEN an indico web/worker pod is recreated
- THEN event data, registrations and abstract reviews persist via the
  `indico-db` PostgreSQL + `pvc-indico`
- AND queued tasks survive via the Celery/Redis backend

#### Scenario: Large uploads accommodated

- GIVEN a file/abstract attachment upload
- THEN the `MAX_CONTENT_LENGTH` limit (`32768` MB) allows conference-scale
  file attachments
- AND the Nginx sidecar terminates TLS/`USE_PROXY` paths

### Requirement: Background jobs via Celery

Asynchronous work (registration emails, export jobs, reminder tasks) SHALL
run on dedicated Celery workers with a beat scheduler.

#### Scenario: Worker topology

- GIVEN regular and periodic Indico jobs
- THEN `indico-celery` consumes the task queue
- AND `indico-celery-beat` schedules recurring jobs

### Requirement: Pinned images

Indico SHALL run from pinned mirrored images (`getindico/indico:3.3.14`,
postgres 17.11, nginx 1.30); `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN all component images are pinned tags via the local registry mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| indico-web | Indico (3.3.14) + Nginx sidecar | 1 | `pvc-indico` |
| indico-celery | async task workers | 1 | — |
| indico-celery-beat | periodic scheduler | 1 | — |
| indico-db | dedicated PostgreSQL (17.11) | 1 | data PVC |
| indico-redis | cache + Celery broker | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| indico web/workers | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `getindico/indico:3.3.14` (mirrored, pinned) |
| Route | `indico.<cluster-domain>` → oauth2-proxy → web |
| Base URL | `https://indico.openedusuite.org` (`USE_PROXY=true`) |
| Timezone | `Europe/Berlin` |
| Uploads | `MAX_CONTENT_LENGTH` = 32768 MB |
| Stores | PostgreSQL (`indico-db`), Redis (`indico-redis`) |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- PostgreSQL (`indico-db`)
- Redis (`indico-redis`)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-indico`)
- Calendar/booking flows (separate surfaces; Indico is event-lifecycle
  management)
- Portal (tile entry)

## SLO

**Tier**: Medium (stateful, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `indico-config` ConfigMap
- **User data**: `indico-db` PostgreSQL + `pvc-indico` backups via the
  existing backup regime
- **Recovery order**: restore DB + attachments → redeploy from GitOps →
  verify SSO via oauth2-proxy
