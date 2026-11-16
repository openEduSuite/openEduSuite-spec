<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Kitodo (Digital Library)

## Purpose

Kitodo.Production is a comprehensive digitalization and publishing workflow
system for managing digitized document collections, metadata enrichment,
and DFG-viewer presentation. It supports the university library's workflows
for digitization projects, including import, OCR, metadata editing, and
publication of digital collections.

## Scope

- ✅ **In scope**: Kitodo.Production application deployment (Java web app),
  dedicated MySQL/MariaDB database (`kitodo-db`), Elasticsearch cluster
  (`kitodo-es`) for full-text and metadata search, RabbitMQ message queue
  (`kitodo-mq`) for asynchronous task processing, oauth2-proxy SSO via
  Keycloak OIDC, persistent storage for digitized assets
- ❌ **Out of scope**: Multi-tenant hosting for external institutions,
  replacing the primary library catalog system, public-facing discovery layer
  (handled by DFG-viewer frontends)

## Non-Goals

- Hosting digitization workflows for non-library units
- Providing a general-purpose document management system outside the
  digitization/publishing domain
- Replacing existing repository systems (e.g., DSpace, Fedora)

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Kitodo.Production SHALL be reachable only through the dedicated oauth2-proxy
instance (`kitodo-oauth2-proxy`, image `oauth2-proxy:v7.15.4`, provider
`oidc`, Keycloak), with `--upstream=http://kitodo-app:8080`. No local
account login for regular users.

#### Scenario: User accesses Kitodo via SSO

- GIVEN a user opening `kitodo.<cluster-domain>`
- WHEN the oauth2-proxy finds no valid `_oauth2_proxy_kitodo` cookie
- THEN the user is redirected to Keycloak for OIDC authentication
- AND the resulting session cookie grants access to Kitodo.Production

### Requirement: Application image and port

Kitodo.Production SHALL run from the pinned SLUB image
`172.25.24.36:5001/slub/kitodo-production-docker/kitodo_production:3.5.0-2`
exposing HTTP container port 8080.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the application container uses the pinned Kitodo.Production 3.5.0-2
  image from the SLUB registry
- AND the container listens on port 8080 for HTTP traffic

### Requirement: Database backend (MySQL/MariaDB)

Kitodo.Production SHALL use the dedicated MySQL/MariaDB deployment
`kitodo-db` (port 3306) with database and user both named `kitodo`,
credentials provided via `kitodo-secrets`.

#### Scenario: Database connectivity

- GIVEN the Kitodo application pod
- WHEN it connects to `kitodo-db:3306`
- THEN it authenticates with the `kitodo` user
- AND persists all workflow, metadata, and user data in the `kitodo` database

### Requirement: Full-text search via Elasticsearch

Kitodo.Production SHALL index and search digitized content metadata and
full-text via the dedicated Elasticsearch deployment `kitodo-es` (ports
9200 for HTTP, 9300 for transport).

#### Scenario: Search functionality

- GIVEN a user performs a search in Kitodo
- WHEN the query is submitted
- THEN Kitodo forwards the search request to `kitodo-es:9200`
- AND results are returned from Elasticsearch indices

### Requirement: Asynchronous processing via RabbitMQ

Kitodo.Production SHALL use the dedicated RabbitMQ deployment `kitodo-mq`
for message queuing of asynchronous tasks (digitization workflows, OCR
processing, metadata export).

#### Scenario: Job processing

- GIVEN a digitization workflow is initiated
- WHEN tasks require asynchronous processing
- THEN job messages are published to `kitodo-mq`
- AND worker components consume and process these messages

### Requirement: Separate backend deployments

Kitodo backend services (database, Elasticsearch, RabbitMQ) SHALL be
deployed as separate, dedicated deployments (`deploy-kitodo-db.yaml`,
`deploy-kitodo-es.yaml`, `deploy-kitodo-mq.yaml`) to enable independent
scaling and lifecycle management.

#### Scenario: Independent service management

- GIVEN a need to scale Elasticsearch independently
- WHEN `deploy-kitodo-es.yaml` is updated
- THEN only the `kitodo-es` deployment is affected
- AND the Kitodo application and other backends remain unchanged

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| kitodo-app | Kitodo.Production 3.5.0-2 Java web application | 1+ | — |
| kitodo-db | MySQL/MariaDB database for Kitodo | 1 | MySQL data PVC |
| kitodo-es | Elasticsearch for full-text and metadata search | 1+ | Elasticsearch data PVC |
| kitodo-mq | RabbitMQ message queue for async tasks | 1 | RabbitMQ data PVC |
| kitodo-oauth2-proxy | OAuth2 proxy (v7.15.4) for Keycloak OIDC SSO | 1 | — |

## Security Context

Kitodo.Production is a Java-heavy application. The target security posture
SHALL be:

- Run as non-root user
- Capabilities: drop ALL
- Seccomp profile: RuntimeDefault
- No privilege escalation allowed

Kyverno policies (zki-*) apply to all Kitodo deployments and enforce
these constraints at admission time.

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/slub/kitodo-production-docker/kitodo_production:3.5.0-2` (pinned) |
| Route | `kitodo.<cluster-domain>` → kitodo-oauth2-proxy → kitodo-app:8080 |
| Container Port | 8080 (HTTP) |
| Database | `kitodo-db:3306`, database/user: `kitodo` (credentials from `kitodo-secrets`) |
| Search | `kitodo-es:9200/9300` (Elasticsearch) |
| Message Queue | `kitodo-mq` (RabbitMQ) |
| SSO | oauth2-proxy v7.15.4, provider: `oidc`, upstream: `http://kitodo-app:8080` |

## Depends On

- Keycloak (OIDC identity provider via oauth2-proxy)
- MySQL/MariaDB (`kitodo-db`, port 3306)
- Elasticsearch (`kitodo-es`, ports 9200/9300)
- RabbitMQ (`kitodo-mq`)
- `kitodo-secrets` (database credentials)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `kitodo-oauth2-proxy`)
- DFG-viewer (presentation layer for digitized collections)
- University library digitization workflows and systems
- Portal (tile entry for Kitodo access)

## SLO

**Tier**: Standard (stateful, SSO-gated, moderate traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <800 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Standard (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests (`deploy-kitodo-*.yaml`,
  oauth2-proxy configuration)
- **User data**: MySQL database (`kitodo-db`) + Elasticsearch indices
  (`kitodo-es`) + persistent volumes backups via the existing backup regime
- **Recovery order**: restore DB (`kitodo-db`) → restore Elasticsearch
  (`kitodo-es`) → restore Redis (if used) → redeploy Kitodo application
  from GitOps → verify SSO via oauth2-proxy (`kitodo-oauth2-proxy`)
