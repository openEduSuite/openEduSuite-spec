<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Greenlight (BigBlueButton Frontend)

## Purpose

Greenlight v3 is the BigBlueButton user-facing frontend / UI for room
management and joining BBB meetings. It complements the bbb-core / k8s BBB
deployments by providing a web interface where users sign in, create and
configure rooms, schedule sessions, manage recordings, and obtain join URLs
into the underlying BigBlueButton backend meetings. Authentication uses
Greenlight v3's native OpenID Connect client against Keycloak
(`OPENID_CONNECT_*` envs); there is no oauth2-proxy gateway in the path.

## Scope

- ✅ **In scope**: Greenlight v3 web deployment (pinned upstream image),
  dedicated PostgreSQL + Redis backends, persistent storage via
  `greenlight-pvc`, served at `https://bbb.openedusuite.org` behind the
  BigBlueButton nginx frontend, native OIDC SSO against Keycloak
  (`OPENID_CONNECT_*`), room management and BBB meeting join flows
- ❌ **Out of scope**: the BBB backend / media server deployment itself (see
  `../bigbluebutton`), WebRTC media processing, recording storage on the BBB
  backend, GPU-accelerated transcription

## Non-Goals

- Replacing or duplicating the BBB backend conferencing server (managed
  separately; see `../bigbluebutton`)
- Standard video conferencing without BBB (see `../jitsi`)
- Recording file storage (handled by the BBB backend; Greenlight stores only
  recording metadata / pointers)

## Requirements

### Requirement: Pinned image and HTTP container port

Greenlight SHALL run from the pinned upstream image
`bigbluebutton/greenlight:v3.9.0.1`; floating tags are not used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the container image is `bigbluebutton/greenlight:v3.9.0.1`
- AND the HTTP container port exposed is `3000`

### Requirement: SSO via native OpenID Connect (Keycloak)

Greenlight SHALL authenticate suite identities through its own OpenID
Connect client configured against Keycloak (`OPENID_CONNECT_ISSUER` =
`https://id.openedusuite.org/realms/openedusuite`,
`OPENID_CONNECT_CLIENT_ID=greenlight`, `OPENID_CONNECT_UID_FIELD=sub`),
so suite identities are brokered by the central IdP without a local
password store for regular users.

#### Scenario: User reaches Greenlight via SSO

- GIVEN a user opening `https://bbb.openedusuite.org`
- WHEN no Greenlight session exists for the user
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the OIDC redirect back to Greenlight establishes the session

### Requirement: Dedicated persistence

Greenlight SHALL persist room metadata, user accounts and session state in
the dedicated `greenlight-postgres` and `greenlight-redis` deployments, with
file storage on the `greenlight-pvc` PVC.

#### Scenario: Room data survives restart

- WHEN a greenlight pod is recreated
- THEN rooms, user accounts and settings persist via `greenlight-postgres`
- AND session / cache state is rebuilt via `greenlight-redis`
- AND uploaded / generated files survive via `greenlight-pvc`

### Requirement: Configuration and secrets

Greenlight SHALL be configured via the `greenlight-config` ConfigMap and
sensitive values via the `greenlight-secrets` secret.

#### Scenario: Config and secret wiring

- GIVEN the deployment manifest
- THEN non-sensitive configuration is mounted from the
  `greenlight-config` ConfigMap
- AND credentials (DB URL, secret key base, BBB endpoint / secret) are
  sourced from the `greenlight-secrets` secret

### Requirement: Serving at the BigBlueButton domain

Greenlight SHALL be exposed at `https://bbb.openedusuite.org` (`URL_HOST`)
through the BigBlueButton ingress/nginx frontend (bbb-nginx), proxying to
the Greenlight service (`greenlight:3000`).

#### Scenario: External access

- WHEN a user navigates to `https://bbb.openedusuite.org`
- THEN the BBB nginx frontend routes the request to the Greenlight service
  on port `3000`
- AND Greenlight serves the room-management UI under `URL_PREFIX: /`

### Requirement: BBB backend integration

Greenlight SHALL communicate with the BigBlueButton backend server via the
BBB API to create meetings and generate join URLs.

#### Scenario: Room creation and meeting join

- GIVEN an authenticated user creating a room in Greenlight
- WHEN the room is created and a meeting started
- THEN Greenlight calls the BBB backend API to create the meeting
- AND a join URL is returned for the user to enter the BBB session

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| greenlight | BigBlueButton frontend / UI (`:3000`) | 1 | `greenlight-pvc` |
| greenlight-postgres | PostgreSQL for rooms, users, metadata | 1 | data PVC |
| greenlight-redis | Redis for session / cache state | 1 | — |
| bbb-nginx | BBB nginx frontend (`proxy_pass greenlight:3000`) | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| greenlight | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `bigbluebutton/greenlight:v3.9.0.1` (pinned) |
| Port | `:3000` (container HTTP) |
| Route | `https://bbb.openedusuite.org` (`URL_HOST`) via bbb-nginx → greenlight:3000 |
| Config | `greenlight-config` ConfigMap (`OPENID_CONNECT_*`, `URL_HOST`, `BD_BBB_ENDPOINT`) |
| Secrets | `greenlight-secrets` secret (DB URL, secret key base, BBB endpoint/secret) |
| Stores | `greenlight-postgres` (PostgreSQL), `greenlight-redis` (Redis) |
| Storage | `greenlight-pvc` PVC (file uploads / generated assets) |
| Auth | native OIDC via Keycloak (`OPENID_CONNECT_CLIENT_ID=greenlight`) |

## Depends On

- Keycloak (native OIDC via `OPENID_CONNECT_*`)
- PostgreSQL (`greenlight-postgres`)
- Redis (`greenlight-redis`)
- `greenlight-pvc` persistent volume
- BBB nginx frontend (bbb-nginx / HAProxy Ingress)
- BBB backend server (meeting API; managed separately — see `../bigbluebutton`)

## Integrates With

- Keycloak (native OIDC SSO)
- BigBlueButton backend (meeting creation / join API — see
  `../bigbluebutton`)
- bbb.openedusuite.org domain (shared BBB nginx frontend; not a separate
  portal tile)

## SLO

**Tier**: Standard

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Standard (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `greenlight-config`
  ConfigMap + `greenlight-secrets` secret
- **Data**: `greenlight-postgres`, `greenlight-redis` and `greenlight-pvc`
  backups via the existing backup regime
- **Recovery order**: restore DB + Redis + PVC → redeploy Greenlight from
  GitOps → verify native OIDC login
