<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Integrate Operaton as BPM Engine Service — Tasks

## 1. Packaging

- [ ] 1.1 Determine current stable Operaton release; pin `operaton/operaton` Tomcat tag
- [ ] 1.2 Add helmfile release for the engine behind an environment toggle (off by default), values: image pin, resources (start 1–2 GiB), security context (non-root, drop ALL, RuntimeDefault)
- [ ] 1.3 Provision dedicated PostgreSQL database + role (`operaton`), credentials via secret; verify engine schema auto-creation on first boot

## 2. Identity & Routing

- [ ] 2.1 Create Keycloak OIDC client (`operaton`, confidential) in the suite realm; wire engine webapp SSO plugin (Cockpit/Tasklist/Admin — no local accounts for regular users)
- [ ] 2.2 Ingress route `bpm.<cluster-domain>` → :8080 with TLS via HAProxy Ingress
- [ ] 2.3 Add Nubus portal tile for Cockpit/Tasklist

## 3. Verification

- [ ] 3.1 Smoke: deploy with toggle on → engine boots, schema created, SSO login lands on Cockpit, REST API reachable in-cluster
- [ ] 3.2 Persistence: pod delete/recreate → deployed process definitions and history survive
- [ ] 3.3 Contract check: confirm no suite-owned image gains engine Java API dependencies (REST-only)
- [ ] 3.4 Toggle-off deploy leaves no engine resources behind

## 4. Operations

- [ ] 4.1 Document patch cadence (monthly Operaton releases) in image-cadence/ops docs
- [ ] 4.2 Confirm PostgreSQL backup regime covers the `operaton` database; note RPO ≤24 h / RTO 4 h per service spec
