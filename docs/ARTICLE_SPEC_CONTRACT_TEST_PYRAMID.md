---
SPDX-FileCopyrightText: 2026 UDC
SPDX-License-Identifier: AGPL-3.0-only
---

# The Spec-Contract-Test Pyramid: A Framework for Documentation-Driven Development

*By openDesk Team - July 2026*

---

## Abstract

In complex infrastructure deployments, maintaining consistency between *what is specified*, *how components communicate*, and *what is actually tested* becomes increasingly difficult. The **Spec-Contract-Test Pyramid** is a novel framework that addresses this challenge by organizing documentation into three clearly defined layers: **Specifications** (Level 3), **Contracts** (Level 2), and **Tests** (Level 1). This hierarchical approach, combined with automated validation tools and CI/CD integration, transforms static documentation into a living, validated system that ensures correctness from design to production deployment.

This article explores the pyramid concept, its implementation in the openDesk Edu project, and demonstrates how it can achieve **100% traceability** from high-level requirements to automated validation.

---

## Table of Contents

1. [The Documentation Problem](#1-the-documentation-problem)
2. [Introducing the Pyramid Framework](#2-introducing-the-pyramid-framework)
3. [The Three Levels](#3-the-three-levels)
4. [The Registry: Meta-Documentation](#4-the-registry-meta-documentation)
5. [Implementation: The openDesk Edu Experience](#5-implementation-the-opendesk-edu-experience)
6. [Automation: Bringing the Pyramid to Life](#6-automation-bringing-the-pyramid-to-life)
7. [Metrics and Success Stories](#7-metrics-and-success-stories)
8. [Lessons Learned](#8-lessons-learned)
9. [Getting Started](#9-getting-started)
10. [Conclusion](#10-conclusion)

---

## 1. The Documentation Problem

Every infrastructure project faces the same documentation challenges:

### The Gap Between Design and Reality

```
SPECIFICATION  →  DEPLOYMENT  →  OPERATION
     ↓               ↓               ↓
  "We need"     "We built"    "Is it working?"
     ↓               ↓               ↓
  Design Docs   Code/Config    Tests/Monitoring
```

**The Problem:** There's no guaranteed connection between these three pillars. Specifications often:
- Become outdated as implementations evolve
- Lack testable requirements
- Don't define clear interfaces between components
- Aren't validated against actual deployments

### The openDesk Edu Challenge

The openDesk Edu project deploys a complete educational platform with:
- **50+ services** (Nextcloud, Keycloak, MariaDB, Element, SOGo, etc.)
- **400+ Helm chart values** across deployments
- **12+ namespaces** in Kubernetes
- **5+ authentication mechanisms** (SAML, OIDC, LDAP)
- **Complex dependencies** between services

With this complexity, traditional documentation approaches fail:
- Wiki pages become stale
- Diagrams don't reflect reality
- Tests don't cover deployment scenarios
- Service dependencies are implicit, not explicit

---

## 2. Introducing the Pyramid Framework

The **Spec-Contract-Test Pyramid** solves these problems by introducing a hierarchical, validated approach to documentation:

```
                        SPEC-CONTRACT-TEST PYRAMID
                              ┌─────────┐
                              │  Level 3 │ ← What do we need?
                              │ SPECS    │   High-level requirements
                              └────┬────┘
                                   │
                              ┌────▼────┐
                              │  Level 2 │ ← How do we communicate?
                              │CONTRACTS │   Interface definitions
                              └────┬────┘
                                   │
                              ┌────▼────┐
                              │  Level 1 │ ← Does it work?
                              │  TESTS   │   Automated validation
                              └─────────┘
```

### Core Principles

1. **Each level serves a distinct purpose** - No overlap, no confusion
2. **Bidirectional traceability** - Every spec maps to contracts, every contract to tests
3. **Automated validation** - CI/CD ensures consistency across all levels
4. **Executable documentation** - Tests validate that specs are implemented correctly

### Why a Pyramid?

The pyramid shape reflects the natural distribution:
- **Many specs** (top) - High-level requirements for each service and component
- **Fewer contracts** (middle) - Interfaces between services (shared resources)
- **Many tests** (bottom) - Comprehensive validation of all requirements

This contrasts with the traditional "documentation as an afterthought" approach, where documentation is either:
- Too high-level to be useful
- Too detailed to be maintainable
- Not connected to implementation

---

## 3. The Three Levels

### Level 3: Specifications (What we need)

**Purpose:** Define *what* the system should do

**Location:** `specs/` directory

**Structure:**
```
specs/
├── services/           # 24 service specifications
│   ├── keycloak/
│   │   └── index.md      # SSO service requirements
│   ├── nextcloud/
│   │   └── index.md      # File sync & share requirements
│   └── ...
├── platform/           # 17 platform specifications
│   ├── kubernetes/
│   │   └── index.md      # Cluster requirements
│   ├── monitoring/
│   │   └── index.md      # Metrics & logging requirements
│   └── ...
├── auth/               # 4 authentication specifications
│   ├── saml/
│   │   └── index.md      # SAML requirements
│   └── ...
└── integrations/       # 6 integration specifications
    └── ...
```

**Spec Template:**
```markdown
# Service Name

## Overview
- Purpose
- Scope
- Dependencies

## Requirements
### Functional Requirements
1. Shall provide [feature]
2. Shall support [protocol]
3. Shall integrate with [service]

### Non-Functional Requirements
- Performance: [SLO]
- Availability: [SLA]
- Security: [requirements]

## Configuration
- Required parameters
- Optional parameters
- Defaults

## Interconnections
- Depends on: [service1], [service2]
- Provides to: [service3], [service4]
```

**Example (Keycloak Spec):**
```markdown
## Requirements

### Functional Requirements
1. Shall provide SAML 2.0 identity provider functionality
2. Shall integrate with LDAP for user authentication
3. Shall support OIDC for modern applications
4. Shall provide admin REST API for user management

### Non-Functional Requirements
- Availability: 99.95%
- Response time: < 500ms for authentication requests
- Security: FIPS 140-2 compliant encryption

## Interconnections
- Depends on: MariaDB, Redis
- Provides to: Nextcloud, Element, SOGo, JupyterHub
```

### Level 2: Contracts (How we communicate)

**Purpose:** Define *how* services communicate with each other

**Location:** `specs/integrations/api-contracts/`

**Contract Types:**
1. **REST APIs** - HTTP endpoints, request/response formats
2. **Database schemas** - Tables, indices, constraints
3. **Message formats** - Event schemas, queue messages
4. **Configuration interfaces** - Helm values, environment variables
5. **Storage contracts** - Volume claims, object storage structures

**Contract Structure:**
```yaml
# REST API Contract Example
contract: user-management-api
version: v1.0.0
description: CRUD operations for user data

endpoints:
  POST /api/v1/users:
    request:
      schema: UserCreateRequest
      content-type: application/json
    response:
      schema: UserResponse
      status: 201
    auth: Bearer token

  GET /api/v1/users/{id}:
    request:
      params:
        id: string (UUID)
    response:
      schema: UserResponse
      status: 200

schemas:
  UserCreateRequest:
    type: object
    properties:
      username: string (required)
      email: string (required, email format)
      roles: array of strings
    required: [username, email]

  UserResponse:
    type: object
    properties:
      id: string (UUID)
      username: string
      email: string
      createdAt: string (ISO 8601)
      roles: array of strings
```

**Why Contracts Matter:**
- Prevent breaking changes between services
- Enable independent service development
- Provide clear boundaries between components
- Allow mock implementation for testing

### Level 1: Tests (Does it work?)

**Purpose:** Validate that specifications and contracts are correctly implemented

**Location:** `specs/*/tests/` directory

**Test Types:**
1. **Deployment Tests** - Verify service can be deployed
2. **Configuration Tests** - Verify settings are correct
3. **Integration Tests** - Verify service-to-service communication
4. **Contract Tests** - Verify API/interface compliance
5. **End-to-End Tests** - Verify complete workflows

**Test Example (YAML-based Helm tests):**
```yaml
suite: keycloak specification validation
description: Tests for Keycloak SSO service
templates:
  - deployment.yaml
  - service.yaml
  - ingress.yaml

tests:
  - it: should deploy with required resources
    asserts:
      - containsDocument:
          kind: Deployment
          apiVersion: apps/v1
      - hasDocuments:
          count: 3

  - it: should have SAML enabled
    set:
      sso.saml.enabled: true
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: SAML_ENABLED
            value: "true"

  - it: should connect to MariaDB
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: DB_HOST
            valueFrom:
              secretKeyRef:
                name: keycloak-db
                key: host
```

---

## 4. The Registry: Meta-Documentation

The **Registry** is the glue that holds the pyramid together, providing traceability and visibility.

### Registry Components

```
specs/_registry/
├── component-index/         # Index of all components
│   └── index.md            # Master list with categories
├── test-mapping/            # Maps tests to specs
│   └── index.md            # Which tests cover which specs
├── test-coverage-gaps/      # Identifies untested areas
│   └── index.md            # What's missing coverage
├── interconnection-matrix/  # Service dependency map
│   └── index.md            # Who depends on whom
└── implementation-reference/ # Maps specs to implementations
    └── index.md            # Which chart implements which spec
```

### Test Coverage Tracking

The test coverage registry tracks which specifications have corresponding tests:

```markdown
## Test Coverage Report

### Services (24 total)

| Service | Spec | Tests | Coverage | Status |
|---------|------|-------|----------|--------|
| Keycloak | ✅ | ✅ | 80% | Good |
| MariaDB | ✅ | ❌ | 0% | ⚠️ Missing |
| Nextcloud | ✅ | ✅ | 60% | Needs work |
| PostgreSQL | ✅ | ❌ | 0% | ⚠️ Missing |
| Redis | ✅ | ❌ | 0% | ⚠️ Missing |

### Overall Coverage: 12% (8 tests for 65 specs)

**Target: 80%+ coverage**
```

### Interconnection Matrix

The interconnection matrix documents service dependencies:

```markdown
## Service Interconnections

| Service | Depends On | Provides To | Status |
|---------|------------|-------------|--------|
| Keycloak | MariaDB, Redis | Nextcloud, Element, SOGo | ✅ Validated |
| Nextcloud | MariaDB, Redis, Keycloak | Web, Mobile | ⚠️ Partially validated |
| Element | PostgreSQL, Keycloak | Web | ❌ Not validated |
| SOGo | PostgreSQL, Keycloak | Web, CalDAV, CardDAV | ❌ Not validated |
```

This matrix enables:
- Impact analysis ("What breaks if MariaDB changes?")
- Dependency validation ("Do all dependencies have tests?")
- Deployment ordering ("What needs to start first?")

---

## 5. Implementation: The openDesk Edu Experience

### Before the Pyramid

**The Problem:**
```
Documentation Structure (Before):
├── README.md                    # General overview
├── docs/
│   ├── architecture.md          # Diagrams (often outdated)
│   ├── deployment.md            # Deployment instructions
│   └── services/                # Ad-hoc service docs
│       ├── nextcloud.md         # Mix of specs and config
│       └── keycloak.md          # Different format than others
└── charts/                      # Helm charts (no connection to docs)
    └── nextcloud/
        └── values.yaml          # No link to specs

Issues:
❌ No standard format
❌ No connection between docs and code
❌ No way to verify documentation accuracy
❌ No test coverage tracking
❌ No dependency validation
```

**Symptoms:**
- Outdated documentation
- Inconsistent formatting
- Missing information
- No way to verify if requirements are met
- Difficult to onboard new contributors

### After the Pyramid

**The Solution:**
```
Documentation Structure (After):
specs/
├── services/
│   ├── keycloak/
│   │   ├── index.md            # Specification
│   │   └── tests/              # Automated tests
│   │       └── keycloak_test.yaml
│   └── nextcloud/
│       ├── index.md
│       └── tests/
│           └── nextcloud_test.yaml
├── platform/
│   └── kubernetes/
│       ├── index.md
│       └── tests/
│           └── k8s_test.yaml
├── integrations/
│   └── api-contracts/
│       ├── index.md           # All contracts (to be split)
│       └── user-api.yaml      # Individual contract
└── _registry/
    ├── test-mapping/
    │   └── index.md
    ├── test-coverage-gaps/
    │   └── index.md
    └── interconnection-matrix/
        └── index.md

Benefits:
✅ Standard format for all specs
✅ Clear separation of concerns
✅ Traceability from spec to test
✅ Automated validation
✅ Dependency tracking
✅ Coverage metrics
```

---

## 6. Automation: Bringing the Pyramid to Life

The pyramid's power comes from **automation**. Manual maintenance of 65+ specs, 30+ contracts, and 60+ tests would be impossible. The openDesk Edu project implements comprehensive automation.

### CI/CD Workflows

#### Lint Workflow (`.github/workflows/lint.yml`)

Validates the documentation itself:

```yaml
名前: Lint

jobs:
  - spdx-headers:       # SPDX license compliance
  - code-style:         # .editorconfig compliance
  - broken-links:       # Internal link validation
  - sidebar:            # Navigation consistency
  - metadata:           # METADATA.yml validation
  - markdown-lint:      # Markdown formatting
  - yaml-lint:          # YAML formatting
  - contract-anchors:   # Contract reference validation
  - summary:            # Aggregate results
```

#### Pyramid Validation Workflow (`.github/workflows/spec-pyramid-validation.yml`)

Validates the pyramid structure:

```yaml
名前: Spec Pyramid Validation

jobs:
  - calculate-coverage:      # Measure test coverage
  - validate-interconnections: # Check service dependencies
  - validate-cross-references: # Verify cross-file links
  - validate-contracts:       # Ensure contract validity
  - summary:                  # Aggregate all checks
```

### Python Scripts

Three key scripts power the automation:

#### 1. `calculate-coverage.py` - Coverage Calculation

```bash
$ python scripts/calculate-coverage.py

Output:
about the Spec-Contract-Test Pyramid
==========================

📊 Spec-Contract-Test Pyramid Coverage Report
==============================================

Total Specifications:  65
Total Tests:           8
Total Contracts:       1

Overall Coverage:      12.31%

By Category:
────────────────────────────────────────────────
 Services (24):        25.00%  (6/24 tested)
 Platform (17):        0.00%   (0/17 tested)
 Auth (4):             0.00%   (0/4 tested)
 Integrations (6):     0.00%   (0/6 tested)

Untested Specifications:
────────────────────────────────────────────────
 ❌ specs/platform/kubernetes/index.md
 ❌ specs/services/mariadb/index.md
 ❌ specs/services/postgresql/index.md
 ... (60 more)

Coverage by Level:
────────────────────────────────────────────────
 Level 3 (Specs):     100.00%  (65/65 with specs)
 Level 2 (Contracts):  0.00%   (0/65 with contracts)
 Level 1 (Tests):      12.31%  (8/65 with tests)
```

**Features:**
- Category-based breakdown
- Untested specs listing
- Coverage by pyramid level
- CI-compatible output

#### 2. `validate-interconnections.py` - Dependency Validation

```bash
$ python scripts/validate-interconnections.py

Output:
Validating interconnections...

Matrix File: specs/_registry/interconnection-matrix/index.md
✅ Matrix file found

Services with bidirectional connections:
  ✅ Keycloak ↔ MariaDB
  ✅ Keycloak ↔ Redis
  ⚠️  Nextcloud → MariaDB (missing reverse connection)
  ❌ Element → PostgreSQL (PostgreSQL doesn't declare dependency)

Services with undeclared dependencies:
  ⚠️  SOGo declares dependency on PostgreSQL, but PostgreSQL not in matrix
  ⚠️  Etherpad declares dependency on MariaDB, but MariaDB not in matrix

Validation Complete: 2 errors, 3 warnings
```

**Features:**
- Validates declared dependencies
- Checks for bidirectional connections
- Identifies missing connections
- Validates against spec declarations

#### 3. `generate-tests.py` - Test Stub Generation

```bash
$ python scripts/generate-tests.py specs/services/keycloak

Output:
Generating test stub for Keycloak...

Found 4 functional requirements:
  1. Shall provide SAML 2.0 identity provider functionality
  2. Shall integrate with LDAP for user authentication
  3. Shall support OIDC for modern applications
  4. Shall provide admin REST API for user management

Found 3 non-functional requirements:
  1. Availability: 99.95%
  2. Response time: < 500ms for authentication requests
  3. Security: FIPS 140-2 compliant encryption

Generating test file: specs/services/keycloak/tests/keycloak_spec_test.yaml

✅ Generated 4 requirement tests + 3 SLO tests = 7 tests

Creating directory: specs/services/keycloak/tests/
Writing test file...
✅ Test stub created: specs/services/keycloak/tests/keycloak_spec_test.yaml
```

**Generated Test File:**
```yaml
suite: keycloak specification validation
description: Tests for Keycloak SSO service
templates:
  - deployment.yaml
tests:
  - it: should satisfy requirement 1: provide SAML 2.0 identity provider functionality
    release:
      name: keycloak
    asserts:
      - containsDocument:
          kind: Deployment

  - it: should satisfy requirement 2: integrate with LDAP for user authentication
    release:
      name: keycloak
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: LDAP_ENABLED
            value: "true"

  # ... 5 more tests
```

**Features:**
- Extracts requirements from spec markdown
- Generates meaningful test descriptions
- Creates valid Helm test YAML
- Can generate for all services at once

---

## 7. Metrics and Success Stories

### Current State (Before Pyramid)

```
Total Documents:        ~50 ad-hoc files
Standard Format:        ❌ No
Cross-References:       ⚠️  Some, but often broken
Test Connection:        ❌ No link between docs and tests
Dependency Tracking:    ❌ No
Automated Validation:   ❌ No
Coverage Visibility:    ❌ No
```

### Current State (With Pyramid - Phase 0)

```
Total Specifications:   65 (well-organized)
Total Contracts:        1 (needs expansion)
Total Tests:            8 (needs expansion)
SPDX Compliance:        ✅ 100%
Lint Workflow:          ✅ Running
Pyramid Validation:     ✅ Running
Overall Coverage:       12%
```

### Target State (Phase 1: 1 Month)

```
Total Specifications:   65 (stable)
Total Contracts:        30+ (split from index.md)
Total Tests:            30+ (critical services)
Overall Coverage:       50%
Service Coverage:       50% (12/24)
Platform Coverage:      40%
Automated Generation:   ✅ Yes
```

### Target State (Phase 2: 3 Months)

```
Total Specifications:   70+
Total Contracts:        40+
Total Tests:            50+
Overall Coverage:       70%
Service Coverage:       80% (19/24)
Platform Coverage:      70%
Contract Coverage:      80%
Continuous Validation:  ✅ Yes
Coverage Dashboard:     ✅ Live
```

### Target State (Phase 3: 6 Months)

```
Total Specifications:   75+
Total Contracts:        50+
Total Tests:            60+
Overall Coverage:       80%+
Service Coverage:       100%
Platform Coverage:      100%
Contract Tests:         30+
Full Automation:        ✅ Yes
```

### Measurable Benefits

| Metric | Before | After (Target) | Improvement |
|--------|--------|----------------|-------------|
| Documentation Findability | Low | High | +∞ |
| Cross-Reference Integrity | ~50% | 100% | +100% |
| Test Coverage | 0% | 80%+ | +∞ |
| Onboarding Time | Weeks | Days | -80% |
| Bug Detection | Manual | Automated | +∞ |
| Contribution Confidence | Low | High | +∞ |

---

## 8. Lessons Learned

### What Worked Well

1. **Structure First, Content Later**
   - We focused on creating the directory structure and templates before filling in content
   - This made it easy to add new specifications consistently
   - Contributors know exactly where to put new documentation

2. **Automation from Day One**
   - We implemented validation scripts before we had many specs
   - This ensured that quality standards were maintainable from the start
   - CI workflows prevent regressions

3. **Incremental Adoption**
   - We didn't convert all existing documentation at once
   - New specifications use the pyramid structure
   - Old documentation is migrated gradually
   - This prevents "big bang" failures

4. **Clear Separation of Concerns**
   - Each pyramid level has a distinct purpose
   - No overlap between layers
   - Everyone understands what belongs where

### Challenges and Solutions

**Challenge 1: Resistance to Change**
- *Problem:* Engineers accustomed to ad-hoc documentation were reluctant to adopt the new structure
- *Solution:* Demonstrated the value through automation; showed how the pyramid catches errors that manual processes miss

**Challenge 2: Initial Overhead**
- *Problem:* Creating specs, contracts, AND tests seemed like 3x the work
- *Solution:* Developed automated test generation; focused on high-value specifications first

**Challenge 3: Cross-Reference Complexity**
- *Problem:* Maintaining valid cross-references across 65+ files is error-prone
- *Solution:* Implemented automated validation; CI fails on broken references

**Challenge 4: Keeping Tests in Sync**
- *Problem:* Tests become outdated when specifications change
- *Solution:* Automated test generation from specs; require tests to be updated with specs

### Key Insights

1. **Documentation is Code**
   - Specifications should be treated with the same rigor as code
   - They should be reviewed, tested, and versioned
   - They should fail the build when broken

2. **Traceability is Non-Negotiable**
   - Every requirement must map to a test
   - Every test must map to a requirement
   - Every contract must map to both

3. **Automation is Essential**
   - Manual maintenance doesn't scale
   - Automation makes the pyramid sustainable
   - CI/CD provides instant feedback

4. **Start Small, Think Big**
   - Begin with critical services
   - Expand gradually
   - Measure progress

---

## 9. Getting Started

Want to implement the Spec-Contract-Test Pyramid in your project? Here's how:

### Step 1: Set Up the Structure

```bash
# Create directory structure
mkdir -p specs/{services,platform,auth,integrations}/_registry/{component-index,test-mapping,test-coverage-gaps,interconnection-matrix,implementation-reference}

# Create initial files
cat > specs/services/example/index.md << 'EOF'
---
SPDX-FileCopyrightText: 2026 Your Org
SPDX-License-Identifier: AGPL-3.0-only
---

# Example Service

## Overview
- Purpose: Example service for demonstration
- Scope: This, that, and the other
- Dependencies: None

## Requirements
### Functional Requirements
1. Shall provide basic functionality
2. Shall expose a REST API

### Non-Functional Requirements
- Availability: 99.9%

## Configuration
- Required: `ENABLE_FEATURE`
- Optional: `DEBUG_MODE`

## Interconnections
- Depends on: None
- Provides to: None
EOF
```

### Step 2: Add a Test

```bash
mkdir -p specs/services/example/tests
cat > specs/services/example/tests/example_test.yaml << 'EOF'
suite: example service validation
description: Basic test for example service
templates:
  - deployment.yaml

tests:
  - it: should deploy successfully
    release:
      name: example
    asserts:
      - containsDocument:
          kind: Deployment
          apiVersion: apps/v1
EOF
```

### Step 3: Set Up Validation Scripts

```bash
# Use the provided scripts or create your own
git clone https://github.com/openEduSuite/openEduSuite-spec.git
cp openEduSuite-spec/scripts/*.py your-project/scripts/
chmod +x your-project/scripts/*.py
```

### Step 4: Create CI Workflows

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/calculate-coverage.py
```

### Step 5: Start Filling the Pyramid

1. **Start with critical services** - What breaks if it's wrong?
2. **Define contracts for shared interfaces** - APIs, databases, message formats
3. **Write tests for each specification** - Use the generator to start
4. **Track coverage** - Use the coverage calculation script
5. **Iterate** - Gradually expand to all services

---

## 10. Conclusion

The **Spec-Contract-Test Pyramid** represents a paradigm shift in documentation-driven development. By organizing documentation into three clearly defined layers and implementing automated validation, we transform static documentation into a living system that:

✅ **Ensures Accuracy** - Documentation is validated against implementation
✅ **Provides Traceability** - Every requirement maps to a test
✅ **Enables Automation** - CI/CD catches errors before they reach production
✅ **Improves Maintainability** - Clear structure makes updates easy
✅ **Increases Confidence** - Everyone knows what's implemented and tested

### The Pyramid in One Sentence

> "The Spec-Contract-Test Pyramid is a framework that ensures what you specify is what you build and what you test, with automated validation at every step."

### Call to Action

Documentation doesn't have to be an afterthought. With the Spec-Contract-Test Pyramid, you can build a documentation system that's as reliable as your code. Start small, automate everything, and watch your project's quality soar.

```bash
# Get started today
python scripts/calculate-coverage.py
python scripts/generate-tests.py specs/services/your-first-service
```

---

## Appendix A: File Templates

### Specification Template

```markdown
---
SPDX-FileCopyrightText: 2026 Your Org
SPDX-License-Identifier: AGPL-3.0-only
---

# Service Name

## Metadata
- **ID**: service-name
- **Category**: services/platform/auth/integrations
- **Version**: v1.0.0
- **Status**: draft/proposed/active/deprecated
- **Owner**: @team-member

## Overview
[2-3 sentence description of the service]

### Purpose
- [Primary purpose]
- [Secondary purpose]

### Scope
- [What's included]
- [What's NOT included]

### Dependencies
- [Service 1]
- [Service 2]

## Requirements

### Functional Requirements
1. **Requirement 1**
   - Description: [What this requirement means]
   - Priority: high/medium/low
   - Category: functional

2. **Requirement 2**
   - Description: [What this requirement means]
   - Priority: high/medium/low
   - Category: functional

### Non-Functional Requirements

#### Performance
- [Requirement] - [Target] - [Priority]

#### Availability
- [Requirement] - [Target] - [Priority]

#### Security
- [Requirement] - [Target] - [Priority]

## Configuration

### Required Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| PARAM | string | "" | Description |

### Optional Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| PARAM | string | "value" | Description |

## Interconnections

### Depends On
- [Service 1] - [Purpose of dependency]
- [Service 2] - [Purpose of dependency]

### Provides To
- [Service 1] - [What it provides]
- [Service 2] - [What it provides]

## Examples

### Basic Usage
```yaml
# Example configuration
service:
  enabled: true
  config:
    param1: value1
```

## Notes
- [Additional context]
- [Known limitations]
- [Future enhancements]

## Links
- [Related specifications]
- [External documentation]
- [Source code]
```

### Contract Template

```yaml
---
SPDX-FileCopyrightText: 2026 Your Org
SPDX-License-Identifier: AGPL-3.0-only
---

# API Contract: Service Name

## Metadata
contract: service-api
version: v1.0.0
description: API contract for Service Name
dependsOn: [contract1, contract2]
status: active

## Endpoints

### GET /api/v1/resource
- **Description**: Retrieve a resource
- **Parameters**:
  - `id` (string, required): Resource identifier
- **Response**:
  - Status: 200
  - Body: Resource object
- **Authentication**: Bearer token
- **Rate Limit**: 100 requests/minute

### POST /api/v1/resource
- **Description**: Create a new resource
- **Request Body**: ResourceCreateRequest
- **Response**:
  - Status: 201
  - Body: Resource object
- **Authentication**: Bearer token

## Schemas

### Resource
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["id", "name", "createdAt"]
}
```

### ResourceCreateRequest
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    }
  },
  "required": ["name"]
}
```

## Error Responses

| Error | HTTP Status | Description |
|-------|-------------|-------------|
| InvalidRequest | 400 | Request body validation failed |
| Unauthorized | 401 | Authentication required |
| Forbidden | 403 | Insufficient permissions |
| NotFound | 404 | Resource not found |
| RateLimitExceeded | 429 | Too many requests |

## Examples

### Request
```http
GET /api/v1/resource/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Example Resource",
  "createdAt": "2026-07-25T10:00:00Z"
}
```

## Version History

| Version | Date | Changes | Backwards Compatible |
|---------|------|---------|---------------------|
| v1.0.0 | 2026-07-25 | Initial version | ✅ Yes |
```

### Test Template

```yaml
---
SPDX-FileCopyrightText: 2026 Your Org
SPDX-License-Identifier: AGPL-3.0-only
---

# Test Suite: Service Name

suite: service-name specification validation
description: Comprehensive tests for Service Name
namespace: default
templates:
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - configmap.yaml

tests:
  # Deployment Tests
  - it: should deploy with required resources
    release:
      name: service-name
      namespace: default
    asserts:
      - containsDocument:
          kind: Deployment
          apiVersion: apps/v1
      - equal:
          path: spec.replicas
          value: 1

  - it: should use the correct container image
    release:
      name: service-name
    asserts:
      - contains:
          path: spec.template.spec.containers[0].image
          content: registry.example.com/service-name:v1.0.0

  # Configuration Tests
  - it: should have required environment variables
    release:
      name: service-name
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: REQUIRED_VAR
            valueFrom:
              secretKeyRef:
                name: service-secrets
                key: required-var

  # Resource Tests
  - it: should request appropriate resources
    release:
      name: service-name
    asserts:
      - contains:
          path: spec.template.spec.containers[0].resources.requests
          content:
            memory: 256Mi
            cpu: 250m

  # Security Tests
  - it: should not run as root
    release:
      name: service-name
    asserts:
      - notContains:
          path: spec.template.spec.securityContext
          content:
            runAsUser: 0

  # Network Tests
  - it: should expose the correct ports
    release:
      name: service-name
    asserts:
      - contains:
          path: spec.template.spec.containers[0].ports
          content:
            containerPort: 8080
            protocol: TCP

  # Contract Tests
  - it: should satisfy API contract requirements
    release:
      name: service-name
    set:
      config.api.enabled: true
    asserts:
      - contains:
          path: spec.template.spec.containers[0].env
          content:
            name: API_ENABLED
            value: "true"
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Specification** | A document describing *what* a service or component should do, including requirements and design decisions |
| **Contract** | A formal definition of *how* services communicate, including APIs, schemas, and protocols |
| **Test** | An automated validation that verifies a specification or contract is correctly implemented |
| **Coverage** | The percentage of specifications that have corresponding tests |
| **Interconnection Matrix** | A document that maps service dependencies, showing which services depend on which |
| **Traceability** | The ability to trace from a requirement through to its implementation and tests |

---

## Appendix C: References

- [Helm Testing Framework](https://github.com/quintush/helm-unittest/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [JSON Schema](https://json-schema.org/)
- [SPDX License List](https://spdx.org/licenses/)
- [openDesk Edu Spec Repository](https://github.com/openEduSuite/openEduSuite-spec)

---

## Appendix D: Contributing

Like the Spec-Contract-Test Pyramid framework? We welcome contributions!

- **Report issues**: [GitHub Issues](https://github.com/openEduSuite/openEduSuite-spec/issues)
- **Contribute code**: Pull requests welcome
- **Suggest improvements**: Open a discussion
- **Ask questions**: Contact the openDesk team

---

*Copyright © 2026 UDC. Licensed under AGPL-3.0-only.*
