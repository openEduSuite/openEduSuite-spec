<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Operaton (BPM Engine)

## Purpose

BPMN 2.0 / DMN 1.3 process orchestration engine for the suite: workflow
automation with human-in-the-loop tasks. Its primary production workload is
**user lifecycle automation** — self-service user provisioning and
reconciliation across the suite's individual services (Keycloak, n8n,
Synapse, ...) via an external-task worker. Operaton is the
community-maintained Apache 2.0 successor of Camunda 7 Community Edition
(EOL October 2025); it preserves the Camunda 7 API, model format, and
database schema while providing continued security patches.

## Scope

- ✅ **In scope**: embedded-style BPMN/DMN engine (Tomcat distribution), Cockpit/Tasklist/Admin web apps, REST API, PostgreSQL persistence, Keycloak OIDC federation for webapp login, Ingress exposure, patch-tracking as pinned image
- ❌ **Out of scope**: Camunda 8 / Zeebe (paid production license + Elasticsearch footprint), Camunda Optimize analytics, SaaS offerings, embedded-engine Java dependencies in other suite services (REST-only contract)

## Non-Goals

- Multi-tenant process hosting for third parties
- High-frequency event-streaming orchestration (Camunda 8 territory, deliberately not used)
- Replacing the suite's n8n automation (n8n = system glue/integrations; Operaton = audited business processes with human tasks)

## Requirements

### Requirement: Maintained Apache-2.0 engine distribution

The engine SHALL run from a pinned `operaton/operaton` Tomcat-distribution
image tag whose release is within the project's supported window. Images
from the archived Camunda 7 upstream SHALL NOT be used.

#### Scenario: Image provenance and pinning

- GIVEN the deployment manifests are reviewed
- WHEN the engine image reference is inspected
- THEN it is a pinned immutable `operaton/operaton` tag (no `latest`)
- AND the tag maps to a release still receiving monthly Operaton patches

### Requirement: PostgreSQL persistence

The engine SHALL persist process definitions, runtime state, and history in
a dedicated PostgreSQL database (separate database and role), backed by a
persistent volume.

#### Scenario: State survives restart

- WHEN the engine pod is rescheduled or recreated
- THEN deployed process definitions and process history remain intact
- AND no manual schema intervention is required (consecutive-version schema compatibility is a documented Operaton guarantee)

The user-lifecycle process suite is the engine's primary workload; its model
source lives in `k8s/operaton/processes/` in the deployment repo:
`user-provisioning.bpmn`, `user-deprovisioning.bpmn`,
`user-deletion.bpmn`, `user-reconciliation.bpmn`. They are NOT deployed by
git/GitOps — they are pushed to the engine at runtime via the engine REST
API (`scripts/deploy-operaton-lifecycle.sh`, deployment name
`user-lifecycle`).

### Requirement: SSO via Keycloak (mandatory central auth)

The engine web applications (Cockpit, Tasklist, Admin) SHALL authenticate
users exclusively through the central Keycloak OIDC provider; local engine
accounts SHALL NOT be used for regular users.

#### Scenario: User reaches Tasklist via SSO

- GIVEN a user with a valid suite session
- WHEN the user opens the engine web app at `bpm.<cluster-domain>`
- THEN authentication is delegated to Keycloak (OIDC)
- AND no local password prompt is shown

#### Scenario: Lifecycle flows deployed to the engine

- GIVEN the operator runs `scripts/deploy-operaton-lifecycle.sh`
- WHEN the engine REST API receives the `user-lifecycle` deployment
- THEN `user-provisioning`, `user-deprovisioning`, `user-deletion` and
  `user-reconciliation` appear as process definitions (engine
  `ACT_RE_PROCDEF` / `process-definition` REST)
- AND each deployment run creates a new deployment version (versions
  accumulate deliberately for audit)

### Requirement: REST-only integration contract

Suite services SHALL integrate with the engine exclusively via its HTTP
REST API. Suite-owned images MUST NOT bundle engine Java API dependencies
(`org.camunda.*` / `org.operaton.*`), keeping the engine swappable between
REST-compatible C7-lineage distributions by changing one image reference.

