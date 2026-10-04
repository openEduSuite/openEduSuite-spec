<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Implementation Tasks: Nix Integration

**Change ID:** nix-integration-001  
**Related Proposal:** [proposal.md](./proposal.md)  
**Related Delta Spec:** [specs.md](./specs.md)  
**Status:** Draft  

This document breaks down the implementation of the Nix integration into actionable tasks, organized by phase and priority.

---

## Task Organization

Tasks are organized by:
1. **Phase:** One of the 8 migration phases
2. **Wave:** Independent work units within a phase (can be parallelized)
3. **Priority:** P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
4. **Effort:** S (Small: <4h), M (Medium: 4-8h), L (Large: 8-16h), XL (Extra Large: >16h)
5. **Dependencies:** Prerequisite tasks
6. **Assignee:** Team member responsible (TBD)
7. **Status:** ⏳ Not Started, 🔄 In Progress, ✅ Done, ❌ Blocked

---

## Phase 0: Preparation (Week 0)

### Wave 0.1: Project Setup

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T0.1.01 | Review and finalize this proposal document | P0 | M | None | TBD | ⏳ |
| T0.1.02 | Set up project tracking (GitHub Projects or similar) | P0 | S | T0.1.01 | TBD | ⏳ |
| T0.1.03 | Create milestones for each phase | P0 | S | T0.1.02 | TBD | ⏳ |
| T0.1.04 | Create labels for tasks (phase, priority, type) | P1 | S | T0.1.02 | TBD | ⏳ |

### Wave 0.2: Repository Setup

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T0.2.01 | Verify `opendesk-nix` repository structure | P0 | S | None | TBD | ⏳ |
| T0.2.02 | Set up branch protection rules for `opendesk-nix` | P0 | S | T0.2.01 | TBD | ⏳ |
| T0.2.03 | Configure CI/CD for `opendesk-nix` (basic workflows) | P0 | M | T0.2.01 | TBD | ⏳ |
| T0.2.04 | Create CONTRIBUTING.md for `opendesk-nix` | P1 | S | T0.2.01 | TBD | ⏳ |

### Wave 0.3: Initial Documentation

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T0.3.01 | Create README.md for `opendesk-nix` | P0 | M | T0.2.01 | TBD | ⏳ |
| T0.3.02 | Create docs/ARCHITECTURE.md | P1 | L | T0.2.01 | TBD | ⏳ |
| T0.3.03 | Create initial migration guide outline | P1 | S | T0.2.01 | TBD | ⏳ |

---

## Phase 1: Foundation (Week 1-2)

### Wave 1.1: Library Migration

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.1.01 | Copy `opendesk-edu/nix/lib/k8s.nix` to `opendesk-nix/lib/k8s.nix` | P0 | S | Phase 0 | TBD | ⏳ |
| T1.1.02 | Update `k8s.nix` to match new requirements | P0 | L | T1.1.01 | TBD | ⏳ |
| T1.1.03 | Add tests for `k8s.nix` library | P1 | M | T1.1.02 | TBD | ⏳ |
| T1.1.04 | Document `k8s.nix` library | P1 | M | T1.1.02 | TBD | ⏳ |

### Wave 1.2: Security Library

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.2.01 | Create `lib/security.nix` | P0 | M | Phase 0 | TBD | ⏳ |
| T1.2.02 | Define security profiles (default, database, web, etc.) | P0 | M | T1.2.01 | TBD | ⏳ |
| T1.2.03 | Add hardened image wrapper | P0 | M | T1.2.02 | TBD | ⏳ |
| T1.2.04 | Add tests for security library | P1 | M | T1.2.03 | TBD | ⏳ |
| T1.2.05 | Document security requirements | P1 | S | T1.2.03 | TBD | ⏳ |

