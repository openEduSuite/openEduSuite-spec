<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Change Proposal: Nix Integration for openEduSuite

**Status:** Draft  
**Created:** 2026-08-28  
**Authors:** openEduSuite Team  
**Change ID:** nix-integration-001  
**Priority:** High  
**Complexity:** High  
**Effort Estimate:** 14-16 weeks

---

## Abstract

This proposal describes the integration of Nix-based build and deployment systems into the openEduSuite ecosystem. The goal is to establish a unified, reproducible, and declarative approach to container image building and Kubernetes manifest generation, addressing the current issues with build reproducibility, security, and maintainability.

---

## Motivation

### Current Problems

The current openEduSuite deployment system has several critical issues:

1. **-build irreproducibility:** Builds vary across environments due to inconsistent dependencies and manual processes
2. **No centralized SBOM generation:** Security compliance requires manual SBOM generation for each service
3. **Inconsistent security hardening:** Security configurations vary between services, creating vulnerabilities
4. **Image version drift:** Different deployments use different versions of the same service
5. **Manual dependency management:** Dependencies are manually tracked and updated
6. **No automated vulnerability scanning:** Security scans are ad-hoc and not integrated into the build pipeline
7. **Complex deployment workflow:** Deployments require multiple manual steps across different tools

### Why This Matters

These issues directly impact:
- **Security:** Without reproducible builds and consistent hardening, we cannot guarantee the security of our deployments
- **Compliance:** SBOM generation is required for ZKI IT-Grundschutz compliance
- **Reliability:** Version drift and inconsistent configurations cause deployment failures
- **Maintainability:** Manual processes are error-prone and time-consuming
- **Scalability:** The current approach does not scale to 50+ services

### Why Nix?

Nix provides several key benefits:

1. **Reproducible builds:** Same inputs always produce the same outputs
2. **Declarative configuration:** All builds and deployments are defined in code
3. **Powerful caching:** Avoid rebuilding unchanged dependencies
4. **Multi-architecture support:** Build for amd64 and arm64 from the same configuration
5. **Integration with Docker/OCI:** Generate standard OCI-compliant images
6. **Strong dependency management:** All dependencies are explicitly declared and versioned
7. **Atomic rollbacks:** Easy to roll back to previous versions

---

## Goals

### Primary Goals

1. **G1:** Establish reproducible builds for all 50+ openDesk services
2. **G2:** Generate SBOMs for all container images automatically
3. **G3:** Apply consistent security hardening across all services
4. **G4:** Maintain backward compatibility with existing Helmfile deployments
5. **G5:** Provide a unified CI/CD pipeline for all services
6. **G6:** Enable multi-registry support (GitLab, GHCR, Zot)

### Secondary Goals

1. **G7:** Generate Kubernetes manifests from Nix expressions
2. **G8:** Support multiple environments (UDC, demo, local)
3. **G9:** Provide development shells with all necessary tools
4. **G10:** Enable gradual migration from Helmfile to Nix

### Non-Goals

1. **NG1:** Replace Helmfile entirely (coexistence required for transition)
2. **NG2:** Support non-Nix build environments
3. **NG3:** Modify the runtime behavior of services
4. **NG4:** Support on-the-fly image customization in production

---

## Scope

### In Scope

- Container image building for all 50+ openDesk services
- Nix flake-based build system
- SBOM generation (CycloneDX + SPDX)
- Vulnerability scanning integration (Trivy)
- Image signing (Cosign)
- Kubernetes manifest generation
- CI/CD pipeline integration (GitHub Actions, GitLab CI)
- Development environment setup
- Migration tools from Helmfile
- Documentation

### Out of Scope

- Replacing the runtime behavior of any service
- Supporting non-Nix build environments
- Modifying the openDesk architecture (only the build/deployment process)
- Direct Helm chart generation (focus on raw manifests + Kustomize)

---

## Impact Assessment

### Affected Components

