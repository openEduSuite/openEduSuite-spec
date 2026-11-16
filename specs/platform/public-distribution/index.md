# Public Distribution

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->



## Purpose



The `openEduSuite-public` repository is a sanitized, publishable subset of the
private `openEduSuite-production` deployment. Its purpose is to let other institutions
reuse and deploy the openEduSuite application set without exposing internal IP
addresses, secrets, or university-specific configuration. The public distribution
provides a Helmfile-based deployment template, an EU `publiccode.yml` descriptor,
a GitHub Actions CI that renders the Helmfile and runs leak-scans, and a static
docs viewer (Dockerfile/nginx.conf) so adopters can browse the rendered
specification and manifests.



## Scope



- The public repository `openEduSuite-public`
  (remote `git@github.com:tobias-weiss-ai-xr/openEduSuite-public.git`).
- The ported application manifests under `helmfile/` (Helmfile + Helm releases,
  with `environments/example.yaml` as the reference environment).
- The sanitization pipeline (`sanitize_public.py` pattern) that produces the
  public subset from the private deployment.
- The GitHub Actions CI (`ci.yml`) that renders the Helmfile and runs leak-scans
  as a publication gate.
- The `publiccode.yml` EU publiccode descriptor, the static docs viewer
  (`Dockerfile`, `nginx.conf`), and the repository README.
- Adopter prerequisites: a general-purpose Kubernetes cluster with the
  equivalent infrastructure (see Depends On).

Out of scope: the private `openEduSuite-production` deployment itself (this spec only
references it as the provenance source), and the run-time behavior of the
deployed suite (see the relevant service and platform specs).



## Non-Goals



- Reproducing the full private deployment. Some applications are intentionally
  omitted from the public set (e.g. those with non-pullable OCI images such as
  `kasmvnc` and the `overleaf` fork; ops-only infrastructure such as
  `mysqld-exporter` stays private).
- Carrying private git history into the public repo. The public repository has
  no git baseline of the private history; it is regenerated through the
  sanitization pipeline.
- Guaranteeing a release cadence. The distribution is a process/convenience
  artifact; its tier does not affect the running suite and is not measured as an
  SLO (see SLO).
- Application-level feature parity with the private deployment. Public manifests
  are generic templates, not production-tuned values.



## Requirements



### Requirement: General-purpose cluster prerequisites



The public distribution SHALL target a general-purpose Kubernetes cluster so
that any compliant institution can adopt it without university-specific
assumptions.



#### Scenario: Adopter cluster meets prerequisites

- GIVEN a Kubernetes cluster with version 1.28 or later
- AND cert-manager, an ingress controller, PostgreSQL/MariaDB/MinIO-equivalent
  data services, and a Keycloak (or compatible OIDC) identity provider
- WHEN the adopter clones `openEduSuite-public` and renders `environments/example.yaml`
- THEN the Helmfile renders without referencing internal hostnames, registries,
  or secrets
- AND the adopter can substitute `<cluster-domain>` and placeholder secret refs
  with their own values



### Requirement: Sanitization pipeline (provenance)



Content SHALL flow from the private `openEduSuite-production` deployment to the public
repository exclusively through a sanitization pipeline following the
`sanitize_public.py` pattern. The pipeline genericizes content — it never simply
deletes ported artifacts — so that adopters receive functional templates.



#### Scenario: Internal hostnames and domains are genericized

- GIVEN a private manifest referencing an internal hostname or domain
- WHEN the sanitization pipeline processes the manifest
- THEN the internal value is replaced with the placeholder `<cluster-domain>`
- AND no internal hostname or domain remains in the rendered output



#### Scenario: Secrets are replaced with placeholder refs

- GIVEN a private manifest referencing concrete secret values
- WHEN the sanitization pipeline processes the manifest
- THEN concrete secrets are replaced with placeholder secret references
- AND no real secret material is present in the public repository



#### Scenario: Internal registries are remapped to public upstream tags

- GIVEN a private manifest pulling from internal registries
  (`172.25.24.36:5001` or `172.25.24.36:5002`)
- WHEN the sanitization pipeline processes the manifest
- THEN the internal registry references are replaced with public upstream image
  tags
- AND no internal IP/registry reference remains in the public repository



#### Scenario: University-specific names are genericized

- GIVEN a private manifest containing university names or institution-specific
  labels
- WHEN the sanitization pipeline processes the manifest
- THEN those names are replaced with generic labels
- AND no university-specific identifier is present in the public repository



### Requirement: Leak-scan publication gate



A leak-scan SHALL run in CI before every push to the public repository, and the
CI SHALL fail on any secret, IP, or domain leak detected in the rendered output.



#### Scenario: Rendered output contains a leaked secret

- GIVEN the CI `ci.yml` renders the Helmfile and runs a leak-scan
- WHEN a secret value is detected in the rendered output
- THEN the CI job fails
- AND no push to the public repository occurs



#### Scenario: Rendered output contains an internal IP or domain

- GIVEN the CI `ci.yml` renders the Helmfile and runs a leak-scan
- WHEN an internal IP (e.g. `172.25.24.36`) or internal domain is detected in
  the rendered output
- THEN the CI job fails
- AND no push to the public repository occurs



### Requirement: No private git history