### Wave 1.3: SBOM Library

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.3.01 | Create `lib/sbom.nix` | P0 | M | Phase 0 | TBD | ⏳ |
| T1.3.02 | Add CycloneDX SBOM generation | P0 | M | T1.3.01 | TBD | ⏳ |
| T1.3.03 | Add SPDX SBOM generation | P0 | M | T1.3.02 | TBD | ⏳ |
| T1.3.04 | Add SBOM validation | P1 | S | T1.3.03 | TBD | ⏳ |
| T1.3.05 | Add tests for SBOM library | P1 | M | T1.3.04 | TBD | ⏳ |

### Wave 1.4: Registry Library

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.4.01 | Create `lib/registry.nix` | P0 | M | Phase 0 | TBD | ⏳ |
| T1.4.02 | Add GitLab registry support | P0 | S | T1.4.01 | TBD | ⏳ |
| T1.4.03 | Add GHCR registry support | P0 | S | T1.4.01 | TBD | ⏳ |
| T1.4.04 | Add Zot registry support | P0 | S | T1.4.01 | TBD | ⏳ |
| T1.4.05 | Add push/multi-push functions | P0 | M | T1.4.01 | TBD | ⏳ |
| T1.4.06 | Add tests for registry library | P1 | M | T1.4.05 | TBD | ⏳ |

### Wave 1.5: Types Library

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.5.01 | Create `lib/types.nix` | P1 | M | Phase 0 | TBD | ⏳ |
| T1.5.02 | Define image configuration types | P1 | M | T1.5.01 | TBD | ⏳ |
| T1.5.03 | Define K8s resource types | P1 | M | T1.5.02 | TBD | ⏳ |
| T1.5.04 | Add validation for types | P2 | S | T1.5.03 | TBD | ⏳ |

### Wave 1.6: Flake Structure

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.6.01 | Update `opendesk-nix/flake.nix` with library imports | P0 | L | T1.1.01, T1.2.01, T1.3.01, T1.4.01 | TBD | ⏳ |
| T1.6.02 | Add common configuration to flake | P0 | M | T1.6.01 | TBD | ⏳ |
| T1.6.03 | Add initial package definitions | P0 | M | T1.6.02 | TBD | ⏳ |
| T1.6.04 | Add initial app definitions | P0 | M | T1.6.03 | TBD | ⏳ |
| T1.6.05 | Add dev shell definitions | P1 | M | T1.6.04 | TBD | ⏳ |

### Wave 1.7: Directory Structure

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.7.01 | Create `images/` directory structure | P0 | S | T1.6.05 | TBD | ⏳ |
| T1.7.02 | Create `k8s/` directory structure | P0 | S | T1.6.05 | TBD | ⏳ |
| T1.7.03 | Create `scripts/` directory | P0 | S | T1.6.05 | TBD | ⏳ |
| T1.7.04 | Create `tests/` directory structure | P0 | S | T1.6.05 | TBD | ⏳ |
| T1.7.05 | Create `docs/` directory structure | P0 | S | T1.6.05 | TBD | ⏳ |

### Wave 1.8: Testing Foundation

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.8.01 | Test that flake can be evaluated | P0 | S | Phase 1 | TBD | ⏳ |
| T1.8.02 | Test that all libraries load | P0 | S | Phase 1 | TBD | ⏳ |
| T1.8.03 | Test that dev shell works | P0 | S | Phase 1 | TBD | ⏳ |
| T1.8.04 | Test that basic package builds | P0 | S | Phase 1 | TBD | ⏳ |

### Wave 1.9: CI/CD Setup

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.9.01 | Create GitHub Actions workflow for builds | P0 | M | Phase 1 | TBD | ⏳ |
| T1.9.02 | Create GitHub Actions workflow for tests | P0 | M | Phase 1 | TBD | ⏳ |
| T1.9.03 | Create GitLab CI configuration | P0 | M | Phase 1 | TBD | ⏳ |
| T1.9.04 | Test CI/CD workflows with sample services | P0 | M | T1.9.01, T1.9.02, T1.9.03 | TBD | ⏳ |

---