| Component | Impact | Risk | Mitigation |
|-----------|--------|------|------------|
| opendesk-nix repository | Major | Low | Repository already exists, will be expanded |
| opendesk-edu/nix | Major | Low | Will be deprecated and migrated to opendesk-nix |
| Helmfile deployments | Medium | Medium | Maintain backward compatibility, gradual migration |
| Docker images | High | Medium | Ensure Nix-built images are identical to Docker-built ones |
| CI/CD pipelines | High | Medium | New pipelines will be added alongside existing ones |
| Documentation | Medium | Low | Update existing docs, add new Nix-specific docs |
| Development environment | Medium | Low | Provide Nix-based dev shells |

### Stakeholders

| Stakeholder | Impact | Communication Plan |
|-------------|--------|-------------------|
| openEduSuite Team | High | Team meetings, documentation, training |
| UDC Operations | Medium | Documentation, migration guide, support |
| Security Team | Medium | Security review, vulnerability scan results |
| End Users | Low | No direct impact (transparent change) |

---

## Proposed Solution

### Architecture Overview

The solution involves creating a unified build and deployment system based on Nix flakes:

```
┌─────────────────────────────────────────────────────────────────┐
│                     opendesk-nix Repository                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ IMAGE BUILD │  │ K8S GENER- │  │  DEPLOY-    │              │
│  │  SYSTEM     │  │  ATION      │  │  MENT       │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                 │                 │                     │
│         ▼                 ▼                 ▼                     │
│  ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ 50+ Image     │ │ K8s        │ │ Environ-   │            │
│  │ Definitions   │ │ Manifests   │ │ ments      │            │
│  └─────────────────┘ └─────────────┘ └─────────────┘            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ lib/ - Reusable Libraries                                  ││
│  │   ├─ k8s.nix       (resource builders)                       ││
│  │   ├─ security.nix  (hardening presets)                       ││
│  │   ├─ sbom.nix      (SBOM generation)                         ││
│  │   └─ registry.nix  (multi-registry support)                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   ┌──────────┐           ┌──────────┐           ┌──────────┐
   │ Docker   │           │ YAML     │           │ kubectl  │
   │ Images   │           │ Manifests│           │ apply    │
   └──────────┘           └──────────┘           └──────────┘
```

### File Structure

```
opendesk-nix/
├── flake.nix                           # Root flake (entry point)
├── images/                             # 50+ service image definitions
│   ├── sogo5/
│   │   ├── default.nix
│   │   └── config/
│   ├── sogo6/
│   ├── ilias/
│   ├── moodle/
│   └── ...
├── k8s/                                # K8s manifest generation
│   ├── services/
│   │   ├── sogo5.nix
│   │   └── ...
│   └── environments/
│       ├── production/
│       └── demo/
├── lib/                                # Reusable libraries
│   ├── k8s.nix
│   ├── security.nix
│   ├── sbom.nix
│   └── registry.nix
└── scripts/                            # Utility scripts
    └── deploy.sh
```

### Migration Phases

The migration will happen in 8 phases over 14-16 weeks:

#### Phase 0: Preparation (Current - Week 0)

- [x] Create opendesk-nix repository
- [x] Define OpenSpec (THIS DOCUMENT)
- [ ] Review and approve proposal
- [ ] Set up initial repository structure
- [ ] Configure CI/CD pipelines

**Duration:** 1 week
**Deliverables:** 
- Approved proposal
- Initial repository structure
- Basic CI/CD setup

#### Phase 1: Foundation (Week 1-2)

- [ ] Move `opendesk-edu/nix/lib/k8s.nix` to `opendesk-nix/lib/k8s.nix`
- [ ] Create type definitions in `opendesk-nix/lib/types.nix`
- [ ] Implement security library (`lib/security.nix`)
- [ ] Implement SBOM library (`lib/sbom.nix`)
- [ ] Implement registry library (`lib/registry.nix`)
- [ ] Update `opendesk-nix/flake.nix` with new structure
- [ ] Create directory structure for all services
- [ ] Test build system with existing images

**Duration:** 2 weeks
**Deliverables:**
- Complete library set
- Working flake structure
- Tested with 2-3 existing services

#### Phase 2: Core Services (Week 3-4)

