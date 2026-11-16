# Greenlight (BigBlueButton Frontend)

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

## Purpose

Greenlight v3 is the BigBlueButton user-facing frontend / UI for room
management and joining BBB meetings. It complements the bbb-core / k8s BBB
deployments by providing a web interface where users sign in, create and
configure rooms, schedule sessions, manage recordings, and obtain join URLs
into the underlying BigBlueButton backend meetings. Authentication is handled
through the standard oauth2-proxy gateway pattern (provider `oidc`, Keycloak)
per the ingress / oauth2 wiring.

## Scope

- ✅ **In scope**: Greenlight v3 web deployment (pinned upstream image),
  dedicated PostgreSQL + Redis backends, persistent storage via
  `greenlight-pvc`, ingress routing at `greenlight.<cluster-domain>`,
  SSO via oauth2-proxy (Keycloak OIDC) gateway (per ingress/oauth2 wiring),
  room management and BBB meeting join flows
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

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Greenlight SHALL be reachable only through the per-app oauth2-proxy
gateway (provider `oidc`, Keycloak) per the ingress / oauth2 wiring, so
suite identities are brokered by the central IdP.

#### Scenario: User reaches Greenlight via SSO

- GIVEN a user opening `greenlight.<cluster-domain>`
- WHEN the oauth2-proxy finds no valid session cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to the Greenlight UI

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

### Requirement: Ingress routing

Greenlight SHALL be exposed at `greenlight.<cluster-domain>` through the
suite ingress controller.

#### Scenario: External access

- WHEN a user navigates to `greenlight.<cluster-domain>`
- THEN the ingress routes the request to the Greenlight service on port
  `3000` (behind the oauth2-proxy gateway)

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
| oauth2-proxy | OIDC SSO gateway (Keycloak) | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| greenlight | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `bigbluebutton/greenlight:v3.9.0.1` (pinned) |
| Port | `:3000` (container HTTP) |
| Ingress | `greenlight.<cluster-domain>` → oauth2-proxy → `:3000` |
| Config | `greenlight-config` ConfigMap |
| Secrets | `greenlight-secrets` secret (DB URL, secret key base, BBB endpoint/secret) |
| Stores | `greenlight-postgres` (PostgreSQL), `greenlight-redis` (Redis) |
| Storage | `greenlight-pvc` PVC (file uploads / generated assets) |
| Auth | oauth2-proxy (Keycloak OIDC) gateway (per ingress/oauth2 wiring) |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- PostgreSQL (`greenlight-postgres`)
- Redis (`greenlight-redis`)
- `greenlight-pvc` persistent volume
- HAProxy Ingress
- BBB backend server (meeting API; managed separately — see `../bigbluebutton`)

## Integrates With

- Keycloak (OIDC SSO via oauth2-proxy)
- BigBlueButton backend (meeting creation / join API — see
  `../bigbluebutton`)
- Portal (tile entry)

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
  GitOps → verify SSO via oauth2-proxy
