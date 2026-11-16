<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# OpenProject



## Purpose



Project management platform with agile boards, work packages, task tracking,

timeline planning, and Nextcloud file store integration, with OIDC

authentication via the central Keycloak IdP and comprehensive project oversight.



## Scope



This spec defines:

- ✅ **In scope**: OpenProject project management deployment, agile boards, work packages, task tracking, timeline planning, Nextcloud file store integration, OIDC authentication via Keycloak (SSO unlock without enterprise token), PostgreSQL backend, MinIO/S3 attachment storage, Memcached caching

- ❌ **Out of scope**: AI-assisted project management (external tool), resource leveling algorithms (manual scheduling only), multi-tenant SaaS mode (single-org only)



## Non-Goals



- AI-assisted project management (external tool)

- Resource leveling algorithms (manual scheduling only)

- Multi-tenant SaaS mode (single-organization deployment only)



## API Contracts



- [Keycloak OIDC Authorization Code Flow](../../integrations/api-contracts/#contract-keycloak-oidc-token-endpoint) — OIDC SSO into OpenProject (OmniAuth provider)

- [S3 Object Storage](../../integrations/api-contracts/#contract-s3-object-storage) — file/media storage

## Security Context



| Component | RunAsUser | Capabilities | Seccomp |

|-----------|-----------|--------------|---------|

| Puma (OpenProject) | non-root carve-out (root start via exception) | drop: ALL | RuntimeDefault |

> **Kyverno carve-out**: the container starts as root (surface permissions set
> before dropping to the unprivileged runtime user), covered by the
> `openproject-root-exception` PolicyException in the `dovecot-eval` exception
> registry (namespace-scoped to `openedusuite`, selector `app: openproject`).
> `allowPrivilegeEscalation: false` is declared in the manifest for BOTH the
> init and main containers and is NOT exempted. See
> `specs/platform/security` for the registry model.



## Known Quirks



**OIDC identity**: OpenProject's OmniAuth providers are gated behind the
`EnterpriseToken` SSO feature. Without an enterprise token,
`providers_for(OmniAuth::Strategies::OpenIDConnect)` returns `[]` and the SSO
start page 404s. The suite unlocks OIDC declaratively: a Rails initializer
(`config/initializers/sso_unlock.rb`, mounted from the
`openproject-sso-unlock` ConfigMap) prepends `SsoUnlockWorkaround` to the
`AuthPlugin` singleton and returns `[:keycloak]` for the OpenIDConnect
strategy, plus `OPENPROJECT_EE_MANAGER_VISIBLE=false` so the gating UI renders
cleanly.

**Auto-login forward**: with `OPENPROJECT_OMNIAUTH_AUTO_LOGIN=true`, a fresh
session is forwarded straight from `/login` to the Keycloak login page — this
is the expected UX and is asserted by the regression test
(`tests/05-regression/openproject_sso.sh`, `openEduSuite-production` repo).

**Bare `GET /auth/keycloak` returns 404 by design**: the OmniAuth request
phase is driven by the form POST from the SSO start page
(`POST /auth/keycloak`); a bare GET on the authorize path is not a valid
request and 404s. Do not assert a redirect on it.

**SAML attribute mapping**: (legacy) OpenProject requires specific SAML
attributes (`mail`, `login`). If Keycloak does not map these attributes, SAML
login fails with a generic error. The current deployment uses OIDC; SAML is
retained only for DFN-AAI federation scenarios.

**Seed job**: OpenProject seeder job creates initial data with setgid. CephFS PVC must support sticky bit inheritance for correct file permissions.



## Depends On



- **PostgreSQL** (database): Stores persistent data including projects, work packages, users, configurations

- **Memcached** (caching): Provides distributed caching for session management and query result caching

- **MinIO/S3** (object storage): Stores file attachments with versioning and retention policies

- **Nextcloud** (bootstrap only): Validates admin account existence for cross-application file store integration

- **SMTP relay** (email notification): Sends project notifications, mentions, and deadline reminders



## Integrates With



- **Keycloak** (authentication): OIDC authorization-code flow via the OmniAuth OpenIDConnect strategy; Keycloak is the sole identity source

- **Nextcloud** (file storage): Provides shared file store for project attachments via OAuth2 integration

- **Postfix** (email delivery): Relays email notifications for internal university recipients



## Requirements



### Requirement: Project and work package management



Users SHALL create projects, manage work packages, assign tasks, and track

progress using agile boards and timeline views.



#### Scenario: User creates a project

- GIVEN an authenticated user with project creation permissions

- WHEN the user creates a new project with name, type (e.g., "Software Development")

- THEN the project is stored in PostgreSQL

- AND the user is set as project administrator

- AND the user can add work packages and assign team members

- AND default agile board is created with columns (Backlog, Ready, In Progress, Done)



#### Scenario: Work package creation and assignment

- GIVEN a user in a project with work package creation permissions

- WHEN the user creates a work package with type, subject, description, assignee

- THEN the work package is stored in PostgreSQL

- AND the assignee receives notification

- AND the work package appears on the project board

- AND status field defaults to "New"



#### Scenario: Workflow status transitions

- GIVEN a work package in "New" status

- WHEN the assignee clicks "Start Work"

- THEN the work package transitions to "In Progress"

- AND the timeline updates with start time

- AND the work package moves from Ready to In Progress column



### Requirement: OIDC authentication via Keycloak (SSO)



OpenProject SHALL authenticate users via OIDC through the central Keycloak

IdP (`id.<cluster-domain>`, realm `openedusuite`, client

`openedusuite-openproject`). SSO SHALL work WITHOUT an OpenProject enterprise

token (see Known Quirks for the declarative unlock) and SHALL be covered by a

regression test.



#### Scenario: User logs in via OIDC

- GIVEN a user accessing OpenProject

- WHEN the user opens `/login` and the SSO start page renders (HTTP 200)

- AND the session+CSRF form posts to `/auth/keycloak`

- THEN the browser is redirected to Keycloak's authorize endpoint

- AND (with auto-login) the session forwards directly to the Keycloak login page

- AND Keycloak validates credentials against the configured identity provider

- AND the `email` standard claim (id_token) is used for user identification

- AND `name` / display claims populate the user profile



#### Scenario: SSO unlock without enterprise token

- GIVEN `providers_for(OmniAuth::Strategies::OpenIDConnect)` is empty

- WHEN the initializer `SsoUnlockWorkaround` is loaded (`ancestors` of

  `OpenProject::Plugins::AuthPlugin.singleton_class` include it)

- THEN OIDC SSO works with `EnterpriseToken` absent

- AND `EnterpriseToken.allows_to?(:sso_auth_providers)` remains false

- AND `OPENPROJECT_EE_MANAGER_VISIBLE=false` prevents the gating UI



#### Scenario: Group mapping from OIDC claims

- GIVEN a user logging in with a `groups` claim containing `student`

- WHEN the user is authenticated

- THEN the user is added to the "Student" role in OpenProject

- AND project permissions are automatically assigned based on role

- AND group sync runs on a schedule via bootstrap job



### Requirement: PostgreSQL persistence



OpenProject SHALL store all project data in PostgreSQL with adequate storage

capacity for long-term project archiving.



#### Scenario: Project data persistence

- GIVEN a project with work packages, attachments, and timeline

- WHEN PostgreSQL pod restarts

- THEN all project data persists in RWO PVC

- AND PostgreSQL serves latest state without data loss

- AND RWO PVC `openproject-postgres-data` is excluded from k8up schedule



#### Scenario: PostgreSQL connection handling

- GIVEN OpenProject configured for PostgreSQL

- WHEN database connection pool is initialized

- THEN OpenProject connects to `postgresql:5432` with user `openproject_user`

- AND maximum connections is 50 (tunable via config)

- AND connection timeout is 10 seconds



### Requirement: Memcached application caching



OpenProject SHALL use Memcached for application-level caching to reduce

PostgreSQL load and improve response times.



#### Scenario: Cache configuration

- GIVEN OpenProject deployed with Memcached

- THEN Memcached is available at `memcached:11211`

- AND OpenProject uses it for session caching (30 min TTL)

- AND OpenProject uses it for page caching (5 min TTL)

- AND cache hit ratio is > 80% under normal load



#### Scenario: Cache invalidation

- GIVEN a work package updated in OpenProject

- WHEN the update is committed

- THEN related cache entries are invalidated

- AND subsequent requests fetch fresh data from PostgreSQL

- AND cache repopulation is transparent to users



### Requirement: S3 Object Storage for attachments



OpenProject SHALL store file attachments in S3-compatible object storage (MinIO)

with versioning and retention policies.



#### Scenario: Attachment upload

- GIVEN a user uploading a PDF attachment (10MB) to a work package

- WHEN the upload completes

- THEN the file is stored in the configured S3 bucket (`openproject`)

- AND path is `/projects/{project_id}/work_packages/{wp_id}/attachments/{filename}`

- AND file is served via MinIO S3 API

- AND Nextcloud can access immutable snapshots (when configured)



#### Scenario: S3 authentication

- GIVEN OpenProject configured for S3

- WHEN attachments are uploaded/downloaded

- THEN OpenProject authenticates via `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

- AND credentials are stored in `openproject-openproject` secret

- AND S3 endpoint is `http://minio:9000` (cluster-local)



#### Scenario: Version control and retention (deployment-only via Never for now)

- Given versioning is required but will not be engaged at this time (Working assumption: no versioning for openproject in current deployments)

- While file retention is enforced for 7 years externally (retention policy: out of spec scope here)

- Mark as deployment-only for current use.



### Requirement: Nextcloud file store integration



OpenProject SHALL bootstrap admin account using Nextcloud API v3 admin password

for cross-application file store integration.



#### Scenario: Admin bootstrap

- GIVEN a fresh OpenProject deployment

- WHEN the bootstrap job runs

- THEN Nextcloud API v3 `GET /ocs/v2.php/cloud/users/admin` validates admin existence

- AND admin password matches `secret.openproject.nextcloud_password`

- AND OpenProject admin is created with same password

- AND subsequent Nextcloud integration (RSpec via pre-approve) can function



### Requirement: SMTP email notifications



OpenProject SHALL send email notifications for work package updates, mentions,

and deadline reminders via SMTP relay.



#### Scenario: Notification delivery

- GIVEN a work package assigned to user1

- WHEN user2 updates the work package

- THEN user1 receives email notification

- AND email is sent via Postfix SMTP relay (`postfix:587` STARTTLS)

- AND From address is `noreply@openedusuite.example.com`

- AND emails for `*@production.example.com` are delivered by local relay



#### Scenario: SMTP relay handling

- Given outbound email to internal recipients (`*@production.example.com`)

- When OpenProject sends notification

- Then email is relayed via Postfix local relay `opendesk-email`

- And external recipients use the inbound relay at `proxy.openedusuite.example.com:3128`



### Requirement: Health and monitoring



OpenProject SHALL be healthy and monitorable with health endpoints and metrics.



#### Scenario: Health checks

- GIVEN OpenProject deployment

- WHEN the container responds on HTTP port 8080 (health check) and `api/v3/status` (readiness probe)

- THEN the pod is marked healthy

- AND health endpoint returns `{"status":"ok"}` when database and S3 are reachable

- AND readiness probe validates PostgreSQL and Memcached connectivity



#### Scenario: Metrics and monitoring

- GIVEN Prometheus configured for scraping

- WHEN Prometheus scrapes OpenProject metrics

- THEN metrics include work package creation rate, cache hit rate, database latency

- And AlertManager sends alerts when work package creation rate drops below threshold

- Or Metrics include daily (or other) aggregated counts (stored via Prometheus, enabling visualization)



### Requirement: Capacity planning and sizing



OpenProject SHALL support capacity planning with resource defaults for typical

university deployment settings.



#### Scenario: Memory and CPU defaults (baseline)

- Given a medium deployment (500 users)

- And typical load (50 concurrent requests/sec)

- Recommended memory: 4 GiB (or actual deployment spec: 2 GiB app, 4 GiB DB; 8 GiB app, 8 GiB DB)

- Recommended CPU: 4 cores (or actual deployment spec: 2 cores app, 4 cores DB; 4 cores app, 4 cores DB)

- Storage: PostgreSQL RWO PVC (30 GiB incremental growth) + S3 (no limit; bucket lifecycle: 7 years retention)



#### Scenario: Storage growth projection

- Given 500 projects per semester, averaging 5 work packages per project

- With 100 KB per work package (text + small attachments)

- Estimated semester growth: 250 MB (projects) + 5 GB attachments min (S3 bucket)

- Annual growth: 2 GB (projects) + 20 GB attachments min (S3 bucket)

- Recommended PVC size increments: 10 GB PostgreSQL per year (actual: 30 GiB baseline)

- Recommended S3 bucket quota: 100 GB (can scale with MinIO)





## Component Reference



| Property | Value |

|---------|-------|

| Chart | Upstream OpenProject (OCI registry: `opencode.de`)

| Database | PostgreSQL (`openproject` DB, `openproject_user`) |

| Storage | RWO PVC (`postgres-data` 30Gi) + S3 (`openproject-uploads` bucket) |

| Cache | Redis (`cache.openproject.host:port`) |

| License | GPL-3.0 |

| Config | ``helmfile/apps/openproject/values.yaml.gotmpl`` |

| Image | Upstream OpenProject (OCI registry) |

| Replicas | 2 (default) |



## SLO



**Tier**: High (important for project management, can degrade gracefully)



| Metric | Target | Measurement |

|--------|--------|-------------|

| **Availability** | 99.5% (3.6 hours downtime/month max) | Uptime over 30-day window |

| **Latency (P95)** | <500ms (page load) | Nginx access log analysis |

| **Latency (P95)** | <1s (work package update) | OpenProject API response metrics |

| **Error Rate** | <0.5% (HTTP 5xx) | Nginx access log analysis |

| **Cache Hit Rate** | >80% (Memcached) | Memcached metrics |



**Alerts**:

- OpenProject 5xx error rate >1% for 10 minutes → P2 alert

- Database connection pool exhausted → P2 alert

- Memcached connection failures >3 in 5 minutes → P2 alert

- SAML authentication failures >5% for 5 minutes → P1 alert

- S3 attachment upload failures >2% for 10 minutes → P3 alert



**Capacity**:

- 2,000 concurrent users

- 10,000 work packages created per month (typical)

- 5,000 API requests per minute (peak)

- Database: 10 GB (typical), 100 GB (large institution)

- S3 attachments: 1 TB (typical), 10 TB (large institution)



## Disaster Recovery



**Tier**: High (RPO: 1 hour, RTO: 4 hours)



**Backup Strategy**:

- **Database** (PostgreSQL): Hourly incremental + daily full backup, PITR enabled

- **S3 attachments**: Daily snapshot, 30-day retention

- **Memcached state**: Stateless (no backup needed)

- **Configuration**: GitOps-managed



**Recovery Order**:

1. PostgreSQL database restore - 20 min

2. S3 attachment verification - 15 min

3. OpenProject application deployment - 15 min

4. Memcached deployment - 5 min

5. SAML SP configuration verification - 5 min

6. Nextcloud integration test - 5 min

7. SMTP relay configuration test - 5 min

8. Smoke tests (login, project creation, work package update) - 10 min

9. User access restoration - 15 min



**Critical Data**:

- Projects, work packages, and timelines

- User assignments and permissions

- File attachments (S3)

- Comments and activity logs

- Custom fields and workflows



**Failure Scenarios**:

- **Database corruption**: Restore from PITR, verify project data integrity

- **S3 attachment loss**: Restore from snapshot, verify checksums

- **SAML misconfiguration**: Re-register SP in Keycloak, verify SSO flow

- **Complete failure**: Redeploy from GitOps, restore DB + attachments, re-register SAML SP
