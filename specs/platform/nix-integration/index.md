<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Nix Integration Specification

**Status:** Draft v0.1.0  
**Last Updated:** 2026-08-28  
**Authors:** openDesk Edu Team  
**License:** Apache-2.0  
**Category:** Platform / Deployment Infrastructure

---

## Purpose

This specification defines the integration of Nix-based build and deployment systems into the openDesk Edu ecosystem. The goal is to establish a unified, reproducible, and declarative approach to container image building and Kubernetes manifest generation.

---

## Background

### Current State

openDesk Edu currently uses:
- **Helmfile** for Kubernetes deployments
- **Docker** for container image builds
- **Multiple Dockerfiles** across repositories
- **Manual image pushing** to GitLab Container Registry
- **Custom scripts** for various deployment tasks

### Problems

1. **P1:** Builds are not reproducible across environments
2. **P2:** No centralized SBOM generation
3. **P3:** Security hardening is inconsistent
4. **P4:** Image versions drift across deployments
5. **P5:** Manual dependency management
6. **P6:** No automated vulnerability scanning in build pipeline

### Why Nix?

Nix provides:
- **R1:** Reproducible builds (same inputs = same outputs)
- **R2:** Declarative configuration (Nix expressions)
- **R3:**strong caching (avoid rebuilding unchanged dependencies)
- **R4:** Multi-architecture support (amd64, arm64)
- **R5:** Integration with existing Docker/OCI ecosystem
- **R6:** Automatic dependency management
- **R7:** Atomic rollbacks

---

## Scope

### In Scope

- Container image building for all 50+ openDesk services
- Kubernetes manifest generation from Nix expressions
- SBOM generation for all images
- Security scanning integration
- Multi-registry support (GitLab, GHCR, Zot)
- CI/CD pipeline integration (GitHub Actions, GitLab CI)
- Development environment setup
- Migration path from existing Dockerfiles/Helmfile

### Out of Scope

- Replacing Helmfile entirely (coexistence required for transition)
- Supporting non-Nix build environments
- Modifying the runtime behavior of services
- On-the-fly image customization in production

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     opendesk-nix Repository                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐ │
│  │   IMAGE BUILD   │   │ K8S GENERATION  │   │  DEPLOYMENT     │ │
│  │   SYSTEM        │   │  SYSTEM         │   │  SYSTEM         │ │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘ │
│           │                     │                     │          │
│           ▼                     ▼                     ▼          │
│  ┌─────────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│  │ images/sogo5.nix    │ │ k8s/sogo5.nix   │ │ environments/│ │
│  │ images/sogo6.nix    │ │ k8s/sogo6.nix   │ │   production/       │ │
│  │ images/ilias.nix    │ │ k8s/ilias.nix   │ │   demo/      │ │
│  │ ... (50+ services) │ │ ... (50+ svcs) │ │   local/     │ │
│  └─────────────────────┘ └─────────────────┘ └─────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    lib/                                 ││
│  │   ├─ k8s.nix            │ resource builders               ││
│  │   ├─ security.nix       │ hardening presets               ││
│  │   ├─ sbom.nix           │ SBOM generation                  ││
│  │   ├─ registry.nix       │ multi-registry support          ││
│  │   └─ utils.nix          │ common utilities                ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Docker   │        │ YAML     │        │ kubectl  │
   │ Images   │        │ Manifests│        │ apply    │
   └──────────┘        └──────────┘        └──────────┘