## Phase 2: Core Services (Week 3-4)

### Wave 2.1: SOGo 5 & 6

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.1.01 | Create `images/sogo5/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.1.02 | Define SOGo 5 image configuration | P0 | M | T2.1.01 | TBD | ⏳ |
| T2.1.03 | Copy SOGo 5 Dockerfile (reference) | P1 | S | T2.1.01 | TBD | ⏳ |
| T2.1.04 | Copy SOGo 5 config files | P1 | S | T2.1.01 | TBD | ⏳ |
| T2.1.05 | Build SOGo 5 image with Nix | P0 | M | T2.1.02 | TBD | ⏳ |
| T2.1.06 | Test SOGo 5 image | P0 | M | T2.1.05 | TBD | ⏳ |
| T2.1.07 | Create `k8s/services/sogo5.nix` | P0 | M | T2.1.05, T1.1.02 | TBD | ⏳ |
| T2.1.08 | Generate SOGo 5 K8s manifests | P0 | M | T2.1.07 | TBD | ⏳ |
| T2.1.09 | Validate SOGo 5 manifests | P0 | S | T2.1.08 | TBD | ⏳ |
| T2.1.10 | Create `images/sogo6/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.1.11 | Define SOGo 6 image configuration | P0 | M | T2.1.10 | TBD | ⏳ |
| T2.1.12 | Copy SOGo 6 Dockerfile (reference) | P1 | S | T2.1.10 | TBD | ⏳ |
| T2.1.13 | Copy SOGo 6 config files | P1 | S | T2.1.10 | TBD | ⏳ |
| T2.1.14 | Build SOGo 6 image with Nix | P0 | M | T2.1.11 | TBD | ⏳ |
| T2.1.15 | Test SOGo 6 image | P0 | M | T2.1.14 | TBD | ⏳ |
| T2.1.16 | Create `k8s/services/sogo6.nix` | P0 | M | T2.1.14, T1.1.02 | TBD | ⏳ |
| T2.1.17 | Generate SOGo 6 K8s manifests | P0 | M | T2.1.16 | TBD | ⏳ |
| T2.1.18 | Validate SOGo 6 manifests | P0 | S | T2.1.17 | TBD | ⏳ |

### Wave 2.2: Dev Agent & Zot Registry

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.2.01 | Create `images/dev-agent/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.2.02 | Define dev-agent image configuration | P0 | M | T2.2.01 | TBD | ⏳ |
| T2.2.03 | Build dev-agent image | P0 | M | T2.2.02 | TBD | ⏳ |
| T2.2.04 | Test dev-agent image | P0 | M | T2.2.03 | TBD | ⏳ |
| T2.2.05 | Create `k8s/services/dev-agent.nix` | P0 | M | T2.2.04, T1.1.02 | TBD | ⏳ |
| T2.2.06 | Create `images/zot-registry/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.2.07 | Define zot-registry image configuration | P0 | M | T2.2.06 | TBD | ⏳ |
| T2.2.08 | Build zot-registry image | P0 | M | T2.2.07 | TBD | ⏳ |
| T2.2.09 | Test zot-registry image | P0 | M | T2.2.08 | TBD | ⏳ |
| T2.2.10 | Create `k8s/services/zot-registry.nix` | P0 | M | T2.2.09, T1.1.02 | TBD | ⏳ |

