#!/usr/bin/env python3
"""Audit existing problems in repo and map to domains."""

import os
import csv
from pathlib import Path

# Domain mappings (infer from directory/file structure)
DOMAIN_KEYWORDS = {
    'array': 'arrays',
    'string': 'strings',
    'linked_list': 'linked-lists',
    'stack': 'stacks-queues',
    'queue': 'stacks-queues',
    'deque': 'stacks-queues',
    'tree': 'trees',
    'bst': 'trees',
    'avl': 'trees',
    'trie': 'trees',
    'graph': 'graphs',
    'heap': 'heaps',
    'hash': 'hash-tables',
    'hashmap': 'hash-tables',
    'dp': 'dynamic-programming',
    'dynamic_programming': 'dynamic-programming',
    'sort': 'sorting-searching',
    'search': 'sorting-searching',
    'bit': 'bit-manipulation',
    'design': 'design-patterns',
}

def infer_domain(filename):
    """Infer domain from filename."""
    filename_lower = filename.lower()
    for keyword, domain in DOMAIN_KEYWORDS.items():
        if keyword in filename_lower:
            return domain
    return 'uncategorized'

def scan_problems():
    """Scan all problem implementations in repo."""
    problems = []
    repo_root = Path('/home/sbisw/github/interviewprep')

    # Scan Python implementations
    python_dir = repo_root / 'python'
    if python_dir.exists():
        for py_file in python_dir.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue
            domain = infer_domain(py_file.name)
            problems.append({
                'name': py_file.stem,
                'domain': domain,
                'language': 'python',
                'path': str(py_file.relative_to(repo_root)),
                'difficulty': 'unknown',  # Will be manual
                'time_estimate': 'unknown',  # Will be manual
                'stages': '',  # Will be manual
            })

    # Scan Java implementations
    java_dir = repo_root / 'java'
    if java_dir.exists():
        for java_file in java_dir.rglob('*.java'):
            domain = infer_domain(java_file.name)
            # Check if Python version already added this
            stem = java_file.stem.lower()
            if not any(p['name'].lower() == stem and p['domain'] == domain for p in problems):
                problems.append({
                    'name': java_file.stem,
                    'domain': domain,
                    'language': 'java',
                    'path': str(java_file.relative_to(repo_root)),
                    'difficulty': 'unknown',
                    'time_estimate': 'unknown',
                    'stages': '',
                })

    return problems

def write_csv(problems):
    """Write problems to CSV."""
    with open('_problem_map.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'domain', 'language', 'path', 'difficulty',
            'time_estimate', 'stages', 'notes'
        ])
        writer.writeheader()
        for p in problems:
            p['notes'] = ''
            writer.writerow(p)

if __name__ == '__main__':
    problems = scan_problems()
    write_csv(problems)
    print(f"Scanned {len(problems)} problems. See _problem_map.csv")
    # Print summary
    domains = {}
    for p in problems:
        d = p['domain']
        domains[d] = domains.get(d, 0) + 1
    print("\nProblems by domain:")
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count}")
