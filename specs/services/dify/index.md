<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Dify (LLM Application Platform)

## Purpose

Low-code LLM application platform for the suite (chatbots, RAG assistants,
agent workflows) with prompt orchestration, model management and a plugin
ecosystem. Authenticated through the central Keycloak IdP via the **dify SSO
Bridge** — a small Node reverse proxy (same pattern as the n8n bridge) that
adds OIDC SSO and user provisioning to the open-source Dify distribution.

## Scope

- ✅ **In scope**: Dify deployment (web/api/worker/plugin-daemon), route
  split via the dedicated dify-nginx, OIDC SSO via the dify bridge, vector
  search (Weaviate) and metadata persistence (PostgreSQL), plugin storage
- ❌ **Out of scope**: Dify cloud/enterprise features, model gateway
  licensing concerns, replacing other suite AI surfaces (kept separate from
  Operaton BPMN orchestration)

## Non-Goals

- Becoming the suite's process engine (that is Operaton's role)
- Hosting third-party tenants
- Running models inside the suite without the configured model backend

## Requirements

### Requirement: SSO via dify bridge (Keycloak OIDC)

Users SHALL reach Dify only through the bridge, which authenticates via
Keycloak OIDC and provisions Dify users (mirroring the n8n bridge pattern:
deterministic derived credentials + REST session injection).

#### Scenario: User logs in via the bridge

- GIVEN a user opening the Dify route without a valid session
- WHEN the bridge redirects to Keycloak and authentication completes
- THEN the bridge provisions the Dify user for the OIDC identity
- AND the session is injected so no local login form is shown

### Requirement: Route split via dedicated nginx

The public Dify request path SHALL be
`ingress → dify-bridge:8080 → dify-nginx:80 → dify-web / dify-api`, with the
nginx split:

| Location | Backend |
|----------|---------|
| `/api`, `/console/api`, `/explore/api`, `/files`, `/v1`, `/health` | `dify-api:5001` |
| `/` (everything else) | `dify-web:3000` |

#### Scenario: API vs console routing

- GIVEN a request to `/api/v1/...` (agent/chat API) or `/console/api/...`
- THEN it proxies to the dify API backend, not the web frontend

### Requirement: Persistence

Dify SHALL keep metadata in the dedicated PostgreSQL database and embeddings
in the Weaviate vector store, backed by PVCs; plugin storage SHALL be
persistent.

#### Scenario: Data survives restart

- WHEN a dify api/worker pod is recreated
- THEN app data (datasets, workflows) persists via `dify-postgres`
- AND vector indexes persist via `dify-weaviate`
- AND plugin artifacts persist via `dify-plugin-storage`

### Requirement: Pinned images

Dify images SHALL be pinned tags mirrored through the local registry (e.g.
`dify-api:1.18.0`); `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifests are inspected
- THEN all dify component images are pinned mirrored tags
- AND credentials (OIDC/DB) come from secrets, never from ConfigMaps/values

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| dify-web | Next.js console/explore frontend (`:3000`) | 1 | none |
| dify-api | FastAPI backend (`:5001`) | 1 | `dify-data` PVC |
| dify-worker | async jobs (Celery-style) | 1 | — |
| dify-plugin-daemon | plugin runtime | 1 | `dify-plugin-storage` |
| dify-nginx | route split (web vs api) | 1 | none |
| dify-bridge | OIDC reverse proxy + user provisioning (`:8080`) | 1 | none |
| dify-postgres | metadata | shared | `dify-postgres` Pvc |
| dify-weaviate | vector store | shared | `dify-weaviate` Pvc |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| dify components | non-root (distro default) | drop: ALL | RuntimeDefault |
| dify-bridge | non-root | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Images | `dify-api:1.18.0` (+ web/worker/plugin-daemon pinned tags), mirrored |
| Route | `dify.<cluster-domain>` → ingress → bridge → nginx |
| OIDC | Keycloak realm client via `dify-bridge` secret |
| Stores | PostgreSQL (metadata), Weaviate (vector), plugin storage PVC |

## Depends On

- Keycloak (OIDC IdP)
- PostgreSQL (dify metadata schema)
- Weaviate (vector store)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via the bridge)
- Portal (tile entry)
- Model backend (configured provider keys managed via Dify UI/secrets)

## SLO

**Tier**: Medium (stateful, SSO-gated, modest traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms (chat/API) | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + bridge code in ConfigMap
  (code edits require a bridge rollout restart to take effect)
- **User data**: `dify-postgres` + `dify-weaviate` + `dify-plugin-storage`
  backups via the existing backup regime
- **Recovery order**: restore stores → redeploy from GitOps → verify SSO via
  bridge health endpoint