- [ ] Migrate SOGo 5/6 images and K8s manifests
- [ ] Migrate MariaDB, PostgreSQL, Redis, Memcached
- [ ] Migrate Keycloak and Nubus services (portal, ldap, udm, provisioning)
- [ ] Test all core services in isolation
- [ ] Test service interconnections

**Duration:** 2 weeks
**Deliverables:**
- 10-12 services migrated
- Working core infrastructure
- Validated service interconnections

#### Phase 3: LMS Services (Week 5-6)

- [ ] Migrate ILIAS, Moodle, JupyterHub
- [ ] Create K8s manifests for LMS services
- [ ] Integrate with database services
- [ ] Test LMS deployments
- [ ] Validate SAML/OIDC integration

**Duration:** 2 weeks
**Deliverables:**
- LMS services fully migrated
- Working authentication integration
- Tested deployments

#### Phase 4: Collaboration Services (Week 7-8)

- [ ] Migrate Nextcloud, Collabora, Element, Jitsi
- [ ] Create K8s manifests for collaboration services
- [ ] Configure persistent storage
- [ ] Test service integrations
- [ ] Validate file sharing and synchronization

**Duration:** 2 weeks
**Deliverables:**
- Collaboration services fully migrated
- Working storage configurations
- Tested integrations

#### Phase 5: Utility Services (Week 9-10)

- [ ] Migrate all remaining utility services
- [ ] Create K8s manifests for all utility services
- [ ] Configure monitoring stack (kube-prometheus-stack)
- [ ] Configure logging stack (EFK + Loki)
- [ ] Test all services together

**Duration:** 2 weeks
**Deliverables:**
- All utility services migrated
- Monitoring and logging configured
- Integrated testing

#### Phase 6: Validation (Week 11-12)

- [ ] Validate all images and manifests
- [ ] Generate SBOMs for all images
- [ ] Run vulnerability scans on all images
- [ ] Performance test deployments
- [ ] Write comprehensive documentation
- [ ] Create migration guide from Helmfile

**Duration:** 2 weeks
**Deliverables:**
- Complete documentation
- Migration guide
- Performance benchmarks
- Security validation

#### Phase 7: Production Rollout (Week 13-14)

- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Deploy to production (UDC)
- [ ] Monitor for issues
- [ ] Gather feedback
- [ ] Final adjustments

**Duration:** 2 weeks
**Deliverables:**
- Staging deployment
- Production deployment
- Issue resolution
- Performance metrics

#### Phase 8: Helmfile Deprecation (Week 15+)

- [ ] Monitor Nix-based deployments
- [ ] Address any issues
- [ ] Gradually migrate remaining services
- [ ] Deprecate `opendesk-edu/nix` repository
- [ ] Archive old Helmfile-based deployments
- [ ] Update documentation to point to Nix-based system

**Duration:** Ongoing
**Deliverables:**
- Full migration to Nix
- Archived old systems
- Updated documentation

---

## Acceptance Criteria

### Technical Criteria

1. **AC-001:** All 50+ services can be built using the Nix-based system
2. **AC-002:** Nix-built images are identical to Docker-built images (same tags, configurations)
3. **AC-003:** All images have SBOMs generated (CycloneDX + SPDX)
4. **AC-004:** All images pass vulnerability scans with no CRITICAL vulnerabilities
5. **AC-005:** All images are signed with Cosign
6. **AC-006:** All images run as non-root users with proper security contexts
7. **AC-007:** Kubernetes manifests can be generated for all services
8. **AC-008:** Generated manifests are valid and can be applied to a cluster
9. **AC-009:** CI/CD pipelines successfully build, test, and deploy all services
10. **AC-010:** Development shells provide all necessary tools

### Quality Criteria

1. **AC-011:** Build success rate > 99%
2. **AC-012:** Average build time < 30 minutes per service
3. **AC-013:** All tests pass (unit, integration, e2e)
4. **AC-014:** Documentation is complete and accurate
5. **AC-015:** Migration guide enables smooth transition from Helmfile

### Business Criteria

1. **AC-016:** System meets ZKI IT-Grundschutz compliance requirements
2. **AC-017:** System can be maintained by the openEduSuite Team
3. **AC-018:** System scales to support future service additions
4. **AC-019:** Backward compatibility with Helmfile is maintained
5. **AC-020:** No breaking changes to end-user experience

