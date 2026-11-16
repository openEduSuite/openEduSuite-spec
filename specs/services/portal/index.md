# Portal (Home Dashboard)

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

## Purpose

Suite home portal/dashboard that renders the application tile grid as the
primary landing page for authenticated users. Backed by the
`openedusuite-nix/collab-dashboard:main` image. This is the user-facing
entry point after SSO authentication.

## Scope

- ✅ **In scope**: collab-dashboard deployment, tile grid rendering,
  ingress `ingress-home-portal`, oauth2-proxy SSO gateway
  (`oauth2-proxy-home`), ConfigMap `configmap-portal` with tile list,
  canonical domain `cloud.openedusuite.org`
- ❌ **Out of scope**: IAM provisioning (covered by Nubus spec),
  tile registry configuration (Nubus handles canonical app signals),
  individual application routing beyond the tile click

## Non-Goals

- Managing the canonical app tile registry (Nubus spec owns this)
- Keycloak realm or client configuration (Nubus handles this)
- User provisioning or identity management (Nubus handles this)
- Custom theming beyond what collab-dashboard supports

## Requirements

### Requirement: Render application tile dashboard

The portal SHALL render a grid of clickable application tiles for all
applications the authenticated user is authorized to access.

#### Scenario: User sees authorized application tiles

- GIVEN a user authenticated via oauth2-proxy-home (Keycloak OIDC)
- WHEN the user accesses `https://cloud.openedusuite.org`
- THEN collab-dashboard renders the tile grid
- AND tiles for authorized applications appear
- AND tiles for unauthorized applications do NOT appear

#### Scenario: Tile list driven by ConfigMap

- GIVEN ConfigMap `configmap-portal` contains tile definitions
- WHEN collab-dashboard starts
- THEN it reads the tile list from `configmap-portal`
- AND renders tiles based on that configuration

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

The portal SHALL be reachable only through the oauth2-proxy gateway
(`oauth2-proxy-home`) using Keycloak OIDC as the identity provider.

#### Scenario: User authenticates via SSO

- GIVEN an unauthenticated user opening `https://cloud.openedusuite.org`
- WHEN the request reaches oauth2-proxy-home
- THEN the user is redirected to Keycloak OIDC login
- AND upon successful authentication, the user sees the portal dashboard

### Requirement: Ingress routing on cloud.openedusuite.org

The portal SHALL be served at the canonical domain
`https://cloud.openedusuite.org` via `ingress-home-portal`.

#### Scenario: Canonical domain routing

- GIVEN a request to `https://cloud.openedusuite.org`
- WHEN the request reaches HAProxy Ingress
- THEN it is routed to oauth2-proxy-home → collab-dashboard
- AND the user sees the portal dashboard

### Requirement: Image provenance

Portal SHALL run from `openedusuite-nix/collab-dashboard:main`. Note
that `:latest` only updates on v*-tags via workflow; `:main` updates on
every main push. Recommend pinning to a commit tag as a hardening
follow-up.

#### Scenario: Image reference and pinning follow-up

- WHEN the deployment manifest is inspected
- THEN the image is `openedusuite-nix/collab-dashboard:main`
- AND a follow-up task exists to pin the tag to a specific commit

### Requirement: Relation to Nubus

The Nubus spec (`specs/services/nubus/index.md`) covers IAM and
portal-structure provisioning via UMS. The portal service here is the
user-facing tile dashboard served by collab-dashboard. Nubus provides the
canonical app signal (tile registry) and identity; portal renders the home
dashboard using those signals.

#### Scenario: Nubus provides tile registry

- GIVEN Nubus maintains the canonical application tile registry
- WHEN collab-dashboard starts
- THEN it consumes the tile list (via ConfigMap `configmap-portal`)
- AND Nubus ensures the tile registry is up to date

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| collab-dashboard | Application tile dashboard UI | 1+ | None |
| oauth2-proxy-home | OIDC SSO gateway (Keycloak) | 1 | None |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| collab-dashboard | non-root (distro default) | drop: ALL | RuntimeDefault |
| oauth2-proxy-home | non-root | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `openedusuite-nix/collab-dashboard:main` (pin to commit tag recommended) |
| Ingress | `ingress-home-portal` at `cloud.openedusuite.org` |
| SSO | oauth2-proxy-home with Keycloak OIDC |
| ConfigMap | `configmap-portal` (tile list) |
| Container port | 80 (or as configured in collab-dashboard) |

## Depends On

- Keycloak (OIDC via oauth2-proxy-home, provided by Nubus)
- HAProxy Ingress
- Nubus (IAM, portal-structure provisioning, tile registry signals)
- cloud-alias-redirect (legacy hostnames redirect to cloud.openedusuite.org via HTTP 301)

## Integrates With

- Nubus (IAM, Keycloak OIDC, portal tile registry via UMS)
- All suite applications (via tileclick navigation; each app handles its
  own OIDC/SAML SSO through Keycloak clients defined in Nubus)
- oauth2-proxy-home (SSO gateway for the portal itself)

## SLO

**Tier**: Standard (user-facing entry point, critical user experience)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <200 ms | Ingress access logs (dashboard render time) |
| **Error Rate** | <0.5% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Standard (stateless; config via ConfigMap, RPO: ≤1 h, RTO: 15 min)

- **Configuration**: GitOps-managed manifests + ConfigMap
  `configmap-portal`
- **State**: None; collab-dashboard is stateless (user session handled
  by oauth2-proxy + Keycloak)
- **Recovery order**: redeploy from GitOps → verify SSO via oauth2-proxy
  → verify tile list from ConfigMap → smoke test dashboard render
- **Follow-up**: pin collab-dashboard image to a specific commit tag for
  reproducible deployments
