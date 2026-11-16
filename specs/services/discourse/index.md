<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Discourse (Community Forum)

## Purpose

Community forum / discussion platform for the suite ("https://discourse.<cluster-domain>",
site "openEduSuite Community") for announcements, support threads and
community Q&A. Authenticated via the central Keycloak IdP through the
standard oauth2-proxy gateway pattern; content managed by site moderators.

## Scope

- ✅ **In scope**: Discourse deployment (official pinned image), dedicated
  PostgreSQL + Redis backends, oauth2-proxy SSO (Keycloak OIDC), topic/post
  persistence
- ❌ **Out of scope**: multi-tenant public hosting, replacing the suite's
  real-time chat (Element/Matrix) or event tooling

## Non-Goals

- Replacing real-time chat (Matrix/Element) or event management (Indico)
- Public internet-scale forum hosting

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Discourse SHALL be reachable only through the per-app oauth2-proxy
(`oauth2-proxy-discourse`, provider `oidc`, Keycloak).

#### Scenario: User reaches Discourse via SSO

- GIVEN a user opening `discourse.<cluster-domain>`
- WHEN the oauth2-proxy finds no valid session cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to the forum

### Requirement: Persistence

Topics, posts and user profiles SHALL persist in the dedicated
`discourse-postgres` database (pgvector image); Redis SHALL serve sidekiq
jobs and rate limiting.

#### Scenario: Forum data survives restart

- WHEN a discourse pod is recreated
- THEN topics/posts persist via the discourse PostgreSQL database
- AND background jobs continue via the Redis/sidekiq backend

### Requirement: Site configuration contract

The deployment SHALL configure discourse via the official image's
`DISCOURSE_*` env contract (prefix stripped + lowercased → config key).

#### Scenario: Config mapping

- GIVEN `DISCOURSE_HOSTNAME=discourse.<cluster-domain>` and
  `DISCOURSE_SITE_NAME=openEduSuite Community`
- THEN the image maps them to `hostname` / `site_name` config keys
- AND the SMTP path likewise follows `DISCOURSE_SMTP_*` → `smtp_*`

### Requirement: Pinned image

Discourse SHALL run from a pinned date-stamped official tag
(`discourse/discourse:2026.11.0-latest`); floating `latest` is not used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is the pinned official date tag via the local mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| discourse | forum web app (official image, `:80`) | 1 | (DB-backed) |
| discourse-postgres | PostgreSQL (pgvector image) | 1 | data PVC |
| discourse redis | sidekiq queue / rate limiting | 1 | — |
| oauth2-proxy | OIDC SSO gateway | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| discourse web | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `discourse/discourse:2026.11.0-latest` (mirrored, pinned) |
| Route | `discourse.<cluster-domain>` → oauth2-proxy → `:80` |
| Hostname / Site | `DISCOURSE_HOSTNAME`, `DISCOURSE_SITE_NAME="openEduSuite Community"` |
| Email | `DISCOURSE_DEVELOPER_EMAILS` / `DISCOURSE_NOTIFICATION_EMAIL` |
| Stores | PostgreSQL (`discourse-postgres`), Redis |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- PostgreSQL (discourse schema)
- Redis (sidekiq)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-discourse`)
- Email (notification/developer addresses on the suite mail domain)
- Portal (tile entry)

## SLO

**Tier**: Standard (community-facing, SSO-gated)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + env contract
- **User data**: discourse PostgreSQL + Redis backups via the existing
  backup regime
- **Recovery order**: restore DB + Redis → redeploy from GitOps → verify SSO
  via oauth2-proxy
