<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Integrate Operaton as BPM Engine Service — Proposal

## Why

The suite has no process orchestration engine: administrative and
teaching-support workflows (approvals, onboarding, request chains) are
handled ad hoc via mail or tickets, without audit trail or human-task UI.
The natural engine class for auditable, human-in-the-loop workflows is the
Camunda 7 lineage — but Camunda 7 CE is EOL (October 2025) and Camunda 8
carries a paid production license plus an Elasticsearch footprint.

**Operaton** (community-owned Apache 2.0 fork, full API/model/schema
compatibility with Camunda 7.24, monthly patch releases, maintained Tomcat
distribution on Docker Hub) provides the engine without license risk.

## What Changes

- New service: Operaton BPM engine (single Tomcat pod, dedicated PostgreSQL
  database, Keycloak OIDC SSO, Ingress route `bpm.<cluster-domain>`)
- Canonical service spec: [`specs/services/operaton/`](../../specs/services/operaton/index.md)
  (this change integrates it; the spec is the normative reference — no
  separate delta spec needed since no prior engine spec exists)
- Helmfile/GitOps wiring behind an environment toggle so clusters without
  workflow needs don't run it
- Explicit REST-only contract for all suite integrations (no engine Java
  API dependencies in suite-owned images) — keeps the engine swappable
  (CIB seven is the evaluated runner-up fork)

## Alternatives Considered

| Option | Verdict |
|---|---|
| Camunda 8 | rejected: paid production license (self-managed, since 8.6) + mandatory Elasticsearch |
| CIB seven | runner-up; free community edition includes C7-EE ops features; swap-compatible later via REST contract |
| Fluxnova (FINOS) | strongest governance (Linux Foundation, bank-backed) but no maintained container distribution yet; watchlist |
| EximeeBPMS / orquieo | single-vendor / closed — rejected |
| Flowable / Activiti | different engine lineage; integration is a rewrite, not a REST-compatible swap |
| Stay engine-less | workflows remain ad hoc; rejected for auditability goals |

## Impact

- New helmfile release (engine) + PostgreSQL database provisioning + Keycloak
  client + Ingress route + portal tile
- No existing service changes (greenfield integration)
- New operational duty: monthly Operaton patch tracking (pinned image
  policy)
