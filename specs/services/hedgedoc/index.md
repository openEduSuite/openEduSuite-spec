<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# HedgeDoc (Collaborative Markdown)

## Purpose

Collaborative Markdown note-taking/editing for the suite (shared meeting
notes, docs, drafts) with live collaborative editing. Authenticated via the
central Keycloak IdP through the standard oauth2-proxy gateway pattern.

## Scope

- ✅ **In scope**: HedgeDoc deployment (pinned upstream image), SQLite
  persistence, oauth2-proxy SSO (Keycloak OIDC), HTTPS-only routing
- ❌ **Out of scope**: replacing Nextcloud documents or Overleaf (TeX)

## Non-Goals

- Replacing Nextcloud file collaboration or Overleaf TeX editing
- Real-time team chat (that is Element/Matrix)

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

HedgeDoc SHALL be reachable only through the per-app oauth2-proxy
(`oauth2-proxy-hedgedoc`, provider `oidc`, Keycloak).

#### Scenario: User reaches HedgeDoc via SSO

- GIVEN a user opening `hedgedoc.<cluster-domain>`
- WHEN the oauth2-proxy has no valid session cookie
- THEN the user is authenticated via Keycloak OIDC
- AND the resulting session cookie grants access to the notes

### Requirement: Persistence

Notes SHALL persist via the SQLite database on the note PVC
(`CMD_DB_STORAGE=/data/hedgedoc.db`); the session secret SHALL be stable
across restarts.

#### Scenario: Notes survive restart

- WHEN a hedgedoc pod is recreated
- THEN notes persist via SQLite on `pvc-hedgedoc`
- AND sessions stay valid via `CMD_SESSION_SECRET`

### Requirement: HTTPS-only routing

The instance SHALL be served TLS-terminated at the configured domain.

#### Scenario: Domain and TLS

- WHEN the deployment is inspected
- THEN `CMD_DOMAIN=hedgedoc.<cluster-domain>` and
  `CMD_PROTOCOL_USESSL=true`
- AND `CMD_PORT=3000` matches the served container port

### Requirement: Pinned image

HedgeDoc SHALL run from a pinned upstream tag (`hedgedoc/hedgedoc:1.9.9`);
`latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is the pinned upstream tag via the local mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| hedgedoc | collaborative markdown editor (`:3000`) | 1 | `pvc-hedgedoc` (SQLite) |
| oauth2-proxy | OIDC SSO gateway | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| hedgedoc | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `hedgedoc/hedgedoc:1.9.9` (mirrored, pinned) |
| Route | `hedgedoc.<cluster-domain>` → oauth2-proxy → `:3000` |
| Storage | SQLite at `/data/hedgedoc.db` on `pvc-hedgedoc` |
| Domain | `CMD_DOMAIN`, `CMD_PROTOCOL_USESSL=true` |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-hedgedoc`)
- Portal (tile entry)
- (optional) document/discourse linking

## SLO

**Tier**: Low (stateless-leaning, SSO-gated)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Low (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + env vars
- **User data**: `pvc-hedgedoc` (SQLite) via the existing backup regime
- **Recovery order**: restore SQLite PVC → redeploy from GitOps → verify SSO
  via oauth2-proxy
