# MySQL Exporter (Prometheus)

<!--
SPDX-FileCopyrightText: 2026 openEduSuite Contributors
SPDX-License-Identifier: Apache-2.0
-->

## Purpose

Expose MySQL/MariaDB/Galera metrics (server status, replication,
performance_schema) to the cluster Prometheus/metrics stack for dashboards
and alerting. Runs as a stateless single-replica DaemonSet scraped by
Prometheus for the mariadb-galera cluster.

## Scope

- ✅ **In scope**: mysqld-exporter deployment (pinned image), metrics HTTP
  endpoint on port 9104, DB credentials from the `mysqld-exporter` secret,
  Prometheus scraping via the `networkpolicy-allow-prometheus-metrics` rule
- ❌ **Out of scope**: the MariaDB/Galera server itself (see
  `../mariadb/`), alert rule authoring, Grafana dashboards

## Non-Goals

- Owning or managing the MariaDB/Galera cluster (only scrapes it)
- Storing metrics locally (Prometheus is the source of truth)
- Exporting metrics for PostgreSQL (see `../postgresql/`)

## Requirements

### Requirement: Pinned image and metrics endpoint

The exporter SHALL run from a pinned image and expose its metrics on the
standard HTTP port.

#### Scenario: Image provenance and port

- WHEN the deployment manifest is inspected
- THEN the image is `172.25.24.36:5001/prom/mysqld-exporter:v0.14.0`
- AND the metrics HTTP endpoint listens on port `9104`

### Requirement: DB credentials from secret

The exporter SHALL read Galera cluster credentials from the
`mysqld-exporter` secret rather than from inline values.

#### Scenario: Secret-backed connection

- GIVEN the `mysqld-exporter` secret containing DB credentials
- WHEN the exporter starts
- THEN it connects to the mariadb-galera cluster using those credentials
- AND no credentials appear in the pod spec env vars in cleartext

### Requirement: Prometheus scraping

The exporter SHALL be scraped by the cluster Prometheus for the
mariadb-galera cluster.

#### Scenario: Metrics reachable by Prometheus

- GIVEN the `networkpolicy-allow-prometheus-metrics` NetworkPolicy
- WHEN Prometheus scrapes port `9104`
- THEN MySQL/MariaDB/Galera metrics are ingested for dashboards and alerting

## Component Reference

| Component | Purpose | Replicas | Storage |
|-----------|---------|----------|---------|
| mysqld-exporter | Prometheus exporter for MySQL/MariaDB/Galera metrics (`:9104`) | 1 (stateless) | — |

## Security Context

| Component | RunAsUser | Capabilities | Seccomp |
|-----------|-----------|--------------|---------|
| mysqld-exporter | non-root | drop: ALL | RuntimeDefault |

> **Quirk (known ops context):** the mysqld-exporter pod has been observed
> in Error/FailedCreate state due to systemic Kyverno `zki-*` enforce
> denials (e.g. `drop-all-capabilities`). The target posture is
> `drop: ALL`, no privilege escalation, `RuntimeDefault` seccomp. Admission
> denial follow-up is tracked under platform/security (Kyverno BSI
> INF.1 M 1.84 requirement).

## Configuration Reference

| Property | Value |
|----------|-------|
| Image | `172.25.24.36:5001/prom/mysqld-exporter:v0.14.0` (pinned) |
| Metrics port | `9104` (HTTP) |
| Credentials | `mysqld-exporter` secret (Galera DB user/password) |
| Target | mariadb-galera cluster |
| Scrape path | `/metrics` (Prometheus via `networkpolicy-allow-prometheus-metrics`) |

## Depends On

- MariaDB/Galera cluster (scrape target, see `../mariadb/`)
- `mysqld-exporter` secret (DB credentials)

## Integrates With

- Prometheus (scrapes `:9104`)
- Grafana (dashboards consuming the exported metrics)
- Kyverno admission policies (security posture enforcement)

## SLO

**Tier**: Low (metrics only)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99% | Uptime over 30-day window |
| **Latency (P95)** | <500 ms | `/metrics` scrape duration |
| **Error Rate** | <1% scrape failures | Prometheus scrape log |

## Disaster Recovery

**Tier**: Low (RPO: n/a, RTO: 4 h)

- **Configuration**: GitOps-managed manifests + `mysqld-exporter` secret
- **User data**: none (stateless exporter; metrics stored in Prometheus)
- **Recovery order**: redeploy from GitOps → verify Prometheus scraping
  `:9104` → confirm dashboards populate