```

### Data Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Source  │───▶│ Nix Build│───▶│  Docker  │───▶│ Registry │
│  Files   │    │  System  │    │  Image   │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                        │
                                                        ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ K8s Specs│───▶│ Nix Eval │───▶│ Manifests│───▶│ Cluster  │
│ (Nix)    │    │          │    │ (YAML)   │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

---

## Requirements

### Functional Requirements

#### Build System

- **FR-BUILD-001:** The system SHALL build Docker images for all 50+ openDesk services
- **FR-BUILD-002:** The system SHALL use Nix flakes for reproducible builds
- **FR-BUILD-003:** The system SHALL support multi-architecture builds (amd64, arm64)
- **FR-BUILD-004:** The system SHALL generate OCI-compliant images
- **FR-BUILD-005:** The system SHALL support incremental builds with caching
- **FR-BUILD-006:** The system SHALL allow per-service customization
- **FR-BUILD-007:** The system SHALL maintain backward compatibility with existing Dockerfiles

#### Image Requirements

- **FR-IMAGE-001:** All images SHALL run as non-root users (UID != 0)
- **FR-IMAGE-002:** All images SHALL drop ALL Linux capabilities by default
- **FR-IMAGE-003:** All images SHALL only add explicitly required capabilities
- **FR-IMAGE-004:** All images SHALL have read-only root filesystems when possible
- **FR-IMAGE-005:** All images SHALL disable privilege escalation
- **FR-IMAGE-006:** All images SHALL use minimal base images (Alpine, Distroless)
- **FR-IMAGE-007:** All images SHALL include proper OCI labels
- **FR-IMAGE-008:** All images SHALL have health checks defined
- **FR-IMAGE-009:** All images SHALL set appropriate resource limits

#### Security

- **FR-SEC-001:** The system SHALL scan all images for vulnerabilities
- **FR-SEC-002:** The system SHALL generate SBOMs for all images (CycloneDX + SPDX)
- **FR-SEC-003:** The system SHALL sign all images with Cosign
- **FR-SEC-004:** The system SHALL support image verification
- **FR-SEC-005:** The system SHALL apply security hardening presets
- **FR-SEC-006:** The system SHALL support custom security profiles per service

#### Kubernetes Manifests

- **FR-K8S-001:** The system SHALL generate valid Kubernetes manifests
- **FR-K8S-002:** The system SHALL support Deployment, StatefulSet, DaemonSet, Job, CronJob
- **FR-K8S-003:** The system SHALL generate Services for all deployments
- **FR-K8S-004:** The system SHALL generate Ingress resources with TLS support
- **FR-K8S-005:** The system SHALL support ConfigMaps and Secrets
- **FR-K8S-006:** The system SHALL support HorizontalPodAutoscaler
- **FR-K8S-007:** The system SHALL support PodDisruptionBudget
- **FR-K8S-008:** The system SHALL support NetworkPolicies
- **FR-K8S-009:** The system SHALL support PersistentVolumeClaims
- **FR-K8S-010:** The system SHALL support cert-manager Certificate resources

#### Deployment

- **FR-DEPLOY-001:** The system SHALL support multiple environments (production, demo, local)
- **FR-DEPLOY-002:** The system SHALL support environment-specific overrides
- **FR-DEPLOY-003:** The system SHALL support multi-registry pushing
- **FR-DEPLOY-004:** The system SHALL maintain backward compatibility with Helmfile
- **FR-DEPLOY-005:** The system SHALL provide migration tools from Helmfile
- **FR-DEPLOY-006:** The system SHALL support gradual migration (hybrid deployments)

#### CI/CD

- **FR-CICD-001:** The system SHALL integrate with GitHub Actions
- **FR-CICD-002:** The system SHALL integrate with GitLab CI
- **FR-CICD-003:** The system SHALL trigger builds on code changes
- **FR-CICD-004:** The system SHALL trigger vulnerability scans on every build
- **FR-CICD-005:** The system SHALL push images to registries on release
- **FR-CICD-006:** The system SHALL support manual build triggers

#### Development

- **FR-DEV-001:** The system SHALL provide development shells with all necessary tools
- **FR-DEV-002:** The system SHALL support IDE integration
- **FR-DEV-003:** The system SHALL provide documentation for all services
- **FR-DEV-004:** The system SHALL support local development without full Nix installation

### Non-Functional Requirements

#### Performance

- **NFR-PERF-001:** Image builds SHALL complete within 30 minutes on standard CI runners
- **NFR-PERF-002:** Manifest generation SHALL complete within 5 minutes for all services
- **NFR-PERF-003:** The system SHALL cache intermediate build results to minimize rebuild times

#### Reliability

- **NFR-REL-001:** The system SHALL have a build success rate of >99%
- **NFR-REL-002:** The system SHALL automatically retry failed operations (max 3 times)
- **NFR-REL-003:** The system SHALL provide clear error messages for all failures

#### Maintainability

- **NFR-MAIN-001:** The system SHALL use consistent naming conventions
- **NFR-MAIN-002:** The system SHALL have comprehensive documentation
- **NFR-MAIN-003:** The system SHALL have automated tests
- **NFR-MAIN-004:** The system SHALL use type checking where possible (Nix types)

#### Portability

- **NFR-PORT-001:** The system SHALL support Linux (primary)
- **NFR-PORT-002:** The system SHALL support macOS (secondary)
- **NFR-PORT-003:** The system SHALL work with Docker Desktop
- **NFR-PORT-004:** The system SHALL work with Podman as an alternative to Docker

---

## File Structure Specification

### Repository Structure

```
opendesk-nix/
├── README.md                           # User-facing documentation
├── flake.nix                           # Root flake (entry point)
├── flake.lock                          # Lock file (auto-generated, DO NOT EDIT)
│
├── images/                             # Container image definitions
│   ├── <service>/
│   │   ├── default.nix                 # Image configuration
│   │   ├── Dockerfile                  # Optional: reference Dockerfile
│   │   └── config/                     # Service-specific configuration files
│   │       ├── *.conf
│   │       └── *.sh
│   └── ... (50+ service directories)
│
├── lib/                                # Reusable libraries
│   ├── k8s.nix                         # K8s resource builders
│   ├── security.nix                    # Security hardening presets
│   ├── sbom.nix                        # SBOM generation utilities
│   ├── registry.nix                    # Multi-registry support
│   ├── utils.nix                       # Common utilities
│   └── types.nix                       # Type definitions
│
├── k8s/                                # Kubernetes deployments
│   ├── services/                       # Per-service K8s definitions
│   │   ├── <service>.nix
│   │   └── ...
│   ├── environments/                   # Environment-specific configs
│   │   ├── <env>/
│   │   │   ├── default.nix
│   │   │   └── kustomization.yaml
│   │   └── ...
│   ├── overlays/                       # Configuration overlays
│   │   ├── monitoring.nix
│   │   ├── logging.nix
│   │   ├── storage.nix
│   │   └── networking.nix
│   └── kustomization.yaml              # Root kustomization
│
├── scripts/                            # Utility scripts
│   ├── build-all-images.sh
│   ├── build-single-image.sh
│   ├── generate-k8s-manifests.sh
│   ├── deploy.sh
│   ├── push-images.sh
│   ├── validate-manifests.sh
│   └── generate-sbom.sh
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BUILDING.md
│   ├── DEPLOYING.md
│   ├── SECURITY.md
│   └── MIGRATION.md
│
├── tests/
│   ├── image-tests/
│   │   └── <service>/
│   │       └── test.nix
│   └── k8s-tests/
│       └── <service>/
│           └── test.nix
│
├── .github/
│   └── workflows/
│       ├── build.yml
│       ├── test.yml
│       ├── push.yml
│       └── release.yml
│
└── .gitlab-ci.yml                     # GitLab CI configuration
```

### Service Directory Structure

Each service directory (`images/<service>/`) MUST contain:

```
images/<service>/
├── default.nix                    # REQUIRED: Image definition
├── Dockerfile                     # OPTIONAL: Reference Dockerfile for compatibility
├── config/                        # OPTIONAL: Configuration files
│   ├── app.conf
│   ├── entrypoint.sh
│   └── healthcheck.sh
└── README.md                      # OPTIONAL: Service-specific documentation
```

### Nix Module Interface

Each service's `default.nix` MUST export:

```nix
# images/<service>/default.nix
{ 
  lib,        # Library functions from lib/
  pkgs,       # Nixpkgs packages
  config ? {}, # Service-specific configuration
  ...         # Additional arguments
}:

let
  # Image definition
  image = lib.buildDockerImage {
    inherit config;
    # ... image build configuration
  };
  
  # K8s resource definitions
  k8s = import ../../k8s/services/<service>.nix {
    inherit lib pkgs image config;
  };

