<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Delta Specifications: Nix Integration

**Change ID:** nix-integration-001  
**Related Proposal:** [proposal.md](./proposal.md)  
**Status:** Draft  

This document defines the delta specifications (ADDED/MODIFIED/REMOVED) for the Nix integration change proposal.

---

## ADDED

### New Repository: opendesk-nix

- `opendesk-nix/` — New repository for Nix-based build and deployment
  - Purpose: Centralized location for all Nix configurations
  - Contains: Image definitions, K8s manifests, libraries, scripts, documentation

### Image Build System

- `opendesk-nix/flake.nix` — Root flake defining all packages and apps
  - Purpose: Entry point for the Nix build system
  - Spec: [Nix Integration Specification](../specs/platform/nix-integration/index.md#file-structure-specification)

- `opendesk-nix/images/<service>/default.nix` — Image definition for each service (50+ files)
  - Purpose: Define container images using Nix
  - Spec: [Image Configuration Schema](../specs/platform/nix-integration/index.md#image-configuration-schema)
  - Acceptance Criteria: AC-001, AC-002, AC-006

- `opendesk-nix/images/<service>/config/` — Service-specific configuration files
  - Purpose: Store configuration files for each service
  - Contains: `*.conf`, `*.sh`, `entrypoint.sh`, `healthcheck.sh`

### K8s Manifest Generation System

- `opendesk-nix/k8s/services/<service>.nix` — K8s resource definitions (50+ files)
  - Purpose: Generate Kubernetes manifests from Nix expressions
  - Spec: [Kubernetes Resource Schema](../specs/platform/nix-integration/index.md#kubernetes-resource-schema)
  - Acceptance Criteria: AC-007, AC-008

- `opendesk-nix/k8s/environments/<env>/` — Environment-specific configurations
  - Purpose: Define environment-specific overrides
  - Contains: `default.nix`, `kustomization.yaml`
  - Environments: `production`, `demo`, `local`
  - Spec: [Environment Configuration](../specs/platform/nix-integration/index.md#environment-configuration)

- `opendesk-nix/k8s/overlays/` — Configuration overlays
  - Purpose: Apply cross-cutting concerns to services
  - Contains: `monitoring.nix`, `logging.nix`, `storage.nix`, `networking.nix`

### Libraries

- `opendesk-nix/lib/k8s.nix` — K8s resource builders
  - Purpose: Provide reusable builders for K8s resources
  - Spec: [Kubernetes Resource Schema](../specs/platform/nix-integration/index.md#kubernetes-resource-schema)
  - Source: Migrated from `opendesk-edu/nix/lib/k8s.nix`

- `opendesk-nix/lib/security.nix` — Security hardening presets
  - Purpose: Define security profiles for different service types
  - Spec: [Security Hardening Presets](../specs/platform/nix-integration/index.md#security-hardening-presets)

- `opendesk-nix/lib/sbom.nix` — SBOM generation utilities
  - Purpose: Generate SBOMs for container images
  - Spec: [SBOM Generation Process](../specs/platform/nix-integration/index.md#s bom-generation-process)

- `opendesk-nix/lib/registry.nix` — Multi-registry support
  - Purpose: Manage pushing images to multiple registries
  - Spec: [Registry Configuration](../specs/platform/nix-integration/index.md#registry-configuration)

- `opendesk-nix/lib/types.nix` — Type definitions
  - Purpose: Define types for service configurations
  - Spec: [Image Build Interface](../specs/platform/nix-integration/index.md#image-build-interface)

- `opendesk-nix/lib/utils.nix` — Common utilities
  - Purpose: Store reusable utility functions

### Scripts

- `opendesk-nix/scripts/build-all-images.sh` — Build all images
  - Purpose: Build all container images in one command
  - Command: `nix build .#all-images`

- `opendesk-nix/scripts/build-single-image.sh` — Build a single image
  - Purpose: Build a specific container image
  - Command: `nix build .#<service>-image`

- `opendesk-nix/scripts/generate-k8s-manifests.sh` — Generate all K8s manifests
  - Purpose: Generate Kubernetes manifests for all services
  - Command: `nix build .#k8s-manifests`

- `opendesk-nix/scripts/deploy.sh` — Deploy to a cluster
  - Purpose: Deploy openDesk Edu to a Kubernetes cluster
  - Command: `nix run .#deploy-opendesk-edu -- --environment <env>`

- `opendesk-nix/scripts/push-images.sh` — Push images to registries
  - Purpose: Push container images to one or more registries
  - Command: `nix run .#push-images -- <service> --registry <registry>`

- `opendesk-nix/scripts/validate-manifests.sh` — Validate K8s manifests
  - Purpose: Validate generated Kubernetes manifests
  - Command: `nix run .#validate-manifests`

- `opendesk-nix/scripts/generate-sbom.sh` — Generate SBOMs
  - Purpose: Generate SBOMs for all images
  - Command: `nix run .#generate-sbom -- <service>`

### CI/CD

- `.github/workflows/build.yml` — GitHub Actions build workflow
  - Purpose: Build, test, and push images on GitHub
  - Spec: [GitHub Actions Workflow](../specs/platform/nix-integration/index.md#github-actions)

- `.github/workflows/test.yml` — GitHub Actions test workflow
  - Purpose: Run tests on all services

- `.github/workflows/push.yml` — GitHub Actions push workflow
  - Purpose: Push images to registries

- `.github/workflows/release.yml` — GitHub Actions release workflow
  - Purpose: Create releases with signed images

- `.gitlab-ci.yml` — GitLab CI configuration
  - Purpose: Build, test, and push images on GitLab
  - Spec: [GitLab CI Workflow](../specs/platform/nix-integration/index.md#gitlab-ci)

### Documentation

- `opendesk-nix/README.md` — Main readme
  - Purpose: Getting started guide for users
  - Spec: [Documentation Requirements](../specs/platform/nix-integration/index.md#documentation-requirements)

- `opendesk-nix/docs/ARCHITECTURE.md` — Architecture overview
  - Purpose: Explain the architecture of the Nix-based system

- `opendesk-nix/docs/BUILDING.md` — Build instructions
  - Purpose: Guide users through building images

- `opendesk-nix/docs/DEPLOYING.md` — Deployment instructions
  - Purpose: Guide users through deploying openDesk Edu

- `opendesk-nix/docs/SECURITY.md` — Security practices
  - Purpose: Document security requirements and practices

- `opendesk-nix/docs/MIGRATION.md` — Migration guide
  - Purpose: Guide users through migrating from Helmfile to Nix

- `opendesk-nix/CONTRIBUTING.md` — Contribution guidelines
  - Purpose: Guide contributors on how to add new services

### Specifications

- `openEduSuite-spec/specs/platform/nix-integration/index.md` — Nix Integration Specification
  - Purpose: Complete technical specification for the Nix integration
  - Acceptance Criteria: All criteria defined in the specification

### Tests

- `opendesk-nix/tests/image-tests/<service>/test.nix` — Unit tests for each service image
  - Purpose: Test that images build correctly and meet requirements
  - Spec: [Unit Tests](../specs/platform/nix-integration/index.md#unit-tests)
  - Acceptance Criteria: AC-013

- `opendesk-nix/tests/k8s-tests/<service>/test.nix` — Integration tests for K8s manifests
  - Purpose: Test that K8s manifests are valid
  - Spec: [Integration Tests](../specs/platform/nix-integration/index.md#integration-tests)
  - Acceptance Criteria: AC-013

- `opendesk-nix/e2e/` — End-to-end tests
  - Purpose: Test complete deployment workflows
  - Spec: [End-to-End Tests](../specs/platform/nix-integration/index.md#end-to-end-tests)

---

## MODIFIED

### Existing Files

- `opendesk-edu/nix/lib/k8s.nix` — MOVE to `opendesk-nix/lib/k8s.nix`
  - Reason: Consolidate all Nix code in opendesk-nix
  - Changes: May be updated to match new requirements
  - Acceptance Criteria: AC-007, AC-008

### Documentation Updates

- `opendesk-edu/README.md` — Update to reference opendesk-nix
  - Section: Building, Deployment
  - Reason: Point users to the new Nix-based system
  - Acceptance Criteria: AC-014

- `opendesk-edu docs/` — Update all documentation
  - Reason: Reflect the new build and deployment process
  - Acceptance Criteria: AC-014

### Helmfile (Optional Modifications)

- `opendesk-edu/helmfile/charts/<service>/values.yaml.gotmpl` — Add support for Nix-built images
  - Reason: Allow Helmfile to pull Nix-built images
  - Change: Add or update `image.repository` and `image.tag` values
  - Acceptance Criteria: AC-004, AC-019

---

## REMOVED

### Deprecated Directories

- `opendesk-edu/nix/` — DEPRECATE in favor of `opendesk-nix/`
  - Reason: All Nix code moved to opendesk-nix
  - Timeline: After Phase 8 (Helmfile Deprecation)
  - Replacement: `opendesk-nix/`

### Old Build Scripts (Optional Removals)

- `opendesk-edu/scripts/build-*.sh` — DEPRECATE if replaced by Nix scripts
  - Reason: Nix provides better alternatives
  - Timeline: After corresponding Nix scripts are validated
  - Replacement: `opendesk-nix/scripts/*`

---

## Validation Mapping

Each change in this delta spec maps to one or more acceptance criteria from the proposal:

| Delta Spec | Acceptance Criteria | Specification Section |
|------------|---------------------|------------------------|
| `opendesk-nix/flake.nix` | AC-001, AC-002 | [Build System](#image-build-system) |
| `opendesk-nix/images/<service>/` | AC-001, AC-002, AC-006 | [Image Build System](#image-build-system) |
| `opendesk-nix/k8s/services/<service>.nix` | AC-007, AC-008 | [K8s Manifest Generation System](#k8s-manifest-generation-system) |
| `opendesk-nix/k8s/environments/<env>/` | AC-009 | [K8s Manifest Generation System](#k8s-manifest-generation-system) |
| `opendesk-nix/lib/k8s.nix` | AC-007, AC-008 | [Libraries](#libraries) |
| `opendesk-nix/lib/security.nix` | AC-006 | [Libraries](#libraries) |
| `opendesk-nix/lib/sbom.nix` | AC-003 | [Libraries](#libraries) |
| `opendesk-nix/lib/registry.nix` | AC-005 | [Libraries](#libraries) |
| `scripts/*` | AC-010 | [Scripts](#scripts) |
| `.github/workflows/*` | AC-009 | [CI/CD](#cicd) |
| `.gitlab-ci.yml` | AC-009 | [CI/CD](#cicd) |
| `tests/*` | AC-013 | [Tests](#tests) |
| `docs/*` | AC-014 | [Documentation](#documentation) |
| `opendesk-edu/nix/lib/k8s.nix` (MODIFIED) | AC-007, AC-008 | [Existing Files](#existing-files) |
| `opendesk-edu/nix/` (REMOVED) | AC-015 | [Deprecated Directories](#deprecated-directories) |

---

## Dependencies

The following delta specs must be processed in order:

1. ADD `opendesk-nix/` repository
2. ADD `opendesk-nix/lib/*` libraries
3. ADD `opendesk-nix/flake.nix`
4. ADD `opendesk-nix/images/<service>/` for each service
5. ADD `opendesk-nix/k8s/services/<service>.nix` for each service
6. MODIFY `opendesk-edu/nix/lib/k8s.nix` (move to opendesk-nix)
7. ADD `opendesk-nix/scripts/*`
8. ADD CI/CD configurations
9. ADD tests
10. ADD documentation
11. MODIFY existing documentation
12. REMOVE `opendesk-edu/nix/` (after validation)

---

## Rollback Plan

If the migration needs to be rolled back:

1. All changes to `opendesk-edu/` can be reverted individually
2. The `opendesk-nix/` repository can be archived without affecting production
3. Helmfile deployments will continue to work with Docker-built images
4. No breaking changes to production until Phase 7 (Production Rollout)

---

## Notes

- This delta spec follows the [OpenSpec Methodology](../../METHODOLOGY.md)
- Each change should be implemented in its own PR/MR
- Related changes can be grouped in a single PR/MR if they are part of the same phase
- All ADDED files should include proper SPDX license headers
- All MODIFIED files should maintain their existing license headers
