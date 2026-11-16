# SPDX-FileCopyrightText: 2026 openEduSuite Contributors
# SPDX-License-Identifier: Apache-2.0

# Toss (Typst Office Suite)

## Purpose

Document composition and conversion service in the Typst ecosystem for the
openEduSuite, complementing the typst-render PDF rendering pipeline. Toss
provides office-suite compatibility (document conversion, formatting) via a
centralized HTTP API. Access is restricted to authenticated users via SSO.

## Scope

- ✅ **In scope**: Toss core server deployment, oauth2-proxy SSO (Keycloak
  OIDC), ingress routing, configuration via ConfigMap + Secrets
- ❌ **Out of scope**: typst-render service (separate component), end-user
  document editing UIs, multi-tenant document hosting

## Non-Goals

- Replacing typst-render PDF rendering pipeline
- Providing end-user document editing interfaces
- Hosting persistent user documents or state

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Toss SHALL be reachable only through the per-app oauth2-proxy instance
(`oauth2-proxy-toss`, provider `oidc`, Keycloak), with no local login for
regular users.

#### Scenario: User reaches Toss via SSO

- GIVEN a user opening `toss.<cluster-domain>`
- WHEN the oauth2-proxy finds no valid `_oauth2_proxy_toss` cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to Toss

### Requirement: HTTP service on port 8080

The Toss core container SHALL expose its HTTP API on container port 8080.

#### Scenario: Service connectivity

- GIVEN a running Toss pod
- WHEN an internal request is made to port 8080
- THEN the Toss API responds with HTTP 200 for valid endpoints

### Requirement: Pinned container image

Toss SHALL run from the pinned mirrored image
`172.25.24.36:5001/pku-typst/toss-core:2026-04-27`; `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the Toss container uses the pinned date-tagged image from the local
  registry mirror

### Requirement: Configuration via ConfigMap and Secrets

Toss SHALL be configured via the `toss-config` ConfigMap and `toss-secrets`
Secret; no configuration values are hardcoded in manifests.

#### Scenario: Configuration loading

- GIVEN a Toss pod start
- WHEN the pod mounts its configuration
- THEN settings are loaded from `toss-config` ConfigMap and `toss-secrets`
  Secret
- AND no secret values appear in deployment manifests

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| toss-core | Toss document/office compatibility server (Typst ecosystem) | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| toss-core | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/pku-typst/toss-core:2026-04-27` (mirrored, pinned) |
| Route | `toss.<cluster-domain>` → oauth2-proxy → toss-core:8080 |
| ConfigMap | `toss-config` |
| Secrets | `toss-secrets` |

## Depends On

- Keycloak (OIDC via oauth2-proxy-toss)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-toss`)
- typst-render (complementary PDF rendering service in Typst ecosystem)
- Portal (tile entry)

## SLO

**Tier**: Low-to-Medium (stateless, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Low-to-Medium (RPO: near-zero, RTO: <1 h)

- **Configuration**: GitOps-managed manifests + `toss-config` ConfigMap +
  `toss-secrets` Secret
- **Recovery order**: redeploy from GitOps → verify SSO via oauth2-proxy-toss