in {
  inherit image k8s;
  defaultPackage = image;
  defaultApp = k8s;
}
```

---

## Image Configuration Schema

### Required Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `name` | string | Service name | `"sogo6"` |
| `version` | string | Service version | `"6.0.0"` |
| `description` | string | Brief description | `"SOGo 6 Groupware Server"` |
| `fromImage` | string | Base image | `"sogo/sogo:6.0.0"` |
| `user` | int | Runtime UID | `1000` |
| `group` | int | Runtime GID | `1000` |
| `workDir` | path | Working directory | `"/var/lib/sogo"` |
| `expose` | list<int> | Exposed ports | `[ 20000 11211 ]` |
| `env` | attrs | Environment variables | `{ TZ = "Europe/Berlin"; }` |

### Optional Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag` | string | `version` | Image tag |
| `entrypoint` | list<string> | `[ "/bin/sh" ]` | Entrypoint command |
| `cmd` | list<string> | `[]` | Default command |
| `labels` | attrs | `{}` | Additional OCI labels |
| `capabilities` | { drop, add } | `{ drop = [ "ALL" ]; add = []; }` | Linux capabilities |
| `readOnlyRootFS` | bool | `true` | Read-only root filesystem |
| `allowPrivilegeEscalation` | bool | `false` | Allow privilege escalation |
| `generateSBOM` | bool | `true` | Generate SBOM |
| `sbomFormat` | list<enum> | `[ "CycloneDX-1.5" "SPDX-2.3" ]` | SBOM formats |
| `targetRegistries` | list<string> | `[ "gitlab.opencode.de/umr" "ghcr.io/opendesk-edu" ]` | Target registries |

### Standard Labels

All images MUST include the following OCI labels:

```nix
standardLabels = {
  maintainer = "openDesk Edu Team <team@openedusuite.example.org>";
  vendor = "openDesk Edu";
  license = "Apache-2.0";
  
  # OCI Standard
  "org.opencontainers.image.vendor" = "openDesk Edu";
  "org.opencontainers.image.license" = "Apache-2.0";
  "org.opencontainers.image.source" = "https://github.com/openEduSuite/openEduSuite-public";
  "org.opencontainers.image.title" = "<Service Name>";
  "org.opencontainers.image.description" = "<Service Description>";
  "org.opencontainers.image.version" = "<Version>";
  "org.opencontainers.image.architectures" = "amd64,arm64";
  "org.opencontainers.image.os" = "linux";
  
  # openDesk-specific
  "opendesk.org.component" = "<component-type>";
  "opendesk.org.version" = "<Version>";
  "opendesk.org.hardened" = "true";
  "opendesk.org.registry" = "registry.gitlab.opencode.de/umr";
  "opendesk.org.sbom.format" = "CycloneDX-1.5, SPDX-2.3";
  
  # ZKI IT-Grundschutz
  "de.zki.it-grundschutz.module" = "<module>";
  "de.zki.it-grundschutz.layer" = "<layer>";
  "de.zki.it-grundschutz.classification" = "internal";
  
  # container.gov.de
  "de.container.gov.component-id" = "opendesk-<service>";
  "de.container.gov.sbom-format" = "CycloneDX-1.5, SPDX-2.3";
  "de.container.gov.security-level" = "enhanced";
};
```

---

## Kubernetes Resource Schema

### Resource Types

The K8s library (`lib/k8s.nix`) MUST provide builders for:

```nix
lib = {
  # Workloads
  deployment -> attrs,
  statefulset -> attrs,
  daemonSet -> attrs,
  job -> attrs,
  cronJob -> attrs,
  
  # Services
  service -> attrs,
  headlessService -> attrs,
  
  # Networking
  ingress -> attrs,
  ingressWithCert -> attrs,
  networkPolicy -> attrs,
  
  # Config
  configMap -> attrs,
  secret -> attrs,
  
  # Storage
  pvc -> attrs,
  
  # Autoscaling
  hpa -> attrs,
  pdb -> attrs,
  
  # Security
  serviceAccount -> attrs,
  
  # cert-manager
  certificate -> attrs,
  
  # Utilities
  podSpec -> attrs,
  mkContainer -> attrs,
  mkVolume -> attrs,
  mkEnvFromSecret -> attrs,
  mkEnvFromConfigMap -> attrs,
  
  # Security
  securityContext -> attrs,
  tcpProbe -> attrs,
  httpProbe -> attrs,
  commandProbe -> attrs,
}
```

### Deployment Schema

```nix
lib.deployment {
  name = "sogo6";                    # REQUIRED: Deployment name
  image = sogo6-image;               # REQUIRED: Docker image
  tag = "6.0.0";                    # OPTIONAL: Image tag (default: "latest")
  port = 20000;                      # OPTIONAL: Container port
  ports = [ 20000 11211 ];           # OPTIONAL: List of ports
  replicas = 2;                      # OPTIONAL: Number of replicas (default: 1)
  env = [ { name = "TZ"; value = "Europe/Berlin"; } ];
  envFrom = [ mkEnvFromSecret { name = "sogo6-secrets"; } ];
  resources = {                      # OPTIONAL: Resource limits
    requests = { cpu = "1"; memory = "4Gi"; };
    limits = { cpu = "4"; memory = "8Gi"; };
  };
  probes = true;                     # OPTIONAL: Enable probes (default: true)
  probeType = "http";                # OPTIONAL: "http", "tcp", "command"
  probePath = "/SOGo";               # OPTIONAL: Health check path
  volumes = [ mkVolume { name = "data"; mountPath = "/var/lib/sogo"; } ];
  nodeSelector = { kubernetes.io/arch = "amd64"; };
  affinity = { ... };
  tolerations = [ { key = "node-role.kubernetes.io/control-plane"; operator = "Exists"; effect = "NoSchedule"; } ];
  priorityClassName = "opendesk-high-priority";
  securityContext = { runAsNonRoot = true; runAsUser = 1000; };
  serviceAccountName = "sogo6";
  imagePullSecrets = [ { name = "gitlab-registry-opencode"; } ];
}
```

---

## Service Catalog

### Priority 1: Core Infrastructure (Week 1-2)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| sogo5 | `sogo/sogo:5.8.0` | Deployment | ✅ Implemented | Groupware server |
| sogo6 | `sogo/sogo:6.0.0` | Deployment | ✅ Implemented | Groupware server with EDV |
| dev-agent | Custom | Deployment | ✅ Implemented | Self-healing operator |
| zot-registry | `zotregistry/zot:2.0.0-rc5` | Deployment | ✅ Implemented | OCI registry |
| sbom-generator | Custom | Job | ✅ Implemented | SBOM tools |
| website | Next.js | Deployment | ✅ Implemented | Marketing site |

### Priority 2: Database Services (Week 3-4)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| mariadb | `mariadb:11.4.4` | StatefulSet | ⏳ Todo | SQL database |
| postgresql | `postgres:17` | StatefulSet | ⏳ Todo | SQL database |
| redis | `redis:7` | StatefulSet | ⏳ Todo | Key-value store |
| memcached | `memcached:1.6` | Deployment | ⏳ Todo | Object cache |