#### Scenario: Consumer uses REST only

- WHEN a suite service starts or completes workflow tasks
- THEN it does so via the engine REST API
- AND the consumer image contains no engine client libraries

#### Scenario: Fork swap is non-breaking

- WHEN the engine image is exchanged for a REST-compatible distribution (e.g. CIB seven)
- THEN no suite-owned image requires a rebuild

### Requirement: Ingress exposure with TLS

The engine web apps SHALL be reachable at `bpm.<cluster-domain>` through
the suite ingress with TLS termination, following the standard middleware
chain.

#### Scenario: HTTPS route serves engine

- WHEN a user navigates to `bpm.<cluster-domain>`
- THEN the Cockpit/Tasklist login page is served over HTTPS

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| Operaton (Tomcat distro) | BPMN/DMN engine + Cockpit/Tasklist/Admin + REST API | 1 | none (stateless pod) |
| Lifecycle external-task worker | subscribes to `user-reconcile`, `provision-*`, `deprovision-*`, `delete-*` service-task topics; drives Keycloak/n8n/Synapse via REST | 1 | none |
| PostgreSQL (dedicated DB/role) | process runtime + history store | shared cluster instance | PVC (managed by DB layer) |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| Operaton Tomcat | non-root (distro default) | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `operaton/operaton:<pinned tomcat tag>` |
| Database | dedicated DB `operaton` / role `operaton`, credentials via secret |
| OIDC | Keycloak realm client `operaton` (confidential), engine webapp SSO plugin |
| Route | `bpm.<cluster-domain>` → service port 8080 |
| JVM | container memory limit sized for engine + webapps (start: 1–2 GiB) |
| Patches | monthly Operaton patch releases tracked via image-cadence policy |

## Depends On

- HAProxy Ingress
- PostgreSQL
- Keycloak

## Integrates With

- Nubus Portal (tile for Cockpit/Tasklist)
- Keycloak (OIDC SSO; lifecycle worker uses the admin API for
  provision/deprovision/delete of users)
- n8n (complementary: n8n orchestrates system glue; Operaton executes audited
  human workflows; lifecycle worker invokes n8n via its internal JWT API)
- Synapse (lifecycle worker deprovisions matrix accounts on
  `matrix.<cluster-domain>` via admin API)
- PostgreSQL (peristence via dedicated `operaton` database)

## SLO

**Tier**: Medium (stateful process data, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms (REST API) | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

**Alerts**:
- Pod restart loop >3 in 10 minutes → P2 alert (process data at risk)
- DB connection failures in engine logs → P2 alert
- 5xx rate >2% for 10 minutes → P3 alert
- Lifecycle worker `POLL-FEHLER`/`fetch failed` burst >5 in 10 minutes → P2
  (user provisioning/reconciliation stalls; a `fetch failed` burst during
  engine startup is benign noise)

**Capacity**:
- Start: single replica; process throughput needs of administrative workflows are modest (tens of instances/day scale, not thousands/sec)
- Scale-out beyond 1 replica requires DB-backed job-executor tuning; defer until measured need

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

**Backup Strategy**:
- **Configuration**: GitOps-managed manifests
- **User data**: PostgreSQL backups (process definitions, instances, history) via the DB layer's existing backup regime

**Recovery Order**:
1. PostgreSQL restore (dedicated `operaton` database) — engine schema is compatible within consecutive minor versions
2. Engine deployment from GitOps — 10 min
3. SSO/Ingress verification — 10 min

**Critical Data**:
- Process definitions (BPMN/DMN models) — additionally version-controlled in Git by process authors AND pushed to the engine at runtime (`user-lifecycle` deployment); re-deploy via `scripts/deploy-operaton-lifecycle.sh` after a DB restore
- Running process instances and history — recoverable from DB backups only

**Failure Scenarios**:
- **Pod crash**: Kubernetes auto-restart; in-flight transactions recover via engine transaction log in DB
- **DB outage**: engine unavailable until DB returns; no data loss beyond DB backup RPO
- **Complete failure**: GitOps redeploy + DB restore
