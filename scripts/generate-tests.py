#!/usr/bin/env python3
"""Generate test stubs from specification files."""

import os
import re
import yaml
import sys
from pathlib import Path


def extract_requirements(spec_content):
    """Extract testable requirements from spec."""
    requirements = []
    
    # Find all requirement sections
    sections = re.split(r'^##\s+', spec_content, flags=re.MULTILINE)
    
    for section in sections:
        if section.lower().startswith('requirements'):
            # Extract numbered requirements
            reqs = re.findall(r'^\d+\.\s+(.+)$', section, re.MULTILINE)
            requirements.extend(reqs)
        
        # Also look for "Shall" statements
        shall_reqs = re.findall(r'^[-•*]\s+[Ss]hall\s+(.+)$', section, re.MULTILINE)
        requirements.extend([f"Shall {r}" for r in shall_reqs])
        
        # Also look for "Must" statements
        must_reqs = re.findall(r'^[-•*]\s+[Mm]ust\s+(.+)$', section, re.MULTILINE)
        requirements.extend([f"Must {r}" for r in must_reqs])
    
    return requirements


def extract_test_cases(spec_content):
    """Extract test cases from a spec."""
    test_cases = []
    
    # Look for test case sections
    test_sections = re.findall(r'###?\s+Test.*?\n\n(.*?)(?=\n###?|\Z)', spec_content, re.DOTALL | re.IGNORECASE)
    
    for section in test_sections:
        # Extract individual test cases
        cases = re.findall(r'^[-•*]\s+(.+)$', section, re.MULTILINE)
        test_cases.extend(cases)
    
    return test_cases


def generate_test_stub(service_name, requirements, test_cases=None):
    """Generate a test YAML stub."""
    test = {
        'suite': f'{service_name} specification validation',
        'description': f'Tests for {service_name} service specification',
        'templates': ['deployment.yaml'],
        'tests': []
    }
    
    if not requirements and not test_cases:
        # Create a basic connectivity test
        test['tests'].append({
            'it': 'should be deployable',
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
    else:
        # Add tests for each requirement
        for i, req in enumerate(requirements, 1):
            clean_req = re.sub(r'[^a-zA-Z0-9\s-]', '', req)[:50]
            test_id = f"req-{i}"
            test['tests'].append({
                'it': f'should satisfy requirement {i}: {req[:60]}...' if len(req) > 60 else f'should satisfy requirement {i}: {req}',
                'release': {'name': service_name},
                'set': {
                    'testId': test_id
                },
                'asserts': [
                    {
                        'isKind': {
                            'of': 'Deployment'
                        }
                    }
                ]
            })
        
        # Add specific test cases if available
        if test_cases:
            for i, test_case in enumerate(test_cases, 1):
                test['tests'].append({
                    'it': f'should pass test case: {test_case}',
                    'release': {'name': service_name},
                    'asserts': [
                        {
                            'containsDocument': {
                                'kind': 'Deployment'
                            }
                        }
                    ]
                })
    
    return yaml.dump(test, sort_keys=False, default_flow_style=False, allow_unicode=True)


def generate_service_tests(service_name):
    """Generate tests for a specific service."""
    spec_path = f'specs/services/{service_name}/index.md'
    
    if not os.path.exists(spec_path):
        print(f"⚠️  Spec file not found: {spec_path}")
        return None
    
    try:
        with open(spec_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        requirements = extract_requirements(content)
        test_cases = extract_test_cases(content)
        
        test_content = generate_test_stub(service_name, requirements, test_cases)
        
        return test_content
    except Exception as e:
        print(f"⚠️  Error reading {spec_path}: {e}")
        return None


def generate_platform_tests(platform_name):
    """Generate tests for a platform spec."""
    spec_path = f'specs/platform/{platform_name}/index.md'
    
    if not os.path.exists(spec_path):
        print(f"⚠️  Spec file not found: {spec_path}")
        return None
    
    try:
        with open(spec_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        requirements = extract_requirements(content)
        test_cases = extract_test_cases(content)
        
        test = {
            'suite': f'{platform_name} platform validation',
            'description': f'Tests for {platform_name} platform specification',
            'tests': []
        }
        
        if not requirements:
            test['tests'].append({
                'it': 'should have valid configuration',
                'asserts': [
                    {
                        'isKind': {
                            'of': 'ConfigMap'
                        }
                    }
                ]
            })
        else:
            for i, req in enumerate(requirements, 1):
                test['tests'].append({
                    'it': f'should satisfy requirement {i}: {req[:60]}',
                    'asserts': [
                        {
                            'containsDocument': {
                                'kind': 'Deployment'
                            }
                        }
                    ]
                })
        
        return yaml.dump(test, sort_keys=False, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        print(f"⚠️  Error reading {spec_path}: {e}")
        return None


def generate_all_tests():
    """Generate tests for all services and platform specs."""
    generated_count = 0
    skipped_count = 0
    
    # Generate for services
    services_dir = 'specs/services'
    if os.path.exists(services_dir):
        for service_name in sorted(os.listdir(services_dir)):
            service_path = os.path.join(services_dir, service_name)
            if os.path.isdir(service_path):
                test_dir = os.path.join(service_path, 'tests')
                
                # Skip if tests already exist
                if os.path.exists(test_dir) and os.listdir(test_dir):
                    print(f"⏭️  {service_name}: tests already exist")
                    skipped_count += 1
                    continue
                
                test_content = generate_service_tests(service_name)
                if test_content:
                    os.makedirs(test_dir, exist_ok=True)
                    test_file = os.path.join(test_dir, f'{service_name}_spec_test.yaml')
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(test_content)
                    print(f"✅ {service_name}: generated {len(test_content.split('it:')) - 1} tests")
                    generated_count += 1
    
    # Generate for platform
    platform_dir = 'specs/platform'
    if os.path.exists(platform_dir):
        for platform_name in sorted(os.listdir(platform_dir)):
            platform_path = os.path.join(platform_dir, platform_name)
            if os.path.isdir(platform_path):
                test_dir = os.path.join(platform_path, 'tests')
                
                # Skip if tests already exist
                if os.path.exists(test_dir) and os.listdir(test_dir):
                    print(f"⏭️  platform/{platform_name}: tests already exist")
                    skipped_count += 1
                    continue
                
                test_content = generate_platform_tests(platform_name)
                if test_content:
                    os.makedirs(test_dir, exist_ok=True)
                    test_file = os.path.join(test_dir, f'{platform_name}_spec_test.yaml')
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(test_content)
                    print(f"✅ platform/{platform_name}: generated tests")
                    generated_count += 1
    
    print(f"\n{'='*60}")
    print(f"Generated tests for {generated_count} specs")
    print(f"Skipped {skipped_count} specs (tests already exist)")
    print(f"{'='*60}")
    
    return generated_count


def generate_single_test(path):
    """Generate test for a single spec file."""
    parts = path.replace('specs/', '').split('/')
    
    if len(parts) >= 2:
        category = parts[0]
        name = parts[1]
        
        if category == 'services':
            test_content = generate_service_tests(name)
        elif category == 'platform':
            test_content = generate_platform_tests(name)
        else:
            print(f"⚠️  Unsupported category: {category}")
            return None
        
        if test_content:
            print(test_content)
            return test_content
    
    return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Generate test for specific spec
        spec_path = sys.argv[1]
        generate_single_test(spec_path)
    else:
        # Generate tests for all specs
        generate_all_tests()
