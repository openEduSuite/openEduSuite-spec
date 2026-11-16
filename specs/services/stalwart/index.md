<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Stalwart (Mail Server: SMTP / IMAP / JMAP)

## Purpose

Mail delivery and mailbox server for the suite at `mail.<cluster-domain>`
(SMTP submission/relay + IMAP/JMAP mailbox access), using the
`stalwart-rewrite` fork. The fork automatically provisions default IMAP
folders so mail search/filters (SEARCH HEADER Message-ID / IMAP tag
searches, JMAP header filters) return real hits — a fix tied to the suite's
mail + SOGo6 mailbox story. Authentication is XOAUTH2/OAuth-based (no
password logins against the mail server); a companion admin web UI
(`stalwart-webui`) manages the server.

## Scope

- ✅ **In scope**: Stalwart mail server (SMTP `25/465/587`, IMAP `143/993`,
  HTTP/JMAP `8080`), the rewrite fork's folder provisioning, XOAUTH2/OAuth
  auth, admin web UI, mail domain routing
- ❌ **Out of scope**: webmail UI (that is SOGo6), fighting spam/phishing
  beyond configured filters, replacing the identity layer (Keycloak)

## Non-Goals

- Being the webmail client (SOGo6 is the mail UI)
- Password-authenticated IMAP/SMTP for users (OAuth/XOAUTH2 only)

## Requirements

### Requirement: XOAUTH2 / OAuth authentication

Users SHALL authenticate to IMAP/SMTP via OAuth/XOAUTH2 against the suite
identity layer; no password-based mailbox login is offered.

#### Scenario: IMAP access via OAuth

- GIVEN a user with a valid OAuth token
- WHEN the user connects to IMAP (`:143`/`:993`)
- THEN the mailbox is served without a password prompt
- AND mailbox operations (search, folders) work over XOAUTH2

#### Scenario: Mailbox path availability

- WHEN the LDAP/directory is unreachable at boot
- THEN the affected directory provisioning is skipped gracefully
- AND the mail server still starts for existing mailboxes

### Requirement: Default-folder provisioning (rewrite fork)

The `stalwart-rewrite` image SHALL provision default IMAP folders so
SEARCH HEADER Message-ID / JMAP header filters return real hits.

#### Scenario: Fresh mailbox has working search

- WHEN a new mailbox is created
- THEN default folders (INBOX, Sent, Drafts, Trash, ...) are provisioned
- AND message-header searches match across SEPARATOR/namespace variants

### Requirement: Port contract

The mail server SHALL expose the standard ports on the mail domain:
SMTP `25`, submission `587`, SMTPS `465`, IMAP `143`, IMAPS `993`, and
HTTP/JMAP admin `8080`.

#### Scenario: Port exposure

- WHEN the service is inspected
- THEN all mail protocol ports are mapped to `mail.<cluster-domain>`
- AND `8080` serves the JMAP/HTTP endpoint

### Requirement: Pinned fork image

Stalwart SHALL run from the pinned `stalwart-rewrite`
(commit `77df41ab...`) via the local registry; `latest` is never used.

#### Scenario: Image provenance

- WHEN the deployment manifest is inspected
- THEN the fork image is pinned by committed digest/tag via the local
  registry mirror

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| stalwart | SMTP/IMAP/JMAP server (fork) | 1 | data volume |
| stalwart-webui | admin web UI (`openedusuite/stalwart-webui:0.1.0`) | 1 | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| stalwart | distro default (non-root service) | drop: ALL | RuntimeDefault |
| stalwart-webui | distro default | drop: ALL | RuntimeDefault |

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `stalwart-rewrite:77df41ab...` (local registry, pinned) |
| Domain | `mail.<cluster-domain>` |
| Ports | `25`, `587`, `465`, `143`, `993`, `8080` (JMAP/HTTP) |
| Auth | XOAUTH2 / OAuth (no password logins) |
| Admin | `stalwart-webui:0.1.0` (`:8080`) |

## Depends On

- Identity layer (OAuth/XOAUTH2 token validation)
- DNS (`mail.<cluster-domain>` MX/A)
- TLS certificates (SMTPS/IMAPS)

## Integrates With

- Keycloak / identity (XOAUTH2 token issuance)
- SOGo6 (webmail UI reads mailboxes over IMAP/JMAP)
- DNS + cert-manager

## SLO

**Tier**: Critical (core mail transport for the whole suite)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.9% | Uptime over 30-day window |
| **Delivery latency (P95)** | <60 s (queued mail) | mail logs |
| **Error Rate** | <0.5% 4xx/5xx on SMTP submission | mail logs |

## Disaster Recovery

**Tier**: Critical (RPO: ≤24 h, RTO: 2 h)

- **Configuration**: GitOps-managed manifests + `secret-stalwart` (admin
  recovery credential)
- **Mail data**: mailbox store backups via the existing backup regime
- **Recovery order**: restore mail store → redeploy from GitOps → verify
  SMTP/IMAP + folder provisioning
