<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Invoice Ninja (Invoicing / Billing)

## Purpose

Invoicing and billing platform for internal cost-recovery workflows
(e.g. operated-services invoices triggered by finished Operaton processes).
Authenticated via the central Keycloak IdP through the standard oauth2-proxy
gateway pattern, using the customized SSO image with a dedicated Nginx
front on the configured locale/timezone.

## Scope

- ✅ **In scope**: Invoice Ninja deployment (custom SSO image), SSO via
  oauth2-proxy (Keycloak OIDC), Nginx termination, persistence, Operaton
  invoice-generation integration
- ❌ **Out of scope**: public/third-party billing, replacing the suite's
  finance tooling outside cost-recovery flows

## Non-Goals

- Public-facing payment collection
- A general ledger / full accounting system

## Requirements

### Requirement: SSO via oauth2-proxy (Keycloak OIDC)

Invoice Ninja SHALL be reachable through the per-app oauth2-proxy instance
(`oauth2-proxy-invoicing`, provider `oidc`, Keycloak).

#### Scenario: User reaches invoicing via SSO

- GIVEN a user opening `invoicing.<cluster-domain>`
- WHEN the oauth2-proxy has no valid session cookie
- THEN the user is authenticated via Keycloak OIDC
- AND the resulting session cookie grants access to Invoice Ninja

### Requirement: Persistence

Invoices, clients and settings SHALL persist via `pvc-invoiceninja`; the
database backend follows the deployment's DB configuration (controller
environment `production`, locale `de`, timezone `Europe/Berlin`).

#### Scenario: Data survives restart

- WHEN an invoiceninja pod is recreated
- THEN invoices/clients persist via `pvc-invoiceninja`
- AND APP_URL stays at `https://invoicing.openedusuite.org`

### Requirement: Operaton integration

Invoice generation SHALL be triggerable from Operaton BPMN processes over
the dedicated in-cluster route, as allowed by the `allow-operaton-to-invoiceninja`
NetworkPolicy (selector `app: invoice-ninja`).

#### Scenario: Invoice generated from a completed process

- GIVEN an Operaton process that completes a billable service
- WHEN the engine/worker invokes the invoicing API in-cluster
- THEN a client/invoice record is created
- AND network policy allows only the Operaton namespace caller to the
  `invoice-ninja` pods

### Requirement: Pinned customized image

The deployment SHALL use the pinned mirrored SSO image
(`invoiceninja-sso:5.13.37-sso.9`); `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the pinned SSO fork tag is referenced via the local registry mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| invoiceninja | application (custom SSO image) | 1 | `pvc-invoiceninja` |
| nginx | front termination/routing | 1 | — |
| oauth2-proxy | OIDC SSO gateway (`oauth2-proxy-invoicing`) | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| invoiceninja | non-root (declared, see quirk) | drop: ALL | RuntimeDefault |

> **Known issue**: the manifest previously declared a contradictory
> `runAsNonRoot: true` + `runAsUser: 0` pair (drift vs. the image's user).
> Re-sync to the image's declared user is tracked with the systemic Kyverno
> enforce follow-up (see platform/security).

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `invoiceninja-sso:5.13.37-sso.9` (local mirror, pinned) |
| Route | `invoicing.<cluster-domain>` → oauth2-proxy → nginx |
| APP_URL | `https://invoicing.openedusuite.org` |
| Locale / TZ | `de` / `Europe/Berlin` |
| Operaton path | in-cluster NetworkPolicy `allow-operaton-to-invoiceninja` |

## Depends On

- Keycloak (OIDC via oauth2-proxy)
- Database backend (per deployment environment)
- HAProxy Ingress

## Integrates With

- Keycloak (OIDC SSO via `oauth2-proxy-invoicing`)
- Operaton (BPMN-triggered invoice generation)
- Portal (tile entry)

## SLO

**Tier**: Medium (stateful, SSO-gated, low traffic)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.5% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | Ingress access logs |
| **Error Rate** | <1% HTTP 5xx | Ingress access logs |

## Disaster Recovery

**Tier**: Medium (RPO: ≤24 h, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + startup/nginx ConfigMaps
- **User data**: `pvc-invoiceninja` + database backups via the existing
  backup regime
- **Recovery order**: restore DB/PVC → redeploy from GitOps → verify SSO
  via oauth2-proxy
