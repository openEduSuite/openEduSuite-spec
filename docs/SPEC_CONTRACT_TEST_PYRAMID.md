<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# Spec-Contract-Test Pyramid: Framework & Improvements

## Overview

This document outlines the **Spec-Contract-Test Pyramid** framework for the openDesk Edu specification repository. This three-tiered approach ensures comprehensive documentation, clear interfaces, and automated validation across all components.

```
                    ┌─────────────────┐
                    │    SPECS       │  ← High-level requirements (L3)
                    │    (65)        │  ← What we need
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   CONTRACTS    │  ← Interface definitions (L2)
                    │    (~30+)      │  ← How services communicate
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     TESTS       │  ← Implementation validation (L1)
                    │    (~60+)      │  ← How we verify
                    └─────────────────┘
```

## Current State Analysis

### ✅ Strengths

1. **Comprehensive Spec Coverage**
   - 65 specification files covering 24 services, 17 platform topics, 4 auth methods, 6 integrations
   - Well-structured hierarchy (services → platform → auth → integrations)
   - Good metadata in METADATA.yml

2. **Registry Infrastructure**
   - Test mapping tracks which tests cover which specs
   - Test coverage gaps identified and documented
   - Interconnection matrix shows service dependencies
   - Implementation reference tracks real-world deployments

3. **Test Framework**
   - YAML-based test definitions (helm-test compatible)
   - Service-level tests for OIDC, LDAP, Elasticsearch, probe timing
   - Side-by-side with specifications

4. **API Contracts**
   - Central contract definition for service integration
   - Formal API stub definitions
   - Contract-level tests directory

### ⚠️ Identified Gaps

| Area | Current | Target | Gap |
|------|---------|--------|-----|
| **Specs** | 65 | 75+ | Need more platform specs |
| **Contracts** | 1 file | 30+ | Need per-service contracts |
| **Tests** | 8 YAML files | 60+ | Need 6-8x more tests |
| **Test Coverage** | ~12% | 80%+ | Major gap |
| **Contract Tests** | 0 | 30+ | Need contract validation |
| **Integration Tests** | 0 | 20+ | Cross-service scenarios |

### 📊 Current Coverage Matrix

| Category | Specs | Contracts | Tests | Coverage |
|----------|-------|-----------|-------|----------|
| Services | 24 | 0 | 6 | 25% |
| Platform | 17 | 0 | 0 | 0% |
| Auth | 4 | 0 | 0 | 0% |
| Integrations | 6 | 1 | 0 | 0% |
| **Total** | **51** | **1** | **6** | **~12%** |

## The Pyramid Concept

### Level 3: SPECS (High-Level Requirements)
**Purpose:** Define WHAT the system should do

**Structure:**
```
specs/
├── services/           # Individual service specs
│   ├── nextcloud/      # Nextcloud service specification
│   │   ├── index.md    # Main specification
│   │   └── tests/      # Service-level tests
│   └── ... (24 services)
├── platform/           # Platform-level concerns
│   ├── deployment/     # Deployment architecture
│   ├── monitoring/     # Monitoring & observability
│   └── ... (17 topics)
├── auth/               # Authentication methods
│   ├── oidc/           # OpenID Connect spec
│   ├── saml/           # SAML spec
│   └── ...
└── integrations/       # Cross-service integrations
    ├── api-contracts/  # API contract definitions
    └── provisioning/   # User provisioning
```

**Spec Template:**
```markdown
## Overview
## Requirements
## Architecture
## Configuration
## Security Considerations
## Interdependencies
## Testing Strategy
```

### Level 2: CONTRACTS (Interface Definitions)
**Purpose:** Define HOW services communicate

**Structure:**
```
specs/integrations/api-contracts/
├── index.md                  # All contracts in one place
├── contracts/
│   ├── user-provisioning.yaml    # User provisioning contract
│   ├── auth-delegation.yaml      # Auth delegation contract
│   ├── file-storage.yaml         # File storage contract
│   └── ... (30+ contracts)
└── tests/
    ├── contract-validation.yaml  # Tests all contracts
    └── compatibility.yaml         # Cross-version compatibility
```

