#!/usr/bin/env python3
"""Validate learning paths structure and links."""

import os
import re
from pathlib import Path

def find_markdown_files(directory):
    """Find all .md files in learning-paths."""
    return list(Path(directory).rglob('*.md'))

def extract_links(content):
    """Extract markdown links from content."""
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, content)

def validate_links(root_path, md_files):
    """Check if all linked files exist."""
    errors = []

    for md_file in md_files:
        with open(md_file) as f:
            content = f.read()

        links = extract_links(content)
        for text, path in links:
            # Skip external links and anchors
            if path.startswith(('http://', 'https://', '#')):
                continue

            # Resolve relative path
            full_path = (md_file.parent / path).resolve()

            if not full_path.exists():
                errors.append(f"{md_file.name}: Link broken → {path}")

    return errors

def check_file_structure(root_path):
    """Verify required files exist."""
    required = [
        'learning-paths/README.md',
        'learning-paths/index.md',
        'learning-paths/sequential-tracks/2-week-sprint.md',
        'learning-paths/sequential-tracks/4-week-focused.md',
        'learning-paths/sequential-tracks/8-week-comprehensive.md',
        'learning-paths/interview-playbooks/phone-screen.md',
        'learning-paths/interview-playbooks/technical-round.md',
        'learning-paths/interview-playbooks/system-design-round.md',
        'learning-paths/domains/arrays.md',
        'learning-paths/domains/strings.md',
        'learning-paths/domains/linked-lists.md',
        'learning-paths/domains/stacks-queues.md',
        'learning-paths/domains/trees.md',
        'learning-paths/domains/graphs.md',
        'learning-paths/domains/heaps.md',
        'learning-paths/domains/hash-tables.md',
        'learning-paths/domains/dynamic-programming.md',
        'learning-paths/domains/sorting-searching.md',
        'learning-paths/domains/bit-manipulation.md',
        'learning-paths/domains/design-patterns.md',
        'learning-paths/domains/system-design-fundamentals.md',
        'learning-paths/skill-trees/depth-first.md',
        'learning-paths/skill-trees/breadth-first.md',
    ]

    missing = []
    for file_path in required:
        full_path = Path(root_path) / file_path
        if not full_path.exists():
            missing.append(file_path)

    return missing

if __name__ == '__main__':
    root = '/home/sbisw/github/datastructures'

    print("🔍 Validating Learning Paths...")
    print("=" * 60)

    # Check file structure
    missing = check_file_structure(root)
    if missing:
        print(f"\n❌ Missing files ({len(missing)}):")
        for f in missing:
            print(f"  - {f}")
    else:
        print("\n✅ All required files present")

    # Validate links
    md_files = find_markdown_files(Path(root) / 'learning-paths')
    errors = validate_links(root, md_files)

    if errors:
        print(f"\n❌ Link errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ All links valid")

    print()
    print("=" * 60)
    print(f"✓ Validated {len(md_files)} markdown files")

    if missing or errors:
        print("\n⚠️  Fix errors above before proceeding")
        exit(1)
    else:
        print("\n✨ Learning paths validation complete!")
        exit(0)