The public repository SHALL carry no git baseline of the private
`openEduSuite-production` history. The public repo is produced by re-rendering from the
sanitized pipeline, not by mirroring the private history.



#### Scenario: Public repo is regenerated, not mirrored

- GIVEN the private deployment advances with new commits
- WHEN the sanitization pipeline is re-run
- THEN a fresh public repository state is rendered
- AND no private commit history, author metadata, or internal branch names are
  present in the public repository



### Requirement: Publiccode descriptor



The repository SHALL include a `publiccode.yml` file conforming to the EU
publiccode standard so that the distribution is discoverable and interoperable
across public administrations.



#### Scenario: Adopter inspects publiccode.yml

- GIVEN an adopter evaluating the distribution
- WHEN the adopter reads `publiccode.yml`
- THEN the descriptor describes the software, its license, and its intended use
- AND no internal institution data is present in the descriptor



### Requirement: Static docs viewer



The repository SHALL include a `Dockerfile` and `nginx.conf` that build and
serve a static docs viewer, allowing adopters to browse the rendered
specification and manifests without a full local toolchain.



#### Scenario: Adopter builds the docs viewer

- GIVEN the repository checked out locally
- WHEN the adopter builds the Docker image and runs the container
- THEN the static docs viewer is served over HTTP
- AND the rendered content reflects the current public repository state



## Component Reference



| Property | Value |

|---------|-------|

| Repository | `openEduSuite-public` |

| Remote | `git@github.com:tobias-weiss-ai-xr/openEduSuite-public.git` |

| Provenance Source | Private `openEduSuite-production` deployment |

| Sanitization Tooling | `sanitize_public.py` pattern (genericize, never delete) |

| Orchestration | Helmfile + Helm releases under `helmfile/` |

| Reference Environment | `environments/example.yaml` |

| CI | GitHub Actions (`ci.yml`): Helmfile render + leak-scan gate |

| Public Descriptor | `publiccode.yml` (EU publiccode standard) |

| Docs Viewer | `Dockerfile` + `nginx.conf` (static) |

| Ported App Manifests | 27-35 (portal-tiled set) |

| Current Status | 25 releases / ~257 objects rendered green |

| Intentionally Omitted | `kasmvnc`, `overleaf` fork (non-pullable OCI images); `mysqld-exporter` (ops-only) |

| Tier | Process / convenience (does not affect the running suite) |

| License | Apache-2.0 |



## Configuration Reference



| Item | Description |

|------|-------------|

| `helmfile/` | Ported application manifests as Helmfile + Helm releases |

| `environments/example.yaml` | Reference environment adopters copy and adapt |

| `<cluster-domain>` | Placeholder substituted by adopters for their ingress domain |

| Placeholder secret refs | Substituted by adopters with their own secret management |

| `publiccode.yml` | EU publiccode descriptor for discoverability |

| `Dockerfile` / `nginx.conf` | Build and serve the static docs viewer |

| `ci.yml` | GitHub Actions workflow: render Helmfile + leak-scan gate |

| `README.md` | Adopter-facing entry point and quickstart |



## Security Context



- The public repository MUST NOT contain internal IPs, internal domains,
  secrets, or university-specific identifiers. Genericization (never deletion)
  is the control.
- The leak-scan gate in `ci.yml` is the last line of defense and MUST fail the
  pipeline on any detected leak in rendered output.
- Because the public repo has no git baseline of the private history, no commit
  metadata or internal branch naming can leak provenance.
- Internal registries (`172.25.24.36:5001`, `172.25.24.36:5002`) MUST be
  remapped to public upstream image tags; no private registry reference is
  permitted in the public set.
- Sanitization is a one-way, lossy-by-design transform: it produces reusable
  templates, not a faithful copy of the private deployment.



## Depends On



- A general-purpose Kubernetes cluster, version 1.28 or later.
- cert-manager for TLS certificate provisioning.
- An ingress controller.
- Data-service equivalents: PostgreSQL, MariaDB, and MinIO (or compatible).
- A Keycloak or compatible OIDC identity provider.
- Helmfile 1.0.0+ and Helm 3.17.3+ for rendering (consistent with the
  deployment-orchestration spec).



## Integrates With



- `specs/platform/deployment` — the public manifests are a sanitized subset of
  the same Helmfile-based deployment orchestration used privately.
- `specs/platform/security` — the leak-scan gate and genericization policy are
  aligned with the platform's secret-derivation and chart-trust posture.
- `specs/platform/environments` — `environments/example.yaml` mirrors the
  environment pattern used across deployments.
- Adopter identity providers (Keycloak or compatible OIDC) for authentication.



## SLO



The public distribution is a process/convenience artifact: it does not affect
the running suite, so no availability SLO is measured. The operative metric is
release cadence — the ability to re-render and publish a clean, leak-free
distribution. There is no formal SLO target; the CI leak-scan gate is the
quality bar that must pass before any release is published.



## Disaster Recovery



The public repository is GitHub-hosted. Because the public set is produced by
the sanitization and re-render pipeline from the private deployment, disaster
recovery for the public distribution is "regenerate and re-render": the public
repository carries no unique state that cannot be reproduced from the private
source plus the pipeline. If the public repository is lost or corrupted, the
recovery procedure is to re-run the sanitization pipeline and re-publish the
rendered output.