**Contract Definition:**
```yaml
# user-provisioning-contract.yaml
name: User Provisioning API
version: 1.0.0
description: Standard interface for user provisioning
extends: SCIM 2.0
endpoints:
  - path: /api/v1/users
    method: POST
    description: Create a new user
    request:
      schema: user-schema.json
    response:
      schema: user-response-schema.json
    slo:
      latency: < 500ms
      availability: 99.9%
```

### Level 1: TESTS (Implementation Validation)
**Purpose:** Verify THAT it works as specified

**Structure:**
```
tests/
├── unit/                    # Unit tests for individual components
│   └── services/
│       └── nextcloud/
│           └── probe_test.yaml
├── integration/             # Integration tests
│   ├── auth/
│   │   └── oidc-flow_test.yaml
│   ├── services/
│   │   └── nextcloud-element_integration.yaml
│   └── platform/
│       └── deployment_test.yaml
├── contract/                # Contract compliance tests
│   └── api-contracts/
│       └── validation.yaml
└── e2e/                     # End-to-end tests
    └── user-journey_test.yaml
```

**Test Types:**

1. **Unit Tests** - Test individual services in isolation
   - Probe timing validation
   - Container readiness checks
   - Configuration validation

2. **Integration Tests** - Test service interactions
   - OIDC authentication flow
   - LDAP group synchronization
   - Service-to-service communication

3. **Contract Tests** - Verify API contract compliance
   - Request/response format validation
   - SLO adherence
   - Error handling

4. **E2E Tests** - Full user journey validation
   - User onboarding
   - Multi-service workflows
   - Disaster recovery

## Improvements & Action Items

### 🎯 Phase 1: Foundation (High Priority)

#### 1.1 Standardize Contract Definitions
**Current:** Single monolithic `api-contracts/index.md`

**Improvement:** Create individual contract files

**Action Items:**
- [ ] Create `specs/integrations/api-contracts/contracts/` directory
- [ ] Split existing contracts into individual YAML files
- [ ] Define contract schema (JSON Schema)
- [ ] Add versioning to contracts
- [ ] Create contract index with dependency graph

**Example Contract Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "version": { "type": "string", "pattern": "^[0-9]+\.[0-9]+\.[0-9]+$" },
    "description": { "type": "string" },
    "endpoints": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "method": { "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"] },
          "request": { "$ref": "#/definitions/schema" },
          "response": { "$ref": "#/definitions/schema" },
          "slo": { "$ref": "#/definitions/slo" }
        },
        "required": ["path", "method"]
      }
    }
  },
  "required": ["name", "version", "endpoints"]
}
```

#### 1.2 Expand Test Coverage to All Services
**Current:** 6 services have tests (25% coverage)

**Target:** 24 services with tests (100% coverage)

**Action Items:**
- [ ] Create test template for services
- [ ] Add tests for each of the 18 remaining services
- [ ] Focus on critical services first (keycloak, mariadb, postgres, etc.)
- [ ] Automate test generation from specs

**Priority Order:**
1. **Critical Infrastructure** (Keycloak, MariaDB, PostgreSQL, Redis, MinIO)
2. **Core Services** (Nextcloud, Element, SOGo, OpenCloud)
3. **Collaboration** (Etherpad, Cryptpad, BigBlueButton, Jitsi)
4. **Productivity** (Moodle, ILIAS, BookStack, LimeSurvey)
5. **Support** (Zammad, Collabora, Draw.io, Excalidraw)

#### 1.3 Create Platform-Level Tests
**Current:** No platform tests

**Target:** 15+ platform tests

**Platform Test Categories:**
1. **Deployment Tests**
   - Helm chart validation
   - Kubernetes resource limits
   - Affinity/anti-affinity rules
   - PDB (Pod Disruption Budget) verification

2. **Networking Tests**
   - Ingress configuration
   - Service mesh connectivity
   - DNS resolution
   - Load balancing

3. **Storage Tests**
   - PVC provisioning
   - Storage class validation
   - Backup/restore procedures
   - Volume mounting

4. **Security Tests**
   - Pod security policies
   - Network policies
   - RBAC permissions
   - Secret management

5. **Observability Tests**
   - Metrics collection
   - Log aggregation
   - Alerting rules
   - Dashboard validation

### 🎯 Phase 2: Automation (Medium Priority)

#### 2.1 CI/CD Integration for Pyramid Validation
**Current:** Manual testing, some CI checks

**Improvement:** Automated pyramid validation

**New CI Workflow:** `spec-pyramid-validation.yml`

```yaml
name: Spec Pyramid Validation

