<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Grist (Spreadsheet/Database)

## Purpose

Lightweight spreadsheet-and-database hybrid for the suite (small internal
tables, trackers, lists) on a per-organization ("grist") workspace, with
native OIDC SSO via the central Keycloak IdP and file uploads stored on the
suite WebDAV layer.

## Scope

- ✅ **In scope**: Grist deployment (pinned upstream image), **native OIDC
  SSO** (no oauth2-proxy in the request path), document attachments via the
  Intercom/WebDAV upload URL, `GRIST_FORCE_LOGIN` enforcement
- ❌ **Out of scope**: replacing full database engines or the BI/reporting
  surfaces of the suite

## Non-Goals

- Being a general-purpose relational database (PostgreSQL stays that role)
- Replacing the suite's dedicated spreadsheet/file collaboration (Nextcloud)

## Requirements

### Requirement: Native OIDC SSO via Keycloak

Grist SHALL authenticate via **native OIDC** (`GRIST_OIDC_IDP_*` with client
secret from `grist-secrets`), with login forced for all access.

#### Scenario: User logs in via OIDC

- GIVEN a user opening the Grist route
- WHEN `GRIST_FORCE_LOGIN=1` intercepts an anonymous request
- THEN the user is redirected to Keycloak OIDC
- AND the resulting suite identity gains access to the `grist` org
- AND `GRIST_SESSION_SECRET` keeps sessions stable across restarts

### Requirement: Uploads via Intercom/WebDAV

Attachments SHALL be stored through the suite upload URL on the WebDAV
layer rather than local disk.

#### Scenario: Upload storage location

- WHEN a user uploads a file to a Grist document
- THEN it is proxied to
  `http://intercom-service.<ns>.svc:8080/cloud/webdav/`
- AND survives Grist pod restarts (external storage)

### Requirement: Single-org workspace

Grist SHALL operate as one organization (`GRIST_SINGLE_ORG=grist`) so the
SSO identity maps directly to the team workspace.

#### Scenario: Identity-to-org mapping

- WHEN a suite user authenticates
- THEN they land in the `grist` organization
- AND no per-tenant org selection is required

### Requirement: Pinned image

Grist SHALL run from a pinned upstream tag (`gristlabs/grist:1.7.21`);
`latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the image is the pinned upstream tag via the local mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| grist | web app (`:8484`) | 1 | `pvc-grist` |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| grist | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `gristlabs/grist:1.7.21` (mirrored, pinned) |
| Port | `:8484` (ingress + `netpol-allow-haproxy-to-grist`) |
| Org | `GRIST_SINGLE_ORG=grist` |
| Auth | `GRIST_FORCE_LOGIN=1`, `GRIST_OIDC_IDP_*` + `grist-secrets` |
| Uploads | `GRIST_UPLOAD_URL` → Intercom WebDAV |

## Depends On

- Keycloak (native OIDC IdP)
- Intercom service (WebDAV upload endpoint)
- HAProxy Ingress

## Integrates With

- Keycloak (native OIDC SSO)
- Intercom (WebDAV upload storage)
- Portal (tile entry)

## SLO

**Tier**: Medium (SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `grist-config` ConfigMap +
  `grist-secrets` secret
- **User data**: `pvc-grist` + WebDAV uploads via the existing backup regime
- **Recovery order**: restore data → redeploy from GitOps → verify OIDC
  login
