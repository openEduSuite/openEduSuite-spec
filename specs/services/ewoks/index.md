# Ewoks (Scientific Workflows)

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

## Purpose

Graph-based scientific workflow orchestration web client (`ewoksweb`) for
the suite. Ewoks is part of the CEA/ESRF ecosystem and provides a browser UI
to design, schedule and monitor Python workflow graphs. Authenticated via
the central Keycloak IdP through the standard oauth2-proxy gateway pattern.

## Scope

- ✅ **In scope**: Ewoks web client deployment, oauth2-proxy SSO (Keycloak
  OIDC), HTTPS-only routing, persistent volume for workflow artifacts
- ❌ **Out of scope**: the PBS/queue execution backend (referenced
  conceptually only — the spec is limited to what the manifests support:
  web client + SSO + PVC storage)

## Non-Goals

- Owning or configuring the PBS/queue execution layer beyond what the web
  client surfaces
- Replacing general-purpose pipeline tools (Airflow, etc.)
- Multi-replica horizontal scaling of the workflow UI

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Ewoks SHALL be reachable only through the per-app oauth2-proxy
(`oauth2-proxy-ewoks`, provider `oidc`, Keycloak).

#### Scenario: User reaches Ewoks via SSO

- GIVEN a user opening `ewoks.<cluster-domain>`
- WHEN the oauth2-proxy has no valid session cookie
- THEN the user is authenticated via Keycloak OIDC
- AND the resulting session cookie grants access to the workflow UI

### Requirement: Persistence

Workflow artifacts/state SHALL persist on the dedicated PVC
(`pvc-ewoksweb`) so user work survives pod recreation.

#### Scenario: Workflows survive restart

- WHEN an ewoksweb pod is recreated
- THEN workflow artifacts persist on `pvc-ewoksweb`
- AND the user can resume their workflow graphs

### Requirement: HTTPS-only routing

The instance SHALL be served TLS-terminated at the configured domain.

#### Scenario: Domain and TLS

- WHEN the deployment is inspected
- THEN `ewoks.<cluster-domain>` routes through oauth2-proxy to the
  ewoksweb container on port `8000`
- AND traffic is TLS-terminated at ingress

### Requirement: Image provenance

Ewoks SHALL run from the local registry image
`172.25.24.36:5001/openedusuite/ewoksweb:latest`. The manifest literally
tags `:latest`; this SHOULD be moved to a pinned digest/tag as a
hardening follow-up.

#### Scenario: Image provenance and pinning follow-up

- WHEN the deployment manifest is inspected
- THEN the image is `172.25.24.36:5001/openedusuite/ewoksweb:latest`
- AND a follow-up task exists to pin the tag off `latest`

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| ewoksweb | graph-based scientific workflow UI (`:8000`) | 1 | `pvc-ewoksweb` |
| oauth2-proxy | OIDC SSO gateway | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| ewoksweb | non-root (distro default) | drop: ALL | RuntimeDefault |
| oauth2-proxy | non-root | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/openedusuite/ewoksweb:latest` (local mirror; pin off `latest`) |
| Route | `ewoks.<cluster-domain>` → oauth2-proxy → `:8000` |
| Container port | `8000` |
| Storage | `pvc-ewoksweb` for workflow artifacts/state |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-ewoks`)
- Portal (tile entry)
- (conceptually) PBS/queue execution backends surfaced through the web
  client

## SLO

**Tier**: Low-Medium (SSO-gated workflow UI)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Low-Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + env vars
- **User data**: `pvc-ewoksweb` via the existing backup regime
- **Recovery order**: restore `pvc-ewoksweb` → redeploy from GitOps →
  verify SSO via oauth2-proxy
- **Follow-up**: move the ewoksweb image off the `:latest` tag onto a
  pinned digest/tag to guarantee reproducible redeployments
