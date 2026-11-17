<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Toss (Typst Office Suite)

## Purpose

Document composition and conversion service in the Typst ecosystem for the
openEduSuite, complementing the typst-render PDF rendering pipeline. Toss
provides office-suite compatibility (document conversion, formatting) via a
centralized HTTP API. Access is restricted to authenticated users via SSO.

## Scope

- ✅ **In scope**: Toss core server deployment, native OIDC SSO (Keycloak),
  dedicated PostgreSQL backend, ingress routing, configuration via
  ConfigMap + Secrets
- ❌ **Out of scope**: typst-render service (separate component), end-user
  document editing UIs, multi-tenant document hosting

## Non-Goals

- Replacing typst-render PDF rendering pipeline
- Providing end-user document editing interfaces
- Hosting persistent user documents or state

## Requirements

### Requirement: SSO via native OpenID Connect (Keycloak)

Toss SHALL authenticate suite identities through its own OpenID Connect
client configured against Keycloak (`OIDC_ISSUER`/`OIDC_CLIENT_ID=toss`/
`OIDC_REDIRECT_URI` in `toss-config`); no oauth2-proxy proxy is in the path
and no local password store is used for regular users.

#### Scenario: User reaches Toss via SSO

- GIVEN a user opening `toss.<cluster-domain>`
- WHEN no Toss session exists for the user
- THEN the browser is redirected to Keycloak for OIDC authentication
- AND the redirect back to the OIDC callback (`/v1/auth/oidc/callback`)
  establishes the Toss session

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
| toss-core | Toss document/office compatibility server (Typst ecosystem) | 1 | `toss-data-pvc` (RWO) |
| toss-postgres | PostgreSQL (`postgres:15.19-nix`) for suite data / assets | 1 | `toss-postgres-pvc` (RWO) |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| toss-core | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/pku-typst/toss-core:2026-04-27` (mirrored, pinned) |
| Route | `toss.<cluster-domain>` → toss-core:8080 (native OIDC, no proxy) |
| OIDC | `OIDC_ISSUER`/`OIDC_CLIENT_ID=toss`/`OIDC_REDIRECT_URI` (toss-config) |
| Database | PostgreSQL (`toss-postgres`, `postgres:15.19-nix`) |
| ConfigMap | `toss-config` |
| Secrets | `toss-secrets` |

## Depends On

- Keycloak (native OIDC)
- PostgreSQL (`toss-postgres`)
- HAProxy Ingress

## Integrates With

- Keycloak (native OIDC SSO)
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
- **Recovery order**: restore `toss-postgres` → redeploy from GitOps →
  verify native OIDC login
