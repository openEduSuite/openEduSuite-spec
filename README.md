<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# openDesk Edu Spec

Complete specification framework for the openDesk Edu ecosystem — covering services, infrastructure components, platform topics, auth, integrations, and registry.

**Repository**: https://github.com/openEduSuite/openEduSuite-spec

## Structure

```
openEduSuite-spec/
├── specs/                    # Source of truth — all specifications
│   ├── services/             # 24 service specs (nextcloud, element, moodle, ...)
│   ├── platform/             # 17 platform specs (deployment, monitoring, security, ...)
│   ├── auth/                 # OIDC, SAML, LDAP, federation
│   ├── integrations/         # Intercom, provisioning, API contracts, LTI
│   ├── methodology/          # Spec writing guidelines
│   └── _registry/            # Component index, test mapping, interconnection matrix
├── docs/                     # Docusaurus viewer (runs via Docker)
│   ├── docker-compose.yml
│   ├── Dockerfile            # Multi-stage: node build → nginx serve
│   ├── Dockerfile.dev        # Live-reload dev server
│   ├── docusaurus.config.ts
│   └── sidebars.ts
├── changes/                  # Active change proposals
├── archive/                  # Archived change proposals
├── papers/                   # Published papers (md + pdf)
├── METADATA.yml              # Spec metadata index (domain, auth, tier, scenarios)
├── METHODOLOGY.md            # Spec methodology overview
├── opendesk_core.schema.json # Upstream integration contract schema
└── index.html                # Redirect → GitHub repo
```

## Running the Docs Site

### Production (nginx, port 3000)

```bash
docker compose -f docs/docker-compose.yml up docusaurus
```

### Development (hot reload, port 3000)

```bash
docker compose -f docs/docker-compose.yml up dev
```

Both mount `specs/` as a read-only volume — the specs are read directly, no import step needed.

## Spec Categories

| Category | Count | Description |
|----------|-------|-------------|
| Services | 24 | Individual service deployment, auth, and configuration specs |
| Platform | 17 | Cross-cutting concerns (backup, networking, security, monitoring) |
| Auth | 4 | OIDC, SAML, LDAP, federation |
| Integrations | 6 | Inter-service communication and data flow |
| Registry | 5 | Component index, test mapping, interconnection matrix |

## Change Proposals

Active proposals live in `changes/`. Each has three files:

- `proposal.md` — motivation, scope, acceptance criteria
- `specs.md` — delta specs (added/modified/removed)
- `tasks.md` — implementation steps

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for spec template, formatting rules, and review process.

## Related

- [openedusuite.example.org](https://openedusuite.example.org) — Main project website
- [landscape.openedusuite.example.org](https://landscape.openedusuite.example.org) — Interactive service map
- [openEduSuite/openEduSuite-public](https://github.com/openEduSuite/openEduSuite-public) — Source code and deployment

## License

Apache-2.0