### Priority 3: Identity & Authentication (Week 5)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| keycloak | `quay.io/keycloak/keycloak:24` | StatefulSet | ⏳ Todo | OIDC/SAML IdP |
| nubus-ldap | `osixia/openldap:1.5.0` | StatefulSet | ⏳ Todo | LDAP directory |
| nubus-udm | Custom | Deployment | ⏳ Todo | LDAP management |
| nubus-portal | Custom | Deployment | ⏳ Todo | Portal UI |
| nubus-provisioning | Custom | Deployment | ⏳ Todo | User provisioning |

### Priority 4: Learning Management Systems (Week 6-7)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| ilias | `ghcr.io/opendesk-edu/ilias-shibboleth:9-php8.2-apache` | Deployment | ⏳ Todo | LMS |
| moodle | `ghcr.io/opendesk-edu/moodle-shib:v1.4.0` | Deployment | ⏳ Todo | LMS |
| jupyterhub | `jupyterhub/jupyterhub:4.0.2` | Deployment | ⏳ Todo | Notebooks |

### Priority 5: Collaboration Services (Week 8-9)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| nextcloud | `nextcloud:29-apache` | StatefulSet | ⏳ Todo | File sync |
| collabora | `collabora/code:23.05.23.4.1` | Deployment | ⏳ Todo | Office suite |
| element | `matrixdotorg/synapse:v1.108.0` | StatefulSet | ⏳ Todo | Matrix server |
| jitsi | `jitsi/jicofo:stable-8644` | StatefulSet | ⏳ Todo | Video conferencing |
| etherpad | Custom | Deployment | ⏳ Todo | Collaborative editing |
| openproject | `openproject/community:13.0.3` | Deployment | ⏳ Todo | Project management |
| xwiki | `xwiki:lts-mysql-tomcat` | Deployment | ⏳ Todo | Wiki |

### Priority 6: Utility Services (Week 10-11)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| bookstack | `linuxserver/bookstack:v26.05.2-ls276` | Deployment | ⏳ Todo | Documentation |
| drawio | `jgraph/drawio:24.3.3` | Deployment | ⏳ Todo | Diagramming |
| excalidraw | `excalidraw/excalidraw:latest` | Deployment | ⏳ Todo | Whiteboarding |
| planka | `ghcr.io/plankanban/planka:latest` | Deployment | ⏳ Todo | Kanban board |
| code-server | `codercom/code-server:4.28.2` | Deployment | ⏳ Todo | VS Code web |
| rstudio | `rocker/rstudio:4.4.1` | Deployment | ⏳ Todo | RStudio web |
| ttyd | `tsl0922/ttyd:1.7.3` | Deployment | ⏳ Todo | Terminal sharing |
| slidev | `theasterism/slidev:0.47.5` | Deployment | ⏳ Todo | Presentation slides |

### Priority 7: Support Services (Week 12)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| zammad | `zammad/zammad:6.4.0` | Deployment | ⏳ Todo | Helpdesk |
| limesurvey | `limesurvey/limesurvey:6.4.12` | Deployment | ⏳ Todo | Surveys |
| typo3 | `typo3:12.4.18-apache` | Deployment | ⏳ Todo | CMS |
| self-service-password | `ltbproject/self-service-password:1.6.0` | Deployment | ⏳ Todo | Password reset |
| dovecot | `dovecot/dovecot:2.3.21` | StatefulSet | ⏳ Todo | IMAP server |
| open-xchange | Custom | StatefulSet | ⏳ Todo | Groupware |
| crypto | Custom | Deployment | ⏳ Todo | Encryption |

### Priority 8: Storage & Backup (Week 13)

| Service | Image Source | K8s Type | Status | Notes |
|---------|--------------|----------|--------|-------|
| minio | `minio/minio:RELEASE.2023-12-20T00-27-38Z` | StatefulSet | ⏳ Todo | Object storage |
| clamav | `clamav/clamav:1.2.0` | Deployment | ⏳ Todo | Antivirus |
| seaweedfs | `chrislusf/seaweedfs:3.60` | StatefulSet | ⏳ Todo | Distributed storage |

### Priority 9: Monitoring & Observability

| Service | Type | Status | Notes |
|---------|------|--------|-------|
| kube-prometheus-stack | Helm Chart | ⏳ Todo | Prometheus + Grafana |
| elasticsearch | StatefulSet | ⏳ Todo | Search/Analytics |
| filebeat | DaemonSet | ⏳ Todo | Log shipper |
| kibana | Deployment | ⏳ Todo | Log visualization |
| loki | StatefulSet | ⏳ Todo | Log aggregation |
| promtail | DaemonSet | ⏳ Todo | Log collector |

---

## Build Commands

### Building Images

```bash
# Build a single image
nix build .#sogo6-image

# Build all images
nix build .#all-images

# Build for specific architecture
nix build .#packages.x86_64-linux.sogo6-image
nix build .#packages.aarch64-linux.sogo6-image

# Build K8s manifests
nix build .#k8s-manifests

# Build and load into Docker
docker load < $(nix build .#sogo6-image)
```

### Development Shells

```bash
# Enter development shell with all tools
nix develop .#dev

# Enter CI shell (minimal tools)
nix develop .#ci

# Enter SBOM shell
nix develop .#sbom
```

### Development Commands

```bash
# Update all flake inputs
nix flake update

# Show available packages and apps
nix flake show

# Check flake metadata
nix flake metadata

# Garbage collect Nix store
nix-collect-garbage -d
```

### Deployment Commands

```bash
# Generate K8s manifests for all services
nix build .#k8s-manifests --out-link $PWD/manifests

# Apply all manifests
kubectl apply -f manifests/

# Deploy to specific environment
nix run .#deploy-opendesk-edu -- --environment production

# Push image to specific registry
nix run .#push-images -- sogo6 --registry gitlab

# Push all images to all registries
nix run .#push-images -- --all --all-registries
```

---

## Migration Path

### Phase 0: Preparation (Current)

- [x] Create opendesk-nix repository
- [x] Define OpenSpec
- [x] Implement core libraries
- [ ] Set up CI/CD pipelines
- [ ] Document migration process

### Phase 1: Foundation (Week 1-2)