---

## Risks and Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Build times are too long | Medium | High | Optimize builds, use caching, parallelize |
| Nix learning curve is steep | High | Medium | Provide training, documentation, examples |
| Incompatibility with existing Dockerfiles | Medium | High | Maintain backward compatibility, test thoroughly |
| Security scans fail builds | Low | High | Fix vulnerabilities before migration, whitelist false positives |
| SBOM generation is incomplete | Medium | Medium | Validate SBOMs, add custom metadata |
| K8s manifest generation has bugs | Medium | Medium | Test manifests thoroughly, validate against schema |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Team resistance to new tools | Medium | Medium | Demonstrate benefits, provide training, gradual adoption |
| CI/CD pipeline failures | Medium | High | Monitor pipelines, set up alerts, provide rollback options |
| Registry rate limits | Low | Medium | Use multiple registries, implement caching, respect rate limits |
| Nix Configuration Drift | Medium | Medium | Regular sync between team members, shared flake.lock |

### Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Service downtime during migration | Low | High | Test in staging, use blue-green deployments |
| Data loss during migration | Low | Critical | Backup all data before migration, test restore |
| Rollback is needed | Medium | High | Maintain old Helmfile deployments until Nix is validated |
| Helmfile and Nix deployments conflict | Medium | Medium | Use different namespaces for testing, coordinate deployments |

---

## Dependencies

### Technical Dependencies

1. **D1:** Nix package manager (v2.18+)
2. **D2:** Docker (v20.10+)
3. **D3:** kubectl (v1.28+)
4. **D4:** GitHub Actions runners with Nix support
5. **D5:** GitLab CI runners with Nix support
6. **D6:** Container registries (GitLab, GHCR)
7. **D7:** Vulnerability scanning tools (Trivy)
8. **D8:** SBOM generation tools (Syft)
9. **D9:** Image signing tools (Cosign)

### Resource Dependencies

1. **D10:** Team time for development and testing (estimated 320-400 hours)
2. **D11:** CI/CD infrastructure (GitHub Actions, GitLab CI)
3. **D12:** Registry storage (estimated 50-100 GB for all images)
4. **D13:** Nix cache storage (estimated 50-100 GB)

### External Dependencies

1. **D14:** Access to GitHub Container Registry (GHCR)
2. **D15:** Access to GitLab Container Registry (GitLab opencode.de)
3. **D16:** Access to UDC Kubernetes cluster for testing
4. **D17:** Access to Zot registry for local testing

---

## Success Metrics

### Quantitative Metrics

| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| Build success rate | > 99% | TBD | CI/CD pipelines |
| Average build time | < 30 min | TBD | CI/CD pipelines |
| Number of services migrated | 50+ | 6 | Repository |
| Number of vulnerabilities | 0 CRITICAL | TBD | Trivy scans |
| SBOM coverage | 100% | 0% | Repository |
| Image signatures | 100% | 0% | Registry |
| Documentation coverage | 100% | 0% | Repository |
| Test coverage | > 80% | 0% | Test suite |

### Qualitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Team satisfaction | > 4/5 | Survey |
| Ease of use | > 4/5 | Survey |
| Documentation quality | > 4/5 | Survey |
| Migration smoothness | > 4/5 | Retrospective |

---

## Open Questions

1. **Q1:** Should we maintain both `opendesk-nix` and `opendesk-edu/nix` during the transition, or fully migrate to `opendesk-nix`?
   - **Proposed:** Fully migrate to `opendesk-nix` and deprecate `opendesk-edu/nix`

2. **Q2:** How should we handle services that require custom build steps not easily expressible in Nix?
   - **Proposed:** Use `dockerTools.buildLayeredImage` with custom build steps, or keep Dockerfiles for complex cases

3. **Q3:** Should we use a single flake for all services, or multiple flakes (one per service)?
   - **Proposed:** Single flake for all services to enable cross-service dependencies and coordination

4. **Q4:** How should we handle environment-specific configurations (UDC vs. demo vs. local)?
   - **Proposed:** Use Nix overlays for environment-specific configurations

