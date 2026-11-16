<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# n8n (Workflow Automation)

## Purpose

Workflow automation / integration platform ("system glue") used for
cross-service automation, webhooks and asynchronous operations the engine
(Operaton) deliberately does not cover. Authenticated exclusively through the
central Keycloak IdP via the **n8n SSO Bridge** — a small Node reverse proxy
that adds OIDC SSO to the unmodified n8n Community Edition (which has no
native OIDC support outside of the paid plan).

## Scope

- ✅ **In scope**: n8n deployment (pinned community image), OIDC SSO via the
  n8n SSO Bridge (Keycloak + session injection through the n8n REST API),
  owner bootstrap via the `n8n-sso` secret, workflow data persistence,
  consumer of lifecycle automation from the Operaton external-task worker
- ❌ **Out of scope**: n8n paid/cloud features (SSO requires the bridge, not
  licensing), replacing Operaton for audited business processes (Operaton =
  BPMN with human tasks; n8n = glue/webhooks)

## Non-Goals

- Acting as the audited BPM engine (that is Operaton's role)
- Multi-tenant hosting for third parties
- Native OIDC in n8n itself (community edition lacks it — the bridge provides it)

## Requirements

### Requirement: SSO via n8n SSO Bridge (Keycloak OIDC)

Users SHALL reach n8n only through the SSO bridge, which authenticates via
Keycloak OIDC and injects an n8n session cookie. Each OIDC identity SHALL map
to a deterministic n8n account (no local signup prompts).

#### Scenario: User logs in via the bridge

- GIVEN a user opening the n8n route without a valid `n8n-auth` cookie
- WHEN the bridge gate redirects to `/sso/login` and Keycloak authenticates
- THEN the bridge provisions the n8n user for the OIDC identity
- AND logs that user in via `POST /rest/login` with a derived password
- AND hands the resulting `n8n-auth` session cookie to the browser

#### Scenario: Deterministic per-user password

- GIVEN an OIDC `sub` + `email` and the `N8N_SSO_USER_PASSWORD_SECRET`
- WHEN a user logs in for the first time
- THEN `deriveUserPassword` returns
  `base64url(HMAC-SHA256(secret, sub|email))[0:14] + "A1"`
- AND the same password is derived on every later login (no credential store)
- AND a `401` at login triggers an owner-API password-reset-link fallback
  (e.g. after the secret changed or a user was created manually)

#### Scenario: Existing user activation

- GIVEN a user already invited/pending in n8n
- WHEN the bridge provisions the account
- THEN it skips the re-invite (no "invite already accepted" error)
- AND activates via `/rest/invitations/accept` (or a password-reset flow for
  already-active accounts)

### Requirement: Gateway control

The bridge gate SHALL pass only authenticated traffic (plus its own `/sso/`
endpoints), SHALL block WebSocket upgrades without a valid session, and SHALL
allow an optional bypass CIDR for local/testing fallback.

#### Scenario: WebSocket upgrade gate

- GIVEN a client holding an `n8n-auth` cookie
- WHEN a WebSocket upgrade request arrives
- THEN the upgrade is proxied to n8n
- AND upgrades without the cookie are destroyed

### Requirement: Pinned community image

n8n SHALL run from a pinned `n8n:<version>-n8nio` image tag via the local
registry mirror; `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is a pinned mirrored tag (e.g. `n8n:2.45.7-n8nio`)
- AND credentials come from the `n8n-sso` secret (owner + OIDC client), never
  from values files

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| n8n (community) | workflow engine, REST `:5678` | 1 | `n8n-data` PVC (persistent workflow store) |
| n8n SSO Bridge | OIDC reverse proxy `:8080` → `127.0.0.1:5678`, session injection, user provisioning | 1 | none |
| `n8n-direct` service | internal port for service-to-service callers (e.g. Operaton lifecycle worker) | — | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| n8n worker | non-root (distro default) | drop: ALL | RuntimeDefault |
| SSO Bridge (node:22-alpine) | non-root | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `n8n:<pinned>-n8nio` (mirrored locally) |
| Ports | n8n `5678`; bridge `8080` (public route) |
| OIDC | Keycloak realm client via `n8n-sso` secret (issuer, client id/secret, owner) |
| Session | derived per-user password, `N8N_SSO_USER_PASSWORD_SECRET` |
| Bypass | `N8N_SSO_BYPASS_IP` (empty/CIDR; `0.0.0.0/0` = gate disabled for testing) |

## Depends On

- Keycloak (OIDC IdP)
- PostgreSQL / local store behind `n8n-data` (workflow persistence)
- HAProxy Ingress (route to the bridge)

## Integrates With

- Keycloak (OIDC SSO via the bridge)
- Operaton (lifecycle external-task worker invokes n8n via its internal
  REST/JWT endpoints for user-provisioning automation)
- Intercom / async integration services (n8n as webhook/automation backbone)

## SLO

**Tier**: Medium (automation backbone, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms (REST) | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + bridge code in ConfigMap
  (`bridge.js`) — a bridge code change is picked up by `kubectl rollout
  restart deploy/n8n-bridge-app`-style restart
- **User data**: `n8n-data` PVC backup via the existing k8up/backup regime
- **Recovery order**: restore workflow store → redeploy from GitOps → SSO
  verify via bridge health `/sso/health`