- [ ] Move `opendesk-edu/nix/lib/k8s.nix` to `opendesk-nix/lib/k8s.nix`
- [ ] Create type definitions in `opendesk-nix/lib/types.nix`
- [ ] Implement security library in `opendesk-nix/lib/security.nix`
- [ ] Implement SBOM library in `opendesk-nix/lib/sbom.nix`
- [ ] Implement registry library in `opendesk-nix/lib/registry.nix`
- [ ] Update `opendesk-nix/flake.nix` with new structure
- [ ] Create directory structure for all services
- [ ] Test build system with existing images

### Phase 2: Core Services (Week 3-4)

- [ ] Migrate SOGo 5/6 images and K8s manifests
- [ ] Migrate MariaDB, PostgreSQL, Redis, Memcached
- [ ] Migrate Keycloak and Nubus services
- [ ] Test all core services in isolation
- [ ] Test service interconnections

### Phase 3: LMS Services (Week 5-6)

- [ ] Migrate ILIAS, Moodle, JupyterHub
- [ ] Create K8s manifests for LMS services
- [ ] Integrate with database services
- [ ] Test LMS deployments
- [ ] Validate SAML/OIDC integration

### Phase 4: Collaboration Services (Week 7-8)

- [ ] Migrate Nextcloud, Collabora, Element, Jitsi
- [ ] Create K8s manifests for collaboration services
- [ ] Configure persistent storage
- [ ] Test service integrations
- [ ] Validate file sharing and synchronization

### Phase 5: Utility Services (Week 9-10)

- [ ] Migrate all remaining utility services
- [ ] Create K8s manifests for all utility services
- [ ] Configure monitoring stack
- [ ] Configure logging stack
- [ ] Test all services together

### Phase 6: Validation (Week 11-12)

- [ ] Validate all images and manifests
- [ ] Generate SBOMs for all images
- [ ] Run vulnerability scans on all images
- [ ] Performance test deployments
- [ ] Write comprehensive documentation
- [ ] Create migration guide from Helmfile

### Phase 7: Production Rollout (Week 13-14)

- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Deploy to production (UDC)
- [ ] Monitor for issues
- [ ] Gather feedback
- [ ] Final adjustments

### Phase 8: Helmfile Deprecation (Week 15+)

- [ ] Monitor Nix-based deployments
- [ ] Address any issues
- [ ] Gradually migrate remaining services
- [ ] Deprecate `opendesk-edu/nix` repository
- [ ] Archive old Helmfile-based deployments
- [ ] Update documentation to point to Nix-based system

---

## Backward Compatibility

### Helmfile Integration

The new Nix-based system **MUST** maintain compatibility with existing Helmfile deployments:

1. **Image Compatibility**: Nix-built images MUST have the same tags and configurations as Docker-built images
2. **Registry Compatibility**: Nix-built images MUST be pushed to the same registries used by Helmfile
3. **K8s Compatibility**: Nix-generated manifests MUST be compatible with Helmfile-generated manifests

### Dual Deployment Support

During the transition period, the system SHALL support:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL DEPLOYMENT STRATEGIES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STRATEGY 1: Pure Nix                                              │
│  └─ nix run .#deploy-opendesk-edu -- --environment production            │
│                                                                  │
│  STRATEGY 2: Pure Helmfile                                         │
│  └─ helmfile -e production sync                                          │
│                                                                  │
│  STRATEGY 3: Nix Images + Helmfile                                 │
│  ├─ Build images with Nix: nix build .#all-images                  │
│  ├─ Push to registry: nix run .#push-images --all                 │
│  └─ Deploy with Helmfile: helmfile -e production sync                    │
│     (Helmfile pulls Nix-built images)                             │
│                                                                  │
│  STRATEGY 4: Nix Images + Nix Manifests                            │
│  ├─ Build images: nix build .#all-images                          │
│  ├─ Generate manifests: nix build .#k8s-manifests                 │
│  ├─ Push images: nix run .#push-images --all                      │
│  └─ Apply manifests: kubectl apply -f result/                     │
│                                                                  │
│  STRATEGY 5: Gradual Migration                                     │
│  ├─ Service A: Nix images + Helmfile                              │
│  ├─ Service B: Nix images + Nix manifests                          │
│  └─ Service C: Helmfile (unchanged)                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Migration Tools

The system SHALL provide tools to assist with migration:

```nix
# scripts/migrate-helmfile-to-nix.nix
{ lib, pkgs, ... }:

let
  # Parse existing Helmfile values and convert to Nix expressions
  migrateHelmfile = { helmfilePath }:
    # Implementation: parse helmfile and generate equivalent Nix
    ;

  # Generate Nix expressions from existing K8s manifests
  migrateManifests = { manifestPath }:
    # Implementation: parse YAML manifests and generate Nix
    ;

  # Validate that Nix-generated manifests match Helmfile-generated ones
  validateEquivalence = { helmfilePath, nixManifestPath }:
    # Implementation: compare the two deployments
    ;

in {
  inherit migrateHelmfile migrateManifests validateEquivalence;
}
```

---

## Security Requirements

### Image Hardening

All images MUST follow these security requirements:

```nix
# lib/security.nix
{ lib, ... }:

let
  profiles = {
    default = { drop = [ "ALL" ]; add = []; };
    database = { drop = [ "ALL" ]; add = [ "CHOWN" "SETGID" "SETUID" "DAC_OVERRIDE" ]; };
    web = { drop = [ "ALL" ]; add = [ "NET_BIND_SERVICE" ]; };
    file-processing = { drop = [ "ALL" ]; add = [ "CHOWN" "DAC_OVERRIDE" ]; };
    privileged = { drop = [ "NET_RAW" "SYS_ADMIN" ]; add = []; };
  };

  hardenedImage = config:
    config // {
      capabilities = profiles.default;
      readOnlyRootFS = true;
      allowPrivilegeEscalation = false;
      securityContext = {
        runAsNonRoot = true;
        runAsUser = 1000;
        runAsGroup = 1000;
      };
    };

in {
  inherit profiles hardenedImage;
}
```

### Vulnerability Scanning

- **SCAN-001:** All images SHALL be scanned with Trivy on every build
- **SCAN-002:** Scans SHALL fail the build if CRITICAL vulnerabilities are found
- **SCAN-003:** Scans SHALL warn if HIGH or MEDIUM vulnerabilities are found
- **SCAN-004:** Scan results SHALL be uploaded as build artifacts
- **SCAN-005:** Scan results SHALL be stored in a central database (optional)