5. **Q5:** Should we generate Helm charts from Nix, or just raw manifests?
   - **Proposed:** Focus on raw manifests + Kustomize; Helm chart generation can be added later if needed

6. **Q6:** How should we version the images and manifests?
   - **Proposed:** Use semantic versioning for images, git commits for manifests

7. **Q7:** Should we use NixOS modules for service configuration?
   - **Proposed:** Yes, for better type checking and validation

---

## Next Steps

1. **NS-001:** Review this proposal with the openEduSuite Team
2. **NS-002:** Address feedback and refine the proposal
3. **NS-003:** Set up project tracking (issues, milestones, etc.)
4. **NS-004:** Begin Phase 1: Foundation
5. **NS-005:** Regular status updates and retrospectives

---

## Approval

### Approvers

| Name | Role | Approval | Date | Comments |
|------|------|----------|------|----------|
| | Team Lead | ⏳ Pending | | |
| | Architecture Lead | ⏳ Pending | | |
| | Security Lead | ⏳ Pending | | |
| | Operations Lead | ⏳ Pending | | |

### Decision

**Status:** ⏳ Pending Approval  
**Decision Date:**  
**Decision:**  

---

## References

1. [Nix Manual](https://nixos.org/manual/nix/stable/)
2. [Nix Flakes](https://nixos.wiki/wiki/Flakes)
3. [OpenSpec Methodology](../METHODOLOGY.md)
4. [opendesk-nix Repository](https://github.com/openEduSuite/openEduSuite-public)
5. [opendesk-edu/nix](https://github.com/openEduSuite/openEduSuite-public/tree/main/nix)
6. [Current Helmfile Deployments](https://github.com/openEduSuite/openEduSuite-public/tree/main/helmfile)

---

## Appendix A: Service Priority List

See the [Nix Integration Specification](../specs/platform/nix-integration/index.md#service-catalog) for complete service list with priorities.

---

## Appendix B: Cost Estimate

### Time Estimate

| Phase | Duration | Team Members | Total Hours |
|-------|----------|---------------|-------------|
| Phase 0 | 1 week | 2 | 80 |
| Phase 1 | 2 weeks | 2 | 160 |
| Phase 2 | 2 weeks | 2 | 160 |
| Phase 3 | 2 weeks | 2 | 160 |
| Phase 4 | 2 weeks | 2 | 160 |
| Phase 5 | 2 weeks | 2 | 160 |
| Phase 6 | 2 weeks | 2 | 160 |
| Phase 7 | 2 weeks | 2 | 160 |
| Phase 8 | 2+ weeks | 1 | 80+ |
| **Total** | **15+ weeks** | **2 avg** | **1200+** |

### Resource Estimate

| Resource | Quantity | Cost |
|----------|----------|------|
| CI/CD Minutes (GitHub) | ~10,000/month | Included in plan |
| CI/CD Minutes (GitLab) | ~5,000/month | Included in plan |
| Registry Storage | 100 GB | ~$0/month (self-hosted) |
| Nix Cache Storage | 100 GB | ~$0/month (self-hosted) |
| **Total** | | **~$0/month** |

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Flake** | A Nix feature providing reproducible, declarative project definitions |
| **Derivation** | A Nix package definition describing how to build something |
| **Store Path** | A unique path in the Nix store where a derivation's output is stored |
| **Closure** | A set of store paths including all dependencies of a given store path |
| **OCI** | Open Container Initiative - standards for container formats and runtimes |
| **SBOM** | Software Bill of Materials - a machine-readable list of software components |
| **CycloneDX** | A lightweight SBOM standard designed for application security contexts |
| **SPDX** | Software Package Data Exchange - an open standard for SBOM information |

---

## Appendix D: Related Documents

- [Nix Integration Specification](../specs/platform/nix-integration/index.md)
- [OpenSpec Methodology](../METHODOLOGY.md)
- [openEduSuite Architecture](https://openedusuite.example.org/architecture)
- [ZKI IT-Grundschutz Requirements](https://www.zki.de/it-grundschutz)