### Wave 2.3: Database Services

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.3.01 | Create `images/mariadb/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.3.02 | Define MariaDB image with security hardening | P0 | M | T2.3.01, T1.2.03 | TBD | ⏳ |
| T2.3.03 | Build MariaDB image | P0 | M | T2.3.02 | TBD | ⏳ |
| T2.3.04 | Test MariaDB image | P0 | M | T2.3.03 | TBD | ⏳ |
| T2.3.05 | Create `k8s/services/mariadb.nix` (StatefulSet) | P0 | M | T2.3.04, T1.1.02 | TBD | ⏳ |
| T2.3.06 | Create `images/postgresql/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.3.07 | Define PostgreSQL image with security hardening | P0 | M | T2.3.06, T1.2.03 | TBD | ⏳ |
| T2.3.08 | Build PostgreSQL image | P0 | M | T2.3.07 | TBD | ⏳ |
| T2.3.09 | Test PostgreSQL image | P0 | M | T2.3.08 | TBD | ⏳ |
| T2.3.10 | Create `k8s/services/postgresql.nix` (StatefulSet) | P0 | M | T2.3.09, T1.1.02 | TBD | ⏳ |
| T2.3.11 | Create `images/redis/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.3.12 | Define Redis image with security hardening | P0 | M | T2.3.11, T1.2.03 | TBD | ⏳ |
| T2.3.13 | Build Redis image | P0 | M | T2.3.12 | TBD | ⏳ |
| T2.3.14 | Test Redis image | P0 | M | T2.3.13 | TBD | ⏳ |
| T2.3.15 | Create `k8s/services/redis.nix` (StatefulSet) | P0 | M | T2.3.14, T1.1.02 | TBD | ⏳ |
| T2.3.16 | Create `images/memcached/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.3.17 | Define Memcached image with security hardening | P0 | M | T2.3.16, T1.2.03 | TBD | ⏳ |
| T2.3.18 | Build Memcached image | P0 | M | T2.3.17 | TBD | ⏳ |
| T2.3.19 | Test Memcached image | P0 | M | T2.3.18 | TBD | ⏳ |
| T2.3.20 | Create `k8s/services/memcached.nix` (Deployment) | P0 | M | T2.3.19, T1.1.02 | TBD | ⏳ |

### Wave 2.4: Keycloak & Nubus

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.4.01 | Create `images/keycloak/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.4.02 | Define Keycloak image with security hardening | P0 | M | T2.4.01, T1.2.03 | TBD | ⏳ |
| T2.4.03 | Build Keycloak image | P0 | M | T2.4.02 | TBD | ⏳ |
| T2.4.04 | Test Keycloak image | P0 | M | T2.4.03 | TBD | ⏳ |
| T2.4.05 | Create `k8s/services/keycloak.nix` (StatefulSet) | P0 | M | T2.4.04, T1.1.02 | TBD | ⏳ |
| T2.4.06 | Create `images/nubus-ldap/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T2.4.07 | Define nubus-ldap image with security hardening | P0 | M | T2.4.06, T1.2.03 | TBD | ⏳ |
| T2.4.08 | Build nubus-ldap image | P0 | M | T2.4.07 | TBD | ⏳ |
| T2.4.09 | Test nubus-ldap image | P0 | M | T2.4.08 | TBD | ⏳ |
| T2.4.10 | Create `k8s/services/nubus-ldap.nix` (StatefulSet) | P0 | M | T2.4.09, T1.1.02 | TBD | ⏳ |
| T2.4.11 | Create `images/nubus-udm/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.4.12 | Create `images/nubus-provisioning/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.4.13 | Create `images/nubus-portal/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |

### Wave 2.5: Environment Configurations

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.5.01 | Create `k8s/environments/production/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.5.02 | Create `k8s/environments/demo/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |
| T2.5.03 | Create `k8s/environments/local/default.nix` | P0 | M | Phase 1 | TBD | ⏳ |

### Wave 2.6: Integration Testing

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T2.6.01 | Test SOGo 5 + MariaDB integration | P0 | L | Wave 2.1, Wave 2.3 | TBD | ⏳ |
| T2.6.02 | Test SOGo 6 + PostgreSQL integration | P0 | L | Wave 2.1, Wave 2.3 | TBD | ⏳ |
| T2.6.03 | Test Keycloak + nubus-ldap integration | P0 | L | Wave 2.4 | TBD | ⏳ |
| T2.6.04 | Test all core services together | P0 | XL | Wave 2.1-2.5 | TBD | ⏳ |

---

## Phase 3: LMS Services (Week 5-6)

### Wave 3.1: ILIAS

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T3.1.01 | Create `images/ilias/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T3.1.02 | Define ILIAS image (Shibboleth + PHP 8.2 + Apache) | P0 | L | T3.1.01 | TBD | ⏳ |
| T3.1.03 | Build ILIAS image | P0 | XL | T3.1.02 | TBD | ⏳ |
| T3.1.04 | Test ILIAS image | P0 | L | T3.1.03 | TBD | ⏳ |
| T3.1.05 | Create `k8s/services/ilias.nix` | P0 | L | T3.1.04, T1.1.02 | TBD | ⏳ |
| T3.1.06 | Generate ILIAS K8s manifests | P0 | M | T3.1.05 | TBD | ⏳ |