### SBOM Generation

- **SBOM-001:** All images SHALL have SBOMs generated (CycloneDX + SPDX)
- **SBOM-002:** SBOMs SHALL be generated using Syft
- **SBOM-003:** SBOMs SHALL include all direct and transitive dependencies
- **SBOM-004:** SBOMs SHALL include openDesk-specific metadata
- **SBOM-005:** SBOMs SHALL be attached to images as OCI annotations
- **SBOM-006:** SBOMs SHALL be stored alongside images in registry

### Image Signing

- **SIGN-001:** All production images SHALL be signed with Cosign
- **SIGN-002:** Image signatures SHALL be verified before deployment
- **SIGN-003:** Signing SHALL use ephemeral keys for CI builds
- **SIGN-004:** Signing SHALL use persistent keys for release builds
- **SIGN-005:** Public keys SHALL be stored in Git repository

---

## Network Policies

All deployments SHALL include appropriate NetworkPolicies:

```nix
# k8s/overlays/networking.nix
{ lib, ... }:

let
  defaultDenyIngress = { name, namespace }:
    lib.networkPolicy {
      inherit name namespace;
      podSelector = {};
      policyTypes = [ "Ingress" ];
    };

  allowFromNamespace = { name, namespace, fromNamespace, ports }:
    lib.networkPolicy {
      inherit name namespace;
      podSelector = { matchLabels = { "app.kubernetes.io/name" = name; }; };
      policyTypes = [ "Ingress" ];
      ingress = [{
        from = [{ namespaceSelector = { matchLabels = { "kubernetes.io/metadata.name" = fromNamespace; }; }; }];
        ports = map (p: { protocol = "TCP"; port = p; }) ports;
      }];
    };

  allowFromSameNamespace = { name, namespace, ports }:
    allowFromNamespace { inherit name namespace; fromNamespace = namespace; ports = ports; };

in {
  inherit defaultDenyIngress allowFromNamespace allowFromSameNamespace;
}
```

---

## Storage Configuration

### Storage Classes

```nix
# k8s/overlays/storage.nix
{ lib, ... }:

let
  storageClasses = {
    production = {
      rwx = "ceph-cephfs-hdd-ec";      # For shared access (files, configs)
      rwo = "ceph-rbd-ssd";            # For exclusive access (databases)
    };
    demo = {
      rwx = "standard";
      rwo = "standard";
    };
    local = {
      rwx = "hostPath";
      rwo = "hostPath";
    };
  };

  pvcTemplate = { name, storageClass, accessModes, size }:
    lib.pvc {
      name = name;
      storageClassName = storageClass;
      accessModes = accessModes;
      storageSize = size;
    };

in {
  inherit storageClasses pvcTemplate;
}
```

---

## CI/CD Configuration

### GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      service:
        description: 'Service to build'
        required: false
      push:
        description: 'Push to registry'
        required: false
        default: false

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
    
    strategy:
      matrix:
        include:
          - service: sogo6
          - service: ilias
          - service: moodle
          - service: mariadb
          - service: keycloak
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Nix
        uses: cachix/install-nix-action@v22
        with:
          nix_path: nixpkgs=channel:nixos-unstable

      - name: Enable Flakes
        run: |
          mkdir -p ~/.config/nix
          echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

      - name: Build Image
        run: nix build .#${{ matrix.service }}-image

      - name: Load Docker Image
        run: docker load < result

      - name: Scan for Vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ matrix.service }}:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Generate SBOM
        run: nix run .#generate-sbom -- ${{ matrix.service }}

      - name: Login to GitLab Registry
        if: github.event_name != 'pull_request' && inputs.push == 'true'
        run: |
          echo "${{ secrets.GITLAB_OPENCODE_TOKEN }}" | \
          docker login registry.gitlab.opencode.de -u weiss --password-stdin

      - name: Push to GitLab
        if: github.event_name != 'pull_request' && inputs.push == 'true'
        run: nix run .#push-images -- ${{ matrix.service }} --registry gitlab

      - name: Login to GHCR
        if: github.event_name != 'pull_request' && inputs.push == 'true'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push to GHCR
        if: github.event_name != 'pull_request' && inputs.push == 'true'
        run: nix run .#push-images -- ${{ matrix.service }} --registry ghcr

      - name: Sign Images
        if: github.event_name != 'pull_request' && inputs.push == 'true'
        run: |
          cosign sign --yes registry.gitlab.opencode.de/umr/${{ matrix.service }}:latest
          cosign sign --yes ghcr.io/opendesk-edu/${{ matrix.service }}:latest
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - push

variables:
  NIX_CONFIG: "experimental-features = nix-command flakes"

cache:
  key: "nix-${{ runner.os }}"
  paths:
    - /nix
    - /root/.cache/nix

build:
  stage: build
  image: nixos/nix:latest
  script:
    - nix flake update
    - nix build .#all-images
  artifacts:
    paths:
      - result/
    expire_in: 1 week

test:
  stage: test
  image: nixos/nix:latest
  script:
    - docker load < result
    - nix run .#validate-manifests
    - nix-build tests/

push:gitlab:
  stage: push
  image: nixos/nix:latest
  script:
    - docker load < result
    - echo "$CI_JOB_TOKEN" | docker login registry.gitlab.com -u gitlab-ci-token --password-stdin
    - nix run .#push-images -- --registry gitlab --all
  rules:
    - if: $CI_COMMIT_REF_NAME == "main"
    - if: $CI_COMMIT_TAG =~ /^v/

push:ghcr:
  stage: push
  image: nixos/nix:latest
  script:
    - docker load < result
    - echo "$GHCR_TOKEN" | docker login ghcr.io -u $GHCR_USER --password-stdin
    - nix run .#push-images -- --registry ghcr --all
  rules:
    - if: $CI_COMMIT_REF_NAME == "main"
    - if: $CI_COMMIT_TAG =~ /^v/
```

---

## Registry Configuration

### Supported Registries

```nix
# lib/registry.nix
{ lib, ... }:

