#!/usr/bin/env python3
"""Validate service interconnections based on interconnection matrix."""

import os
import yaml
import json
import sys
from collections import defaultdict


def load_interconnection_matrix():
    """Load the interconnection matrix."""
    matrix_file = 'specs/_registry/interconnection-matrix/index.md'
    
    if not os.path.exists(matrix_file):
        print(f"Warning: {matrix_file} not found")
        return {}
    
    # Try to parse as YAML or JSON embedded in markdown
    with open(matrix_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Try to extract YAML/JSON from code blocks
    import re
    
    # Try YAML first
    yaml_matches = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)
    if yaml_matches:
        try:
            return yaml.safe_load(yaml_matches[0])
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in matrix: {e}")
    
    # Try JSON
    json_matches = re.findall(r'```json\n(.*?)```', content, re.DOTALL)
    if json_matches:
        try:
            return json.loads(json_matches[0])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in matrix: {e}")
    
    # If it's pure YAML/JSON
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        pass
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    return {}


def parse_markdown_table(content):
    """Parse markdown table from content."""
    lines = content.split('\n')
    matrix = {}
    headers = []
    
    in_table = False
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('|') and not stripped.startswith('|---'):
            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            
            if not in_table:
                headers = cells[1:]  # Skip first column (service name)
                in_table = True
            else:
                service = cells[0]
                connections = cells[1:]
               (matrix[service] if service in matrix else matrix.setdefault(service, {}))['connections'] = {}
                
                for i, conn in enumerate(connections):
                    if i < len(headers) and conn:
                        matrix[service]['connections'][headers[i]] = conn
    
    return matrix


def get_all_services():
    """Get all services from specs."""
    services = set()
    for root, dirs, files in os.walk('specs'):
        parts = root.replace('specs/', '').split('/')
        if len(parts) >= 2 and parts[0] == 'services':
            services.add(parts[1])
    return sorted(services)


def get_spec_dependencies(spec_content):
    """Extract dependencies from a spec file."""
    dependencies = set()
    
    # Look for dependency sections
    import re
    
    # Find dependencies in markdown
    deps = re.findall(r'- \[(.+?)\].*?\([^)]+\)', spec_content)
    dependencies.update(deps)
    
    # Find dependencies in plain text
    deps = re.findall(r'depends on (?:the )?(?:following:?)?\s*([^\n]+)', spec_content, re.IGNORECASE)
    for dep_list in deps:
        deps = re.split(r',\s*|\s+and\s+|\s+or\s+', dep_list)
        dependencies.update(d.strip() for d in deps if d.strip())
    
    # Find in requirements
    reqs = re.findall(r'^\d+\. .*?requires (.+?)[.\n]', spec_content, re.IGNORECASE | re.MULTILINE)
    for req in reqs:
        dependencies.add(req.strip())
    
    return dependencies


def validate_interconnections():
    """Validate all service interconnections."""
    issues = []
    warnings = []
    info = []
    
    # Load matrix
    matrix_file = 'specs/_registry/interconnection-matrix/index.md'
    
    if not os.path.exists(matrix_file):
        print(f"Error: {matrix_file} not found")
        sys.exit(1)
    
    with open(matrix_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Parse as markdown table
    matrix = parse_markdown_table(content)
    
    if not matrix:
        print("Error: Could not parse interconnection matrix")
        sys.exit(1)
    
    # Get all services
    all_services = get_all_services()
    
    # Check 1: All services in matrix exist
    matrix_services = set(matrix.keys())
    missing_in_specs = matrix_services - set(all_services)
    extra_in_matrix = set(all_services) - matrix_services
    
    if missing_in_specs:
        issues.append(f"Services in matrix but not in specs: {', '.join(sorted(missing_in_specs))}")
    
    if extra_in_matrix:
        warnings.append(f"Services in specs but not in matrix: {', '.join(sorted(extra_in_matrix))}")
    
    # Check 2: Validate connections are bidirectional
    connection_matrix = defaultdict(dict)
    
    for service, data in matrix.items():
        if 'connections' in data:
            for connected, conn_type in data['connections'].items():
                if connected and connected != '-':
                    connection_matrix[service][connected] = conn_type
    
    # Check for bidirectional connections
    for service_a, connections in connection_matrix.items():
        for service_b, conn_type in connections.items():
            if service_b in connection_matrix and service_a in connection_matrix[service_b]:
                conn_type_b = connection_matrix[service_b][service_a]
                if conn_type != conn_type_b:
                    warnings.append(
                        f"Asymmetric connection: {service_a} -> {service_b} ({conn_type}) "
                        f"but {service_b} -> {service_a} ({conn_type_b})"
                    )
            elif service_b in all_services:
                # One-way connection is fine, but note it
                info.append(f"One-way connection: {service_a} -> {service_b}")
    
    # Check 3: Validate against spec dependencies
    specs_with_deps = {}
    for service in all_services:
        spec_path = f'specs/services/{service}/index.md'
        if os.path.exists(spec_path):
            try:
                with open(spec_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                deps = get_spec_dependencies(content)
                specs_with_deps[service] = deps
            except Exception as e:
                warnings.append(f"Could not read {spec_path}: {e}")
    
    # Check if matrix connections match spec dependencies
    for service, deps in specs_with_deps.items():
        if service not in matrix:
            continue
        
        matrix_connections = matrix[service].get('connections', {})
        matrix_deps = set(matrix_connections.keys()) - { '', '-' }
        
        # Check for specs deps that are not in matrix
        missing_in_matrix = deps - matrix_deps - {service}  # Remove self
        if missing_in_matrix:
            issues.append(
                f"{service} spec mentions dependencies not in matrix: {', '.join(sorted(missing_in_matrix))}"
            )
    
    # Print results
    print("\n" + "=" * 80)
    print("INTERCONNECTION VALIDATION REPORT")
    print("=" * 80)
    
    print(f"\n🔗 Services in matrix: {len(matrix_services)}")
    print(f"📦 Services in specs: {len(all_services)}")
    print(f"✅ Matching: {len(matrix_services & set(all_services))}")
    
    if issues:
        print("\n❌ ERRORS:")
        for issue in issues:
            print(f"  • {issue}")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if info:
        print("\nℹ️  INFO:")
        for info_item in info[:10]:  # Limit output
            print(f"  • {info_item}")
        if len(info) > 10:
            print(f"  ... and {len(info) - 10} more")
    
    if not issues and not warnings:
        print("\n✅ All interconnections are valid!")
    
    # Exit with error if there are issues
    if issues:
        print(f"\n❌ {len(issues)} error(s) found")
        sys.exit(1)
    
    return len(issues) == 0


if __name__ == '__main__':
    validate_interconnections()
