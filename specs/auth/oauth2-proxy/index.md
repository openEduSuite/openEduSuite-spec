<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# oauth2-proxy (OIDC SSO Gateway Pattern)

## Purpose

Standard reusable SSO gateway for suite applications that cannot do OIDC
natively: oauth2-proxy terminates the user's session, authenticates against
Keycloak via OIDC, and injects a per-application session cookie that only
that application's backend accepts. Used per application (currently ~26
instances: dify, discourse, drawio, ewoks, excalidraw, hedgedoc, home,
indico, invoicing, kitodo, lms, operaton, overleaf, rt, typst, ...), each
with its own secret, cookie name and upstream.

### Position: native OIDC vs. gateway

- Applications with native OIDC (Nextcloud, OpenCloud, OpenProject, SOGo6,
  n8n/dify via their own bridges) do NOT get an oauth2-proxy instance.
- Applications without native suite SSO get one `oauth2-proxy-<app>`
  deployment in front of their ingress backend.

## Non-Goals

- Replacing native OIDC where the application supports it natively
- Providing authorization/authorization policy (that remains per-application
  and in Keycloak client roles) — the proxy only establishes identity

## Requirements

### Requirement: Keycloak as the OIDC provider

Every oauth2-proxy instance SHALL use the central Keycloak realm as its
`--provider=oidc` issuer; no non-Keycloak provider is configured.

#### Scenario: Login through the proxy

- GIVEN a user opening a protected app route without a valid cookie
- WHEN oauth2-proxy runs with `--skip-provider-button=true` (single
  provider)
- THEN the user is redirected to Keycloak and back
- AND a secure session cookie is issued for that app's `--cookie-name`

### Requirement: Per-application isolation

Each instance SHALL use a distinct `--cookie-name` (e.g. `_oauth2_proxy_dify`),
app-specific OIDC client credentials and an explicit `--upstream`.

#### Scenario: Cookie names never collide

- GIVEN two proxied apps on the same cluster domain
- WHEN both issue session cookies
- THEN the cookie names are distinct (no cross-application session bleed)

### Requirement: Cookie security posture

Cookies SHALL be `secure`, `httponly`, `SameSite=lax`, with bounded
lifetime and active refresh: `--cookie-expire=18h`,
`--cookie-refresh=2m`.

#### Scenario: Session refresh

- WHEN a session approaches `cookie-refresh` expiry
- THEN oauth2-proxy exchanges the refresh token to keep the session alive
- AND absolute `cookie-expire` still bounds the overall lifetime

### Requirement: Pinned gateway image

All instances SHALL run the pinned `oauth2-proxy:v7.15.4` image via the
local registry mirror; `latest` is never used.

#### Scenario: Image provenance

- WHEN any `oauth2-proxy-*` deployment is inspected
- THEN the image is the pinned mirrored tag
- AND OIDC client id/secret come from the per-app `oauth2-proxy-<app>-secrets`
  secret, never from values/ConfigMaps

## Service Registry

| Instance | Upstream | Cookie name |
|----------|----------|-------------|
| oauth2-proxy-dify | `dify-nginx:80` | `_oauth2_proxy_dify` |
| oauth2-proxy-indico | indico web | `_oauth2_proxy_indico` |
| oauth2-proxy-invoicing | invoiceninja nginx | `_oauth2_proxy_invoicing` |
| oauth2-proxy-overleaf | overleaf `:80` | `_oauth2_proxy_overleaf` |
| oauth2-proxy-{discourse,drawio,ewoks,excalidraw,hedgedoc,home,kitodo,lms,operaton,rt,typst,...} | per-app upstream | `_oauth2_proxy_<app>` |

## Depends On

- Keycloak (OIDC IdP)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC issuer)
- All proxied applications (SSO gateway)
- Portal/Nubus (single sign-on across the route egress of all proxied apps)

## SLO

**Tier**: Critical (authentication boundary for ~26 apps)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.9% | Uptime over 30-day window |
| **Auth latency (P95)** | <500 ms | proxy logs |
| **Error Rate** | <0.5% 5xx | ingress/proxy logs |