let
  registries = {
    gitlab-opencode = {
      url = "registry.gitlab.opencode.de/umr";
      authType = "token";
      username = "weiss";
      namespace = "umr";
    };
    ghcr = {
      url = "ghcr.io/opendesk-edu";
      authType = "token";
      username = "tobias-weiss-ai-xr";
      namespace = "opendesk-edu";
    };
    zot-local = {
      url = "172.17.209.143:5000";
      authType = "none";
      namespace = "opendesk-edu";
    };
  };

  tagImage = { image, registry, tag, digest }:
    "${registry.url}/${image.name}:${tag}";

  pushImage = { image, registry, tag, authToken }:
    # Returns shell command to push image to registry
    ''
      docker tag ${image.name}:${tag} ${tagImage { inherit image registry tag; }}
      ${optionalString (registry.authType == "token") ''
        echo "${authToken}" | docker login ${registry.url} -u ${registry.username} --password-stdin
      ''}
      docker push ${tagImage { inherit image registry tag; }}
    '';

  pushAll = { images, registry, authToken, tag }:
    builtins.concatStringsSep "\n" (map (image: pushImage { inherit image registry authToken tag; }) images);

in {
  inherit registries tagImage pushImage pushAll;
}
```

---

## Error Handling

### Build Errors

```nix
# lib/errors.nix
{ lib, ... }:

let
  errorTypes = {
    buildFailed = "BUILD_FAILED";
    imageNotFound = "IMAGE_NOT_FOUND";
    invalidConfig = "INVALID_CONFIG";
    registryPushFailed = "REGISTRY_PUSH_FAILED";
    vulnerabilityFound = "VULNERABILITY_FOUND";
    manifestValidationFailed = "MANIFEST_VALIDATION_FAILED";
    deploymentFailed = "DEPLOYMENT_FAILED";
  };

  handleBuildError = { error, context }:
    if builtins.elem errorTypes.buildFailed context.errorType then
      ''
        Build failed for ${context.service}:
        ${context.message}
        
        Check the build log for details.
        Run: nix build .#${context.service}-image -v
      ''
    else if builtins.elem errorTypes.imageNotFound context.errorType then
      ''
        Image not found: ${context.image}
        
        Ensure the base image exists and is accessible.
        Check Docker Hub or the specified registry.
      ''
    else if builtins.elem errorTypes.vulnerabilityFound context.errorType then
      ''
        Vulnerabilities found in ${context.service}:
        ${builtins.concatStringsSep "\n" context.vulnerabilities}
        
        Critical vulnerabilities MUST be fixed before deployment.
        High vulnerabilities SHOULD be fixed before deployment.
        
        Run: nix run .#scan-vulnerabilities -- ${context.service}
      ''
    else
      ''
        Error: ${error}
        Context: ${builtins.toJSON context}
      '';

in {
  inherit errorTypes handleBuildError;
}
```

---

## Testing Requirements

### Unit Tests

Each service directory SHOULD include unit tests:

```nix
# images/<service>/test.nix
{ pkgs, lib, ... }:

let
  serviceImage = import ./default.nix { inherit pkgs lib; };

