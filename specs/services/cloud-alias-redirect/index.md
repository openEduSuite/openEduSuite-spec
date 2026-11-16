# cloud-alias-redirect (Legacy Alias 301 Redirector)

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

## Purpose

Pure HTTP-to-HTTPS legacy aliases redirector so any bare or inherited
`cloud.*` hostnames land on the canonical OpenCloud domain
`https://cloud.openedusuite.org`. It is a stateless internal utility with
zero persistent state and no user interaction.

## Scope

- ✅ **In scope**: Deployment `cloud-alias-redirect`, ConfigMap
  `cloud-alias-nginx` with single redirect rule, stateless operation,
  horizontal scaling (replicas: 1 by default)
- ❌ **Out of scope**: TLS termination (handled at ingress), canonical
  OpenCloud application routing, DNS configuration for `cloud.*` aliases

## Non-Goals

- TLS/HTTPS support (HTTP only; relies on external TLS termination)
- Path-based or conditional redirects (single catch-all 301)
- Logging or analytics for redirect traffic
- Custom per-tenant redirect mappings

## Requirements

### Requirement: nginx returns 301 to canonical OpenCloud domain

The nginx instance SHALL listen on port 80 and return HTTP 301 redirecting
all requests to `https://cloud.openedusuite.org$request_uri`.

#### Scenario: legacy cloud.* hostname is redirected

- GIVEN a user or bot opens `http://cloud.<legacy-domain>/some/path`
- WHEN the request reaches the `cloud-alias-redirect` service
- THEN nginx returns HTTP 301 with Location header
  `https://cloud.openedusuite.org/some/path`
- AND the client follows the redirect to the canonical domain

#### Scenario: bare hostname is redirected

- GIVEN a request to `http://cloud-alias-redirect/` (bare server_name)
- WHEN the request is processed by nginx
- THEN it returns HTTP 301 to `https://cloud.openedusuite.org/`
- AND preserves any query string parameters via `$request_uri`

### Requirement: Stateless operation

The service SHALL have zero persistent state; all configuration SHALL be
baked into the ConfigMap and container image.

#### Scenario: pod recreation does not lose configuration

- GIVEN the `cloud-alias-redirect` deployment is recreated
- WHEN nginx starts on a new pod
- THEN it reads `default.conf` from ConfigMap `cloud-alias-nginx`
- AND immediately serves redirects without requiring initialization

### Requirement: single replica by default

The deployment SHALL run with replicas: 1 as it is stateless and
horizontal scaling is trivial but not required for the redirect traffic.

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| nginx | HTTP server with 301 redirect rule | 1 | None |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| nginx | non-root (nginx user) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | nginx (alpine-based, from upstream) |
| ConfigMap | `cloud-alias-nginx` |
| Config file | `default.conf` |
| nginx listen port | 80 |
| nginx server_name | `_` (catch-all) |
| nginx redirect rule | `return 301 https://cloud.openedusuite.org$request_uri;` |
| Deployment labels | `app: cloud-alias-redirect` |

## Depends On

HAProxy Ingress (for external HTTP routing to this service)

## Integrates With

- Ingress (directly, as an HTTP endpoint for legacy `cloud.*` routes)
- collab-dashboard / portal (indirectly, by directing users to the canonical
  cloud.openedusuite.org entry point which is backed by the portal
  pipeline)
- Nubus (indirectly, as Nubus provides IAM and portal-structure; the portal
  service renders the user-facing tile dashboard)

## SLO

**Tier**: Low (stateless internal utility)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.0% | Uptime over 30-day window |
| **Latency (P95)** | <10 ms | Ingress access logs (redirect response time) |
| **Error Rate** | <0.1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Low (stateless; RPO: 0, RTO: 1 min)

- **Configuration**: ConfigMap `cloud-alias-nginx` is GitOps-managed;
  redeploy from manifests restores full functionality
- **State**: None; service is stateless
- **Recovery order**: redeploy from GitOps → verify redirect via curl →
  re-attach ingress route if needed
