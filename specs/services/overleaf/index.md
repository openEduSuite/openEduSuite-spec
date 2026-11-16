<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Overleaf (Collaborative LaTeX)

## Purpose

Collaborative LaTeX/TeX document editor for the suite (shared papers,
layouts, co-authoring with real-time compilation and rich-text preview).
Authenticated via the central Keycloak IdP through the standard
oauth2-proxy gateway pattern, with optional LDAP login support in the
deployed fork.

## Scope

- ✅ **In scope**: Overleaf deployment (server + worker, `:80`), Redis and
  MongoDB backends, oauth2-proxy SSO (Keycloak OIDC), LDAP login in the
  fork, project/backup persistence
- ❌ **Out of scope**: Overleaf Server Pro licensing topics, replacing
  document collaboration in Nextcloud (files vs. TeX source projects)

## Non-Goals

- Replacing Nextcloud documents (Overleaf is TeX-project collaboration only)
- Multi-tenant public hosting

## Requirements

### Requirement: SSO via oauth2-proxy and LDAP login

Overleaf SHALL be reachable via the per-app oauth2-proxy (`oauth2-proxy-overleaf`,
Keycloak OIDC). The deployed `overleaf:6.3.0-sso` fork additionally supports
LDAP login for non-SSO flows.

#### Scenario: User reaches Overleaf via SSO

- GIVEN a user opening `overleaf.<cluster-domain>`
- WHEN the oauth2-proxy has no valid session cookie
- THEN the user is authenticated via Keycloak OIDC
- AND the resulting cookie grants access to the editor

#### Scenario: LDAP fallback (fork)

- WHEN a user authenticates via the deployed fork's LDAP login
- THEN credentials are checked against the suite LDAP directory
  (`overleaf-ldap` secret)
- AND an existing Overleaf account is linked

### Requirement: Persistence

Overleaf SHALL persist projects, documents and compile artifacts via the
project PVC and its MongoDB backend; Redis SHALL serve caching/queueing.

#### Scenario: Project survives restart

- WHEN an overleaf server/pod is recreated
- THEN projects and history persist via `pvc-overleaf` (+ backup PVC)
- AND MongoDB + Redis state is restored from the existing backup regime

### Requirement: Pinned fork image

Overleaf SHALL run from the pinned local mirror of the SSO fork
(`overleaf:6.3.0-sso`); `latest` is never used, and the fork image is not
publicly pullable (local registry only).

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the pinned fork tag is referenced via the local registry mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| overleaf | web + compile server (fork, `:80`) | 1 | `pvc-overleaf` (+ backup) |
| overleaf-redis | caching/queue | 1 | — |
| MongoDB | project metadata/document store | 1 | data PVC |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| overleaf server | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `overleaf:6.3.0-sso` (opendesk fork, local mirror, pinned) |
| Route | `overleaf.<cluster-domain>` → oauth2-proxy → `:80` |
| SSO | oauth2-proxy OIDC + LDAP login (fork) |
| Stores | Redis, MongoDB (project data) |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- Redis
- MongoDB
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-overleaf`)
- LDAP (fork login)
- Portal (tile entry)

## SLO

**Tier**: Medium (stateful, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Compile latency (P95)** | <3 s | server logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `overleaf-config` ConfigMap
- **User data**: `pvc-overleaf` (project files + `pvc-overleaf-backup`) +
  MongoDB backups
- **Recovery order**: restore project store + MongoDB → redeploy from
  GitOps → verify SSO via oauth2-proxy
