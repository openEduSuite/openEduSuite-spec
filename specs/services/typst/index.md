<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Typst (Document Rendering)

## Purpose

On-demand compilation of Typst markup to PDF/svg for the suite's document
workflows. The `typst-render` microservice (the `tobias-weiss-ai-xr` fork of
typst-render) exposes an HTTP endpoint that renders submitted Typst source to
PDF or svg, complementing the PKU Toss office-compatibility stack. The service
is stateless and SSO-gated through the standard oauth2-proxy + Keycloak OIDC
pattern.

## Scope

- ✅ **In scope**: `typst-render` deployment (pinned fork image via local
  mirror), HTTP render API on container port `8080`, oauth2-proxy SSO
  (Keycloak OIDC), HTTPS-only routing at `typst.<cluster-domain>`
- ❌ **Out of scope**: persistent document storage, collaborative editing,
  interactive Typst IDE features

## Non-Goals

- Storing or versioning user documents (the service is stateless)
- Replacing Overleaf (LaTeX/TeX editing) or Nextcloud document collaboration
- Acting as a general file-conversion gateway beyond Typst → PDF/svg

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

The render API SHALL be reachable only through the per-app oauth2-proxy
(`oauth2-proxy-typst`, provider `oidc`, Keycloak).

#### Scenario: User reaches Typst render API via SSO

- GIVEN a user opening `typst.<cluster-domain>`
- WHEN the oauth2-proxy has no valid session cookie
- THEN the user is authenticated via Keycloak OIDC
- AND the resulting session cookie grants access to the render endpoint

### Requirement: Stateless rendering

The service SHALL keep no user data between requests; rendering is performed
on demand from submitted Typst source.

#### Scenario: Stateless compile

- WHEN a Typst source document is submitted for rendering
- THEN the service compiles it to PDF/svg on container port `8080`
- AND no document content is persisted after the response is returned

### Requirement: HTTPS-only routing

The instance SHALL be served TLS-terminated at the configured domain.

#### Scenario: Domain and TLS

- WHEN the deployment is inspected
- THEN the ingress route is `typst.<cluster-domain>`
- AND TLS is terminated at the HAProxy ingress before oauth2-proxy

### Requirement: Pinned image

Typst SHALL run from a pinned tag of the fork image; `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is `172.25.24.36:5001/tobias-weiss-ai-xr/typst-render:0.15.1-3`
- AND the manifest notes the canonical upstream
  `ghcr.io/tobias-weiss-ai-xr/typst-render:0.15.1-2` (the local Zot mirror is
  currently stale at `0.15.1-3`)

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| typst-render | Typst → PDF/svg render API (`:8080`) | 1 | — (stateless) |
| oauth2-proxy | OIDC SSO gateway | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| typst-render | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/tobias-weiss-ai-xr/typst-render:0.15.1-3` (mirrored, pinned) |
| Route | `typst.<cluster-domain>` → oauth2-proxy → `:8080` |
| Container port | `8080` |
| Upstream | `ghcr.io/tobias-weiss-ai-xr/typst-render:0.15.1-2` (local mirror stale at `0.15.1-3`) |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-typst`)
- Portal (tile entry)
- Suite document workflows (Typst → PDF/svg rendering, complements PKU Toss
  office compatibility)

## SLO

**Tier**: Low (stateless, SSO-gated)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Compile Latency (P95)** | <3 s | Ingress access logs / render API timings |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Low (RPO: 0, RTO: 1 h)

- **Configuration**: GitOps-managed manifests + env vars
- **User data**: none (stateless service holds no user data)
- **Recovery order**: redeploy from GitOps → verify SSO via oauth2-proxy →
  confirm a sample render request returns a PDF
