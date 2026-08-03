<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Change Proposal: Nix Integration for openDesk Edu

**⚠️ WORK IN PROGRESS - This change proposal is currently in DRAFT status**

## Quick Links

- 📋 [**Proposal**](proposal.md) - Motivation, goals, scope, impact assessment
- 📜 [**Delta Specs**](specs.md) - ADDED/MODIFIED/REMOVED specifications
- 🎯 [**Tasks**](tasks.md) - Actionable implementation tasks organized by phase

## Summary

This change proposes integrating **Nix-based build and deployment systems** into the openDesk Edu ecosystem to address critical issues with:

- ❌ Build irreproducibility
- ❌ Missing centralized SBOM generation
- ❌ Inconsistent security hardening
- ❌ Image version drift
- ❌ Manual dependency management
- ❌ No automated vulnerability scanning
- ❌ Complex deployment workflows

## What's Being Proposed

### New: opendesk-nix Repository

A unified Nix-based system for:

1. **🖥️ Image Building** - Reproducible container images for all 50+ services
2. **📝 K8s Manifest Generation** - Kubernetes resources from Nix expressions
3. **🔒 Security** - SBOM generation, vulnerability scanning, image signing
4. **🚀 Deployment** - Multi-environment, multi-registry support
5. **⚙️ CI/CD Integration** - GitHub Actions and GitLab CI workflows

### Migration Path

8 phases over **14-16 weeks**:

| Phase | Duration | Focus | Status |
|-------|----------|-------|--------|
| 0 | Week 0 | Preparation & Approval | ⏳ Draft |
| 1 | Week 1-2 | Foundation (libraries, structure) | ⏳ Not Started |
| 2 | Week 3-4 | Core Services (SOGo, DBs, Keycloak, Nubus) | ⏳ Not Started |
| 3 | Week 5-6 | LMS Services (ILIAS, Moodle, JupyterHub) | ⏳ Not Started |
| 4 | Week 7-8 | Collaboration Services (Nextcloud, Element, Jitsi, etc.) | ⏳ Not Started |
| 5 | Week 9-10 | Utility Services (all remaining services) | ⏳ Not Started |
| 6 | Week 11-12 | Validation (SBOM, scanning, signing, docs) | ⏳ Not Started |
| 7 | Week 13-14 | Production Rollout | ⏳ Not Started |
| 8 | Week 15+ | Helmfile Deprecation | ⏳ Not Started |

## Acceptance Criteria

**All of these MUST be met for the change to be considered successful:**

### Technical (10/10 required)

- [ ] ✅ All 50+ services can be built using Nix
- [ ] ✅ Nix-built images are identical to Docker-built images
- [ ] ✅ All images have SBOMs (CycloneDX + SPDX)
- [ ] ✅ All images pass vulnerability scans (no CRITICAL)
- [ ] ✅ All images are signed with Cosign
- [ ] ✅ All images run as non-root with proper security contexts
- [ ] ✅ Kubernetes manifests can be generated for all services
- [ ] ✅ Generated manifests are valid and deployable
- [ ] ✅ CI/CD pipelines work for all services
- [ ] ✅ Development shells provide all necessary tools

### Quality (5/5 required)

- [ ] ✅ Build success rate > 99%
- [ ] ✅ Average build time < 30 minutes
- [ ] ✅ All tests pass (unit, integration, e2e)
- [ ] ✅ Documentation is complete and accurate
- [ ] ✅ Migration guide enables smooth transition

### Business (5/5 required)

- [ ] ✅ Meets ZKI IT-Grundschutz compliance requirements
- [ ] ✅ Can be maintained by the openDesk Edu Team
- [ ] ✅ Scales to support future service additions
- [ ] ✅ Backward compatibility with Helmfile maintained
- [ ] ✅ No breaking changes to end-user experience

## How to Review

### For Technical Reviewers

1. **Read the [Proposal](proposal.md)** - Understand the motivation and goals
2. **Check the [Delta Specs](specs.md)** - See what will be added/modified/removed
3. **Review the [Tasks](tasks.md)** - Understand the implementation plan
4. **Validate the Architecture** - Does the design meet our requirements?
5. **Assess Risks** - Are the risks identified and mitigated?

### For Management Reviewers

1. **Read the Executive Summary** (first section of [Proposal](proposal.md))
2. **Review the Acceptance Criteria** - Do these align with business goals?
3. **Check the Timeline** - Is 14-16 weeks realistic?
4. **Assess Resource Requirements** - Do we have the capacity?
5. **Evaluate ROI** - Do the benefits justify the investment?

### For Security Reviewers

1. **Review [Security Requirements](proposal.md#security)**
2. **Check [Security Hardening](specs.md#added)** details
3. **Validate SBOM and Scanning plans**
4. **Assess Image Signing approach**
5. **Verify Compliance with ZKI IT-Grundschutz**

## Next Steps

### For Approval

This change requires approval from:

- [ ] Team Lead
- [ ] Architecture Lead
- [ ] Security Lead
- [ ] Operations Lead

**To approve:** Review the documents above and add your approval to the [Proposal](proposal.md#approval).

### For Implementation

Once approved:

1. **Set up project tracking** - Use the tasks from [tasks.md](tasks.md)
2. **Assign tasks** - Each task needs an assignee
3. **Begin Phase 0** - Preparation and setup
4. **Track progress** - Update task statuses regularly
5. **Pass quality gates** - Each phase has quality gates that must be passed

## Questions?

For questions about this change proposal:

1. **Check the documents** - Most questions are answered in the proposal, specs, or tasks
2. **Ask in Matrix** - `#opendesk-ce-public:matrix.openedusuite.example.com`
3. **Create an issue** - For formal questions or concerns
4. **Request a meeting** - For complex discussion

## See Also

- [OpenSpec Methodology](../../METHODOLOGY.md) - How we use OpenSpec
- [Nix Integration Specification](../../specs/platform/nix-integration/index.md) - Full technical specification
- [opendesk-nix Repository](https://github.com/openEduSuite/openEduSuite-public) - Target repository
- [Current Helmfile Deployments](https://github.com/openEduSuite/openEduSuite-public/tree/main/helmfile) - Existing system

---

**Last Updated:** 2026-08-28  
**Status:** 🟡 Draft / Awaiting Review