on:
  push:
    branches: [master, main]
    paths:
      - 'specs/**'
      - 'tests/**'
      - 'contracts/**'
  pull_request:
    branches: [master, main]

jobs:
  spec-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g ajv-cli
      - run: ajv validate -s spec-schema.json -d specs/**/index.md --all-errors

  contract-validation:
    needs: spec-validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ajv validate -s contract-schema.json -d specs/integrations/api-contracts/contracts/*.yaml

  test-coverage:
    needs: contract-validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/calculate-coverage.py
      - run: |
          COVERAGE=$(python scripts/calculate-coverage.py)
          if [ "$COVERAGE" -lt 80 ]; then
            echo "::error::Test coverage below 80% ($COVERAGE%)"
            exit 1
          fi

  contract-testing:
    needs: test-coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g newman
      - run: newman run specs/integrations/api-contracts/tests/*.yaml

  interconnection-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/validate-interconnections.py
```

#### 2.2 Automated Test Generation
**Current:** Manual test creation

**Improvement:** Generate test stubs from specs

**Script:** `scripts/generate-tests.py`

```python
#!/usr/bin/env python3
"""Generate test stubs from specification files."""

import os
import re
import yaml

def extract_requirements(spec_content):
    """Extract testable requirements from spec."""
    requirements = []
    
    # Find all requirement sections
    sections = re.split(r'^## ', spec_content, flags=re.MULTILINE)
    
    for section in sections:
        if section.startswith('Requirements'):
            # Extract numbered requirements
            reqs = re.findall(r'^\d+\. (.+)$', section, re.MULTILINE)
            requirements.extend(reqs)
    
    return requirements

def generate_test_stub(service_name, requirements):
    """Generate a test YAML stub."""
    test = {
        'suite': f'{service_name} specification validation',
        'templates': ['deployment.yaml'],
        'tests': []
    }
    
    for i, req in enumerate(requirements, 1):
        test['tests'].append({
            'it': f'should satisfy requirement {i}: {req}',
            'release': {'name': service_name},
            'asserts': [
                {
                    'containsDocument': {
                        'kind': 'Deployment',
                        'apiVersion': 'apps/v1'
                    }
                }
            ]
        })
    
    return yaml.dump(test, sort_keys=False)

def main():
    spec_dir = 'specs/services'
    
    for service in os.listdir(spec_dir):
        spec_path = os.path.join(spec_dir, service, 'index.md')
        test_dir = os.path.join(spec_dir, service, 'tests')
        
        if os.path.exists(spec_path) and not os.path.exists(test_dir):
            with open(spec_path, 'r') as f:
                content = f.read()
            
            requirements = extract_requirements(content)
            
            if requirements:
                os.makedirs(test_dir, exist_ok=True)
                test_content = generate_test_stub(service, requirements)
                
                with open(os.path.join(test_dir, f'{service}_spec_test.yaml'), 'w') as f:
                    f.write(test_content)
                
                print(f"✅ Generated test stub for {service} ({len(requirements)} requirements)")

if __name__ == '__main__':
    main()
```

#### 2.3 Test Coverage Dashboard
**Current:** Manual tracking in test-coverage-gaps

**Improvement:** Automated dashboard

**Script:** `scripts/generate-coverage-report.py`

```python
#!/usr/bin/env python3
"""Generate test coverage report."""

import os
import json
from collections import defaultdict

def get_all_specs():
    """Get all specification files."""
    specs = {}
    for root, dirs, files in os.walk('specs'):
        if '_registry' in root:
            continue
        for file in files:
            if file == 'index.md':
                path = root.replace('specs/', '').replace('/', '.')
                specs[path] = {'spec': os.path.join(root, file)}
    return specs

def get_all_tests():
    """Get all test files."""
    tests = []
    for root, dirs, files in os.walk('specs'):
        for file in files:
            if file.endswith(('_test.yaml', '_test.yml', '-test.yaml', '-test.yml')):
                tests.append(os.path.join(root, file))
    return tests

def map_tests_to_specs(specs, tests):
    """Map test files to their corresponding specs."""
    test_mapping = defaultdict(list)
    
    for test in tests:
        # Extract service from path
        parts = test.replace('specs/', '').split('/')
        if len(parts) >= 2:
            spec_key = parts[0]
            if spec_key in specs:
                test_mapping[spec_key].append(test)
    
    return test_mapping

def generate_report(specs, test_mapping):
    """Generate coverage report."""
    report = {
        'total_specs': len(specs),
        'total_tests': sum(len(t) for t in test_mapping.values()),
        'coverage': {},
        'summary': {
            'with_tests': 0,
            'without_tests': 0,
            'coverage_percentage': 0
        }
    }
    
    for spec_key, spec_info in specs.items():
        has_tests = spec_key in test_mapping
        test_count = len(test_mapping.get(spec_key, []))
        
        report['coverage'][spec_key] = {
            'has_tests': has_tests,
            'test_count': test_count,
            'status': '✅' if has_tests else '❌'
        }
        
        if has_tests:
            report['summary']['with_tests'] += 1
        else:
            report['summary']['without_tests'] += 1
    
    total = report['summary']['with_tests'] + report['summary']['without_tests']
    if total > 0:
        report['summary']['coverage_percentage'] = \
            (report['summary']['with_tests'] / total) * 100
    
    return report

def print_report(report):
    """Print coverage report."""
    print("=" * 80)
    print("SPEC-CONTRACT-TEST COVERAGE REPORT")
    print("=" * 80)
    print(f"\nTotal Specifications: {report['total_specs']}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Coverage: {report['summary']['coverage_percentage']:.1f}%")
    print(f"\nWith Tests: {report['summary']['with_tests']}")
    print(f"Without Tests: {report['summary']['without_tests']}")
    
    print("\n" + "-" * 80)
    print("DETAILED COVERAGE:")
    print("-" * 80)
    
    for spec_key, info in sorted(report['coverage'].items()):
        status = info['status']
        test_count = info['test_count']
        print(f"{status} {spec_key}: {test_count} tests")

if __name__ == '__main__':
    specs = get_all_specs()
    tests = get_all_tests()
    test_mapping = map_tests_to_specs(specs, tests)
    report = generate_report(specs, test_mapping)
    print_report(report)
    
    # Save as JSON
    with open('coverage-report.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### 🎯 Phase 3: Advanced (Low Priority / Future)

#### 3.1 Contract Testing with Pact
**Current:** No formal contract testing

**Improvement:** Use Pact for contract testing

**Implementation:**
```yaml
# specs/integrations/api-contracts/pact-config.yaml
provider: nextcloud
consumer: element
pact_file: pacts/nextcloud-element.json

# Run with:
# pact-provider-verifier --provider-base-url http://nextcloud:8080"
```

#### 3.2 OpenAPI/Swagger Integration
**Current:** Custom contract format

**Improvement:** Use OpenAPI 3.0 standard

**Benefits:**
- Standard format for API definitions
- Built-in validation tools
- Automatic documentation generation
- Mock server generation

#### 3.3 Property-Based Testing
**Current:** Example-based tests

**Improvement:** Property-based tests with Schemathesis

```python
# test_user_provisioning.py
from schemathesis import Case

@case("user_provisioning_schemas.yaml")
def test_user_provisioning(case: Case):
    case.call_and_validate()
```

#### 3.4 Performance Testing
**Current:** No performance tests

**Improvement:** Add performance benchmarks

**Test Types:**
- Load testing (100, 1000, 10000 users)
- Stress testing (resource exhaustion)
- Soak testing (long-running)
- Spike testing (sudden load)

#### 3.5 Security Testing
**Current:** Manual security reviews

**Improvement:** Automated security scanning

**Tools:**
- OWASP ZAP for API scanning
- Trivy for container scanning
- Kubeval for Kubernetes validation
- Hadolint for Dockerfile linting

## Test Quality Metrics

### 📈 Target Metrics

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Spec Coverage | 100% | 100% | ✅ Done |
| Contract Coverage | ~2% | 100% | High |
| Unit Test Coverage | 25% | 80% | High |
| Integration Test Coverage | 0% | 60% | High |
| Contract Test Coverage | 0% | 80% | Medium |
| E2E Test Coverage | 0% | 40% | Medium |
| Test Execution Time | N/A | < 10 min | Medium |
| Test Success Rate | N/A | > 95% | High |

### 📊 Quality Gates

1. **Merge Requirements**
   - All specs must have SPDX headers
   - All contracts must be valid YAML/JSON
   - At least one test per critical service
   - No broken cross-references

2. **Release Requirements**
   - > 80% of services have tests
   - > 60% of contracts have validation tests
   - All platform specs have tests
   - Security scan passes

## Implementation Roadmap

### Month 1: Foundation
- [ ] Standardize contract definitions (split into individual files)
- [ ] Create contract schema (JSON Schema)
- [ ] Add tests for all critical infrastructure services (5 services)
- [ ] Add tests for core services (8 services)
- [ ] Create platform-level test categories

### Month 2: Automation
- [ ] Implement CI workflow for pyramid validation
- [ ] Create test generation script
- [ ] Implement coverage dashboard
- [ ] Add contract validation tests
- [ ] Add integration tests for auth flows

### Month 3: Advanced
- [ ] Implement Pact for contract testing
- [ ] Migrate to OpenAPI 3.0
- [ ] Add property-based testing
- [ ] Add performance benchmarks
- [ ] Add security scanning

### Month 4+: Optimization
- [ ] Optimize test execution time
- [ ] Improve test reliability
- [ ] Expand test coverage
- [ ] Add chaos engineering tests
- [ ] Implement canary testing

## Tooling Recommendations

### Linting & Validation
- **editorconfig-checker** - Code style enforcement
- **markdownlint** - Markdown formatting
- **yamllint** - YAML syntax validation
- **ajv** - JSON Schema validation
- **spectral** - OpenAPI linting

### Testing
- **newman** - Postman collection runner
- **pact** - Contract testing
- **schemathesis** - Property-based testing
- **k6** - Load testing
- **OWASP ZAP** - Security scanning

### Documentation
- **docusaurus** - Documentation site (already in use)
- **swagger-ui** - API documentation
- **redoc** - Alternative API documentation

### CI/CD
- **GitHub Actions** - CI/CD (already configured)
- **_forgejo Actions_ - Self-hosted CI
- **ArgoCD** - GitOps deployment
- **Renovate** - Dependency updates

## Success Criteria

### 🎯 Short-term (3 months)
- [ ] All 24 services have at least one test
- [ ] All platform specs have tests
- [ ] 30+ contracts defined
- [ ] CI workflow validates pyramid
- [ ] 60% test coverage

### 🎯 Medium-term (6 months)
- [ ] 80% test coverage
- [ ] Contract testing implemented
- [ ] Integration tests for all auth methods
- [ ] Performance benchmarks established
- [ ] Security scanning in CI

### 🎯 Long-term (12 months)
- [ ] 95% test coverage
- [ ] Full contract testing with Pact
- [ ] Property-based testing
- [ ] Chaos engineering tests
- [ ] Automated canary testing

## Maintenance

### Regular Tasks
1. **Monthly:** Run full pyramid validation
2. **Per PR:** Validate changed specs/contracts/tests
3. **Per Release:** Generate coverage report
4. **Quarterly:** Review and update test strategy

### Quality Assurance
1. All new specs must include test requirements
2. All new contracts must have validation tests
3. All broken links must be fixed before merge
4. All SPDX headers must be present

## Conclusion

The Spec-Contract-Test Pyramid provides a structured approach to documentation and validation:

- **SPECS** define what we need
- **CONTRACTS** define how services communicate
- **TESTS** verify that it works

By systematically improving each layer and the connections between them, we can achieve:
- ✅ Better documentation
- ✅ Clearer interfaces
- ✅ More reliable deployments
- ✅ Faster troubleshooting
- ✅ Higher quality software

Implementing this framework will transform the openDesk Edu specification from a static documentation repository into a living, validated system that ensures correctness from specification to production.

---

**Next Steps:**
1. Start with Phase 1: Foundation (contract standardization + test expansion)
2. Add CI workflow for automated validation
3. Generate initial coverage report
4. Track progress against targets

**Owner:** openDesk Edu Architecture Team
**Last Updated:** 2026-07-25
**Status:** Draft