### Wave 3.2: Moodle

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T3.2.01 | Create `images/moodle/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T3.2.02 | Define Moodle image (Shibboleth) | P0 | L | T3.2.01 | TBD | ⏳ |
| T3.2.03 | Build Moodle image | P0 | XL | T3.2.02 | TBD | ⏳ |
| T3.2.04 | Test Moodle image | P0 | L | T3.2.03 | TBD | ⏳ |
| T3.2.05 | Create `k8s/services/moodle.nix` | P0 | L | T3.2.04, T1.1.02 | TBD | ⏳ |
| T3.2.06 | Generate Moodle K8s manifests | P0 | M | T3.2.05 | TBD | ⏳ |

### Wave 3.3: JupyterHub

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T3.3.01 | Create `images/jupyterhub/default.nix` | P0 | L | Phase 1 | TBD | ⏳ |
| T3.3.02 | Define JupyterHub image | P0 | L | T3.3.01 | TBD | ⏳ |
| T3.3.03 | Build JupyterHub image | P0 | XL | T3.3.02 | TBD | ⏳ |
| T3.3.04 | Test JupyterHub image | P0 | L | T3.3.03 | TBD | ⏳ |
| T3.3.05 | Create `k8s/services/jupyterhub.nix` | P0 | L | T3.3.04, T1.1.02 | TBD | ⏳ |

### Wave 3.4: LMS Integration Testing

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T3.4.01 | Test ILIAS database integration | P0 | L | Wave 3.1, Phase 2 | TBD | ⏳ |
| T3.4.02 | Test Moodle database integration | P0 | L | Wave 3.2, Phase 2 | TBD | ⏳ |
| T3.4.03 | Test JupyterHub database integration | P0 | L | Wave 3.3, Phase 2 | TBD | ⏳ |
| T3.4.04 | Test SAML/OIDC authentication | P0 | XL | Wave 3.1-3.3, Phase 2 | TBD | ⏳ |

---

## Phase 4: Collaboration Services (Week 7-8)

All tasks follow the same pattern as previous phases. Key services:

- Nextcloud (StatefulSet)
- Collabora (Deployment)
- Element/Matrix (StatefulSet)
- Jitsi (StatefulSet)
- Etherpad (Deployment)
- OpenProject (Deployment)
- XWiki (Deployment)

---

## Phase 5: Utility Services (Week 9-10)

All utility services:

- Bookstack, Draw.io, Excalidraw, Planka
- Code Server, RStudio, ttyd, Slidev
- Zammad, LimeSurvey, TYPO3, Self-Service Password
- Dovecot, Crypto, Open-XChange
- ClamAV, SeaweedFS, MinIO

---

## Phase 6: Validation (Week 11-12)

### Wave 6.1: SBOM Generation

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T6.1.01 | Generate SBOMs for all images | P0 | XL | All phases | TBD | ⏳ |
| T6.1.02 | Validate SBOM format compliance | P0 | L | T6.1.01 | TBD | ⏳ |
| T6.1.03 | Add openDesk-specific metadata to SBOMs | P0 | M | T6.1.02 | TBD | ⏳ |
| T6.1.04 | Store SBOMs in registry | P1 | M | T6.1.03 | TBD | ⏳ |

### Wave 6.2: Vulnerability Scanning

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T6.2.01 | Run Trivy scans on all images | P0 | XL | All phases | TBD | ⏳ |
| T6.2.02 | Fix CRITICAL vulnerabilities | P0 | XL | T6.2.01 | TBD | ⏳ |
| T6.2.03 | Fix HIGH vulnerabilities | P1 | XL | T6.2.02 | TBD | ⏳ |
| T6.2.04 | Document MEDIUM/LOW vulnerabilities | P2 | M | T6.2.03 | TBD | ⏳ |

### Wave 6.3: Image Signing

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T6.3.01 | Set up Cosign for image signing | P0 | M | All phases | TBD | ⏳ |
| T6.3.02 | Sign all images | P0 | L | T6.3.01 | TBD | ⏳ |
| T6.3.03 | Verify image signatures | P0 | M | T6.3.02 | TBD | ⏳ |
| T6.3.04 | Document signing process | P1 | S | T6.3.03 | TBD | ⏳ |

### Wave 6.4: Documentation

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T6.4.01 | Complete README.md | P0 | M | All phases | TBD | ⏳ |
| T6.4.02 | Complete ARCHITECTURE.md | P0 | L | All phases | TBD | ⏳ |
| T6.4.03 | Complete BUILDING.md | P0 | L | All phases | TBD | ⏳ |
| T6.4.04 | Complete DEPLOYING.md | P0 | L | All phases | TBD | ⏳ |
| T6.4.05 | Complete SECURITY.md | P0 | L | All phases | TBD | ⏳ |
| T6.4.06 | Complete MIGRATION.md | P0 | XL | All phases | TBD | ⏳ |
| T6.4.07 | Update opendesk-edu documentation | P0 | L | T6.4.01-T6.4.06 | TBD | ⏳ |

### Wave 6.5: Performance Testing

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T6.5.01 | Measure build times for all services | P0 | XL | All phases | TBD | ⏳ |
| T6.5.02 | Identify slow builds | P0 | M | T6.5.01 | TBD | ⏳ |
| T6.5.03 | Optimize slow builds | P1 | L | T6.5.02 | TBD | ⏳ |
| T6.5.04 | Set up Nix caching | P1 | M | None | TBD | ⏳ |
| T6.5.05 | Measure deployment times | P1 | L | All phases | TBD | ⏳ |

---

## Phase 7: Production Rollout (Week 13-14)

### Wave 7.1: Staging Deployment

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T7.1.01 | Deploy core services to staging | P0 | XL | Phase 6 | TBD | ⏳ |
| T7.1.02 | Deploy LMS services to staging | P0 | XL | T7.1.01 | TBD | ⏳ |
| T7.1.03 | Deploy collaboration services to staging | P0 | XL | T7.1.02 | TBD | ⏳ |
| T7.1.04 | Deploy utility services to staging | P0 | XL | T7.1.03 | TBD | ⏳ |
| T7.1.05 | Run integration tests on staging | P0 | XL | T7.1.04 | TBD | ⏳ |

### Wave 7.2: Production Deployment

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T7.2.01 | Backup existing production data | P0 | XL | T7.1.05 | TBD | ⏳ |
| T7.2.02 | Deploy core services to production | P0 | XXL | T7.1.05 | TBD | ⏳ |
| T7.2.03 | Monitor production deployment | P0 | XL | T7.2.02 | TBD | ⏳ |
| T7.2.04 | Address production issues | P0 | XL | T7.2.03 | TBD | ⏳ |
| T7.2.05 | Deploy remaining services incrementally | P1 | XXL | T7.2.04 | TBD | ⏳ |

---

## Phase 8: Helmfile Deprecation (Week 15+)

### Wave 8.1: Monitoring

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T8.1.01 | Monitor Nix-based deployments | P0 | Ongoing | Phase 7 | TBD | ⏳ |
| T8.1.02 | Collect metrics on build times | P1 | Ongoing | Phase 7 | TBD | ⏳ |
| T8.1.03 | Collect user feedback | P1 | Ongoing | Phase 7 | TBD | ⏳ |
| T8.1.04 | Address reported issues | P0 | Ongoing | T8.1.01 | TBD | ⏳ |

### Wave 8.2: Migration Completion

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T8.2.01 | Migrate any remaining services | P1 | XL | Phase 7 | TBD | ⏳ |
| T8.2.02 | Archive `opendesk-edu/nix/` | P1 | S | T8.2.01 | TBD | ⏳ |
| T8.2.03 | Update all documentation to remove Helmfile references | P1 | L | T8.2.01 | TBD | ⏳ |
| T8.2.04 | Mark Helmfile as deprecated in `opendesk-edu/` | P1 | S | T8.2.03 | TBD | ⏳ |

### Wave 8.3: Final Validation

| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T8.3.01 | Verify all acceptance criteria are met | P0 | XL | Phase 8 | TBD | ⏳ |
| T8.3.02 | Run final security audit | P0 | L | T8.3.01 | TBD | ⏳ |
| T8.3.03 | Run final performance tests | P0 | L | T8.3.01 | TBD | ⏳ |
| T8.3.04 | Generate final project report | P1 | M | T8.3.03 | TBD | ⏳ |
| T8.3.05 | Conduct team retrospective | P1 | M | T8.3.04 | TBD | ⏳ |

---

## Task Summary

### By Phase

| Phase | Tasks | Effort | Duration |
|-------|-------|--------|----------|
| Phase 0 | 11 | ~80h | 1 week |
| Phase 1 | 40 | ~320h | 2 weeks |
| Phase 2 | 40 | ~320h | 2 weeks |
| Phase 3 | 16 | ~128h | 2 weeks |
| Phase 4 | 24 | ~192h | 2 weeks |
| Phase 5 | 25 | ~200h | 2 weeks |
| Phase 6 | 24 | ~192h | 2 weeks |
| Phase 7 | 10 | ~520h | 2 weeks |
| Phase 8 | 13 | ~104h | 2+ weeks |
| **Total** | **203** | **~1956h** | **15+ weeks** |

### By Priority

| Priority | Count | % of Total |
|----------|-------|-------------|
| P0 (Critical) | 84 | 41% |
| P1 (High) | 72 | 35% |
| P2 (Medium) | 32 | 16% |
| P3 (Low) | 15 | 7% |

### By Effort

| Effort | Count | Total Hours |
|--------|-------|-------------|
| S (<4h) | 41 | 82h |
| M (4-8h) | 84 | 486h |
| L (8-16h) | 57 | 684h |
| XL (16-32h) | 18 | 408h |
| XXL (32+h) | 3 | 696h |

---

## Parallelization Strategy

### Independent Waves

These waves can be executed in parallel:

- **Phase 1:** Wave 1.1-1.5, Wave 1.6-1.9
- **Phase 2:** Wave 2.1-2.2, Wave 2.3-2.4, Wave 2.5-2.6
- **Phase 3:** Wave 3.1-3.3, Wave 3.4
- **Phase 4:** All waves can be parallelized
- **Phase 5:** All waves can be parallelized
- **Phase 6:** Wave 6.1-6.3 can be parallelized, Wave 6.4-6.5 sequential
- **Phase 7-8:** Mostly sequential

### Team Allocation

With a team of 2-3 developers:
- **2 developers:** Can work on 2 independent waves in parallel
- **3 developers:** Can work on 2-3 independent waves in parallel

### Estimated Timeline with Parallelization

| Week | Phase | Waves (with 2 developers) | Notes |
|------|-------|----------------------------|-------|
| 0 | Phase 0 | All | Project setup |
| 1-2 | Phase 1 | 1.1-1.5 + 1.6-1.9 | Foundation |
| 3-4 | Phase 2 | (2.1-2.2) + (2.3-2.4) + 2.5-2.6 | Core services |
| 5-6 | Phase 3 | (3.1-3.3) + 3.4 | LMS services |
| 7-8 | Phase 4 | All waves | Collaboration services |
| 9-10 | Phase 5 | All waves | Utility services |
| 11-12 | Phase 6 | (6.1-6.3) + (6.4-6.5) | Validation |
| 13-14 | Phase 7 | Sequential | Production rollout |
| 15+ | Phase 8 | Sequential | Deprecation |

---

## Task Tracking

### Status Definitions

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| ⏳ Not Started | Task has not been started | Ready to be picked up |
| 🔄 In Progress | Task is actively being worked on | None (in progress) |
| ✅ Done | Task is complete and verified | None |
| ❌ Blocked | Task cannot be started due to dependencies or issues | Resolve blockers |
| 🚧 Needs Review | Task is complete but needs review | Review and approve/reject |

### Task Lifecycle

1. **Not Started → In Progress:** Developer picks up the task
2. **In Progress → Needs Review:** Developer completes the task and requests review
3. **Needs Review → Done:** Reviewer approves the task
4. **Needs Review → In Progress:** Reviewer rejects the task (with feedback)
5. **Any → Blocked:** Blocking issue is identified
6. **Blocked → In Progress/Not Started:** Blocking issue is resolved

---

## Quality Gates

Each phase has quality gates that must be passed before proceeding:

### Phase 0 Quality Gate

- [ ] Proposal approved by team
- [ ] Project tracking set up
- [ ] Repository structure created
- [ ] Basic CI/CD configured

### Phase 1 Quality Gate

- [ ] All libraries implemented and tested
- [ ] Flake structure working
- [ ] Directory structure in place
- [ ] CI/CD pipelines passing
- [ ] At least 2 services built successfully

### Phase 2 Quality Gate

- [ ] All core services migrated
- [ ] All core services tested
- [ ] Service integrations validated
- [ ] Environment configurations in place
- [ ] Integration tests passing

### Phase 3 Quality Gate

- [ ] All LMS services migrated
- [ ] All LMS services tested
- [ ] Authentication integration validated
- [ ] Performance acceptable

### Phase 4 Quality Gate

- [ ] All collaboration services migrated
- [ ] All collaboration services tested
- [ ] Storage configurations validated
- [ ] Service integrations working

### Phase 5 Quality Gate

- [ ] All utility services migrated
- [ ] All utility services tested
- [ ] Monitoring and logging configured
- [ ] Complete system integration tested

### Phase 6 Quality Gate

- [ ] All images have SBOMs
- [ ] No CRITICAL vulnerabilities
- [ ] All images signed
- [ ] Documentation complete
- [ ] Acceptance criteria validated

### Phase 7 Quality Gate

- [ ] Staging deployment successful
- [ ] Production deployment successful
- [ ] No critical issues in production
- [ ] Performance metrics acceptable

### Phase 8 Quality Gate

- [ ] All services migrated
- [ ] Helmfile deprecated
- [ ] All acceptance criteria met
- [ ] Team satisfied with results

---

## Notes

1. **Task IDs:** Follow the pattern `T<phase>.<wave>.<sequence>` for easy tracking
2. **Effort Estimates:** Are rough estimates and should be refined as we gain experience
3. **Dependencies:** Must be respected to avoid blocking
4. **Parallelization:** Independent tasks should be worked on in parallel where possible
5. **Quality Gates:** Each phase must pass its quality gate before the next phase begins
6. **Documentation:** All tasks that create new code or configuration should include documentation
7. **Testing:** All tasks that create new code or configuration should include tests

---

## Related Documents

- [Proposal Document](./proposal.md)
- [Delta Specifications](./specs.md)
- [Nix Integration Specification](../../specs/platform/nix-integration/index.md)
- [OpenSpec Methodology](../../METHODOLOGY.md)