in {
  imageBuildTest = pkgs.writeShellScriptTest {
    name = "${serviceImage.name}-image-build-test";
    script = ''
      # Test that the image can be built
      docker load < $serviceImage || { echo "Failed to load image"; exit 1; }
      
      # Test that the image has the expected labels
      IMAGE_ID=$(docker inspect --format='{{.Id}}' ${serviceImage.name}:latest || true)
      test -n "$IMAGE_ID" || { echo "Image not found"; exit 1; }
      
      docker inspect $IMAGE_ID | jq -e '.[] | .Config.Labels | has("org.opencontainers.image.version")' || exit 1
      docker inspect $IMAGE_ID | jq -e '.[] | .Config.Labels | has("org.opencontainers.image.title")' || exit 1
      
      # Test that user is non-root
      USER=$(docker inspect --format='{{.Config.User}}' $IMAGE_ID)
      test "$USER" != "root" && test "$USER" != "0" || { echo "Image runs as root"; exit 1; }
      
      echo "All ${serviceImage.name} image tests passed"
    '';
  };
  
  k8sManifestTest = pkgs.writeShellScriptTest {
    name = "${serviceImage.name}-k8s-manifest-test";
    script = ''
      # Test that manifests can be generated
      mkdir -p manifests
      cp -r ${serviceImage.k8s.manifests}/* manifests/ || true
      
      # Test that manifests are valid YAML
      for file in manifests/*.yaml; do
        test -f "$file" && yq e '.' "$file" > /dev/null || { echo "Invalid YAML: $file"; exit 1; }
      done
      
      echo "All ${serviceImage.name} K8s manifest tests passed"
    '';
  };
}
```

### Integration Tests

```nix
# tests/integration/sogo6-deployment.nix
{ pkgs, lib, ... }:

let
  sogo6 = import ../../images/sogo6/default.nix { inherit pkgs lib; };

in {
  deploymentTest = pkgs.writeShellScriptTest {
    name = "sogo6-deployment-integration-test";
    script = ''
      # Generate manifests
      mkdir -p manifests
      cp -r ${sogo6.k8s.manifests}/* manifests/ || true
      
      # Validate manifests
      for file in manifests/*.yaml; do
        test -f "$file" && yq e '.' "$file" > /dev/null || exit 1
      done
      
      # Check for required fields
      for file in manifests/deployment-*.yaml; do
        test -f "$file" || continue
        yq e '.apiVersion' "$file" > /dev/null || exit 1
        yq e '.kind' "$file" > /dev/null || exit 1
        yq e '.metadata' "$file" > /dev/null || exit 1
      done
      
      echo "SOGo 6 integration tests passed"
    '';
  };
}
```

---

## Documentation Requirements

### Required Documentation Files

| File | Location | Purpose |
|------|----------|---------|
| README.md | `opendesk-nix/` | Main readme for users |
| ARCHITECTURE.md | `opendesk-nix/docs/` | Architecture overview |
| BUILDING.md | `opendesk-nix/docs/` | Build instructions |
| DEPLOYING.md | `opendesk-nix/docs/` | Deployment instructions |
| SECURITY.md | `opendesk-nix/docs/` | Security practices and requirements |
| MIGRATION.md | `opendesk-nix/docs/` | Migration guide from Helmfile |
| CONTRIBUTING.md | `opendesk-nix/` | Contribution guidelines |

### Service Documentation

Each service directory SHOULD include:

```markdown
# <Service Name>

## Overview

<Brief description of the service>

## Purpose

<What problem this service solves>

## Architecture

<High-level architecture diagram>

## Configuration

### Required

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `DB_HOST` | string | - | Database host |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TZ` | string | `Europe/Berlin` | Timezone |

## Dependencies

- <Dependency 1>
- <Dependency 2>

## Ports

| Port | Protocol | Description |
|------|-----------|-------------|
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |

## Resources

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 512Mi |
| Storage | 1Gi | 10Gi |

## Security

### Capabilities

- Drops: `ALL`
- Adds: `NET_BIND_SERVICE`

### Permissions

- Run as UID 1000 (non-root)
- Run as GID 1000 (non-root)
- Read-only root filesystem
- No privilege escalation

## Deployment

```bash
# Build image
nix build .#<service>-image

# Push to registry
nix run .#push-images -- <service> --registry gitlab

# Deploy
kubectl apply -f k8s/services/<service>.yaml
```

## Troubleshooting

### Common Issues

#### Issue: <Problem description>

**Cause:** <Root cause>

**Solution:** <How to fix>

## References

- [Official documentation](<url>)
- [Source repository](<url>)
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Flake** | A Nix feature that provides reproducible, declarative project definitions |
| **Derivation** | A Nix package definition describing how to build something |
| **Store Path** | A unique path in the Nix store where a derivation's output is stored |
| **Closure** | A set of store paths including all dependencies of a given store path |
| **Realisation** | The process of building a derivation and putting its output in the Nix store |
| **OCI** | Open Container Initiative - standards for container formats and runtimes |
| **SBOM** | Software Bill of Materials - a machine-readable list of software components |
| **CycloneDX** | A lightweight SBOM standard designed for application security contexts |
| **SPDX** | Software Package Data Exchange - an open standard for SBOM information |
| **Cosign** | A tool for signing and verifying container images |
| **Trivy** | A comprehensive vulnerability scanner for containers |
| **Syft** | A tool for generating SBOMs from container images |

---

## References

### Standards and Specifications

- [Nix Manual](https://nixos.org/manual/nix/stable/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [Nixpkgs Manual](https://nixos.org/manual/nixpkgs/stable/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)
- [CycloneDX Specification v1.5](https://cyclonedx.org/specification/1-5/)
- [SPDX Specification v2.3](https://spdx.github.io/spdx-spec/v2.3/)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Helm Charts](https://helm.sh/docs/topics/charts/)
- [Kustomize](https://kubectl.docs.kubernetes.io/references/kustomize/)

### Tools and Libraries

- [NixOS/nixpkgs](https://github.com/NixOS/nixpkgs) - Nix Packages collection
- [numtide/flake-utils](https://github.com/numtide/flake-utils) - Utilities for Nix flakes
- [anchore/syft](https://github.com/anchore/syft) - SBOM generator
- [aquasecurity/trivy](https://github.com/aquasecurity/trivy) - Vulnerability scanner
- [sigstore/cosign](https://github.com/sigstore/cosign) - Container signing
- [mikefarah/yq](https://github.com/mikefarah/yq) - YAML processor
- [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes) - Kubernetes

### Related Projects

- [openDesk Edu](https://openedusuite.example.org) - Main project website
- [openDesk Edu GitHub](https://github.com/openEduSuite) - GitHub organization
- [openDesk Edu GitLab](https://gitlab.com/opendesk-edu) - GitLab organization
- [openDesk Edu Spec](https://github.com/openEduSuite/openEduSuite-spec) - This specification repository

---

## Appendix A: Complete Service List

See [Service Catalog](#service-catalog) for the complete list of services with priorities.

---

## Appendix B: Common Commands Cheat Sheet

### Building

```bash
# Build a single image
nix build .#<service>-image

# Build all images
nix build .#all-images

# Build for specific architecture
nix build .#packages.x86_64-linux.<service>-image
nix build .#packages.aarch64-linux.<service>-image

# Build K8s manifests
nix build .#k8s-manifests

# Build and load into Docker
docker load < $(nix build .#<service>-image)
```

### Development

```bash
# Enter dev shell
nix develop .#dev

# Update inputs
nix flake update

# Show available packages
nix flake show

# Check flake metadata
nix flake metadata

# Clean Nix store
nix-collect-garbage -d
```

### Deployment

```bash
# Generate manifests
nix build .#k8s-manifests --out-link $PWD/manifests

# Apply manifests
kubectl apply -f manifests/

# Deploy to environment
nix run .#deploy-opendesk-edu -- --environment <env>

# Push image
nix run .#push-images -- <service> --registry <registry>

# Push all images to all registries
nix run .#push-images -- --all --all-registries
```

### Testing

```bash
# Run unit tests
nix-build tests/unit/

# Run integration tests
nix-build tests/integration/

# Scan for vulnerabilities
nix run .#scan-vulnerabilities -- <service>

# Generate SBOM
nix run .#generate-sbom -- <service>
```

---

## Appendix C: Environment Configurations

### UDC Environment

```nix
# k8s/environments/production/default.nix
{
  namespace = "opendesk";
  ingress = {
    className = "haproxy";
    domain = "openedusuite.example.org";
    tls = {
      enabled = true;
      secretName = "opendesk-certificates-tls";
      issuer = "opendesk-ca";
    };
  };
  storage = {
    rwx = "ceph-cephfs-hdd-ec";
    rwo = "ceph-rbd-ssd";
  };
  networking = {
    proxy = "http://proxy.openedusuite.example.org:3128";
    dns = [ "192.0.2.22" "192.0.2.5" "192.0.2.8" ];
  };
}
```

### Demo Environment

```nix
# k8s/environments/demo/default.nix
{
  namespace = "opendesk-demo";
  ingress = {
    className = "nginx";
    domain = "demo.openedusuite.example.org";
    tls = {
      enabled = true;
      secretName = "opendesk-demo-tls";
      issuer = "letsencrypt-prod";
    };
  };
  storage = {
    rwx = "standard";
    rwo = "standard";
  };
  networking = {
    proxy = null;
    dns = [ "8.8.8.8" "8.8.4.4" ];
  };
}
```

### Local Environment

```nix
# k8s/environments/local/default.nix
{
  namespace = "opendesk-local";
  ingress = {
    className = "nginx";
    domain = "localhost";
    tls = {
      enabled = false;
      secretName = null;
      issuer = null;
    };
  };
  storage = {
    rwx = "hostPath";
    rwo = "hostPath";
  };
  networking = {
    proxy = null;
    dns = [ "8.8.8.8" "8.8.4.4" ];
  };
}
```

---

## Changel