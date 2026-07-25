#!/usr/bin/env python3
"""Calculate test coverage for the spec pyramid."""

import os
import json
from collections import defaultdict
import sys


def get_all_spec_services():
    """Get all services that have specs."""
    services = set()
    specs_dir = 'specs'
    
    if not os.path.exists(specs_dir):
        print("Error: specs/ directory not found")
        sys.exit(1)
    
    for root, dirs, files in os.walk(specs_dir):
        # Skip registry and other meta directories
        if '_registry' in root or 'tests' in root:
            continue
            
        for dir_name in dirs:
            # Services are in specs/services/*
            path_parts = root.replace('specs/', '').split('/')
            if len(path_parts) >= 1 and path_parts[0] == 'services':
                services.add(dir_name)
    
    return sorted(services)


def get_platform_specs():
    """Get all platform specs."""
    platforms = set()
    specs_dir = 'specs/platform'
    
    if os.path.exists(specs_dir):
        for item in os.listdir(specs_dir):
            item_path = os.path.join(specs_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'index.md')):
                platforms.add(item)
    
    return sorted(platforms)


def get_auth_specs():
    """Get all auth specs."""
    auths = set()
    specs_dir = 'specs/auth'
    
    if os.path.exists(specs_dir):
        for item in os.listdir(specs_dir):
            item_path = os.path.join(specs_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'index.md')):
                auths.add(item)
    
    return sorted(auths)


def get_integration_specs():
    """Get all integration specs."""
    integrations = set()
    specs_dir = 'specs/integrations'
    
    if os.path.exists(specs_dir):
        for item in os.listdir(specs_dir):
            item_path = os.path.join(specs_dir, item)
            if os.path.isdir(item_path):
                # Check if it has index.md or is a contract directory
                if os.path.exists(os.path.join(item_path, 'index.md')):
                    integrations.add(item)
    
    return sorted(integrations)


def get_services_with_tests():
    """Get all services that have test files."""
    services_with_tests = set()
    specs_dir = 'specs'
    
    for root, dirs, files in os.walk(specs_dir):
        for file in files:
            if file.endswith(('_test.yaml', '_test.yml', '-test.yaml', '-test.yml')):
                # Extract service name from path
                parts = root.replace('specs/', '').split('/')
                if len(parts) >= 2 and parts[0] == 'services':
                    services_with_tests.add(parts[1])
    
    return services_with_tests


def get_platforms_with_tests():
    """Get all platform specs with tests."""
    platforms = set()
    specs_dir = 'specs/platform'
    
    if os.path.exists(specs_dir):
        for root, dirs, files in os.walk(specs_dir):
            for file in files:
                if file.endswith(('_test.yaml', '_test.yml', '-test.yaml', '-test.yml')):
                    parts = root.replace('specs/platform/', '').split('/')
                    if parts[0]:
                        platforms.add(parts[0])
    
    return platforms


def get_all_yaml_tests():
    """Get all YAML test files."""
    tests = []
    for root, dirs, files in os.walk('specs'):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                if '_test' in file or '-test' in file or '/tests/' in root:
                    tests.append(os.path.join(root, file))
    
    return tests


def calculate_coverage():
    """Calculate coverage percentages."""
    # Get all specs
    services = get_all_spec_services()
    platforms = get_platform_specs()
    auths = get_auth_specs()
    integrations = get_integration_specs()
    
    total_specs = len(services) + len(platforms) + len(auths) + len(integrations)
    
    # Get specs with tests
    services_with_tests = get_services_with_tests()
    platforms_with_tests = get_platforms_with_tests()
    
    # For auth and integrations, check differently
    auths_with_tests = set()
    integrations_with_tests = set()
    
    # Check auth tests
    for root, dirs, files in os.walk('specs/auth'):
        for file in files:
            if file.endswith(('_test.yaml', '_test.yml')):
                parts = root.replace('specs/auth/', '').split('/')
                if parts[0]:
                    auths_with_tests.add(parts[0])
    
    # Check integration tests
    for root, dirs, files in os.walk('specs/integrations'):
        for file in files:
            if file.endswith(('_test.yaml', '_test.yml')):
                parts = root.replace('specs/integrations/', '').split('/')
                if parts[0]:
                    integrations_with_tests.add(parts[0])
    
    # Calculate totals
    specs_with_tests = (
        len(services_with_tests) +
        len(platforms_with_tests) +
        len(auths_with_tests) +
        len(integrations_with_tests)
    )
    
    # Count yaml tests
    yaml_tests = get_all_yaml_tests()
    
    # Calculate percentages
    service_coverage = (len(services_with_tests) / len(services) * 100) if services else 0
    platform_coverage = (len(platforms_with_tests) / len(platforms) * 100) if platforms else 0
    auth_coverage = (len(auths_with_tests) / len(auths) * 100) if auths else 0
    integration_coverage = (len(integrations_with_tests) / len(integrations) * 100) if integrations else 0
    overall_coverage = (specs_with_tests / total_specs * 100) if total_specs > 0 else 0
    
    return {
        'summary': {
            'total_specs': total_specs,
            'total_tests': len(yaml_tests),
            'specs_with_tests': specs_with_tests,
            'overall_coverage': round(overall_coverage, 1)
        },
        'by_category': {
            'services': {
                'total': len(services),
                'with_tests': len(services_with_tests),
                'coverage': round(service_coverage, 1),
                'items': sorted(services),
                'tested': sorted(services_with_tests),
                'untested': sorted(set(services) - services_with_tests)
            },
            'platform': {
                'total': len(platforms),
                'with_tests': len(platforms_with_tests),
                'coverage': round(platform_coverage, 1),
                'items': sorted(platforms),
                'tested': sorted(platforms_with_tests),
                'untested': sorted(set(platforms) - platforms_with_tests)
            },
            'auth': {
                'total': len(auths),
                'with_tests': len(auths_with_tests),
                'coverage': round(auth_coverage, 1),
                'items': sorted(auths),
                'tested': sorted(auths_with_tests),
                'untested': sorted(set(auths) - auths_with_tests)
            },
            'integrations': {
                'total': len(integrations),
                'with_tests': len(integrations_with_tests),
                'coverage': round(integration_coverage, 1),
                'items': sorted(integrations),
                'tested': sorted(integrations_with_tests),
                'untested': sorted(set(integrations) - integrations_with_tests)
            }
        },
        'test_files': sorted(yaml_tests)
    }


def print_coverage_report(coverage):
    """Print a formatted coverage report."""
    print("\n" + "=" * 80)
    print("SPEC-CONTRACT-TEST PYRAMID COVERAGE REPORT")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 40)
    print(f"Total Specifications:    {coverage['summary']['total_specs']}")
    print(f"Total YAML Tests:        {coverage['summary']['total_tests']}")
    print(f"Specifications Tested:   {coverage['summary']['specs_with_tests']}")
    print(f"Overall Coverage:        {coverage['summary']['overall_coverage']}%")
    
    # By Category
    print("\n📁 COVERAGE BY CATEGORY")
    print("-" * 40)
    
    for category, data in coverage['by_category'].items():
        print(f"\n{category.capitalize()}:")
        print(f"  Total: {data['total']} | Tested: {data['with_tests']} | Coverage: {data['coverage']}%")
        if data['untested']:
            print(f"  ⚠️  Untested: {', '.join(data['untested'])}")
        else:
            print(f"  ✅ All tested!")
    
    # Detailed untracked
    print("\n📄 TEST FILES")
    print("-" * 40)
    for test_file in coverage['test_files']:
        print(f"  • {test_file}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Return coverage percentage for CI
    return coverage['summary']['overall_coverage']


if __name__ == '__main__':
    coverage = calculate_coverage()
    percentage = print_coverage_report(coverage)
    
    # Exit with error if coverage is below threshold
    if len(sys.argv) > 1 and sys.argv[1] == '--ci':
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0
        if percentage < threshold:
            print(f"::error::Test coverage {percentage}% is below threshold {threshold}%")
            sys.exit(1)
    
    # Save JSON report
    with open('coverage-report.json', 'w') as f:
        json.dump(coverage, f, indent=2)
