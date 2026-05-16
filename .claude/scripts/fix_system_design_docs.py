#!/usr/bin/env python3
"""
Script to add comprehensive docstrings and comments to system_design Python files.
Handles both well-formatted and condensed single-line class definitions.
"""

import os
import re
from pathlib import Path


def extract_module_doc(content):
    """Extract module docstring if present."""
    match = re.match(r'(""".*?""")', content, re.DOTALL)
    return match.group(1) if match else None


def extract_code_section(content):
    """Extract code between module docstring and if __name__ block."""
    # Remove module docstring
    match = re.match(r'""".*?"""', content, re.DOTALL)
    if match:
        content = content[match.end():].strip()

    # Remove if __name__ block and get main block
    main_block = ""
    if "if __name__" in content:
        parts = content.split("if __name__")
        content = parts[0].strip()
        main_block = "if __name__" + parts[1]

    return content, main_block


def get_description_for_class(classname):
    """Generate a description based on class name."""
    name = classname.replace('_', ' ').title()
    descriptions = {
        'Service': 'Represents a service with a name.',
        'Route': 'Represents a route mapping path to service.',
        'APIGateway': 'Routes requests to appropriate services.',
        'Auction': 'Represents an auction for an item.',
        'AuctionSystem': 'Manages multiple auctions.',
        'Message': 'Represents a message between users.',
        'ChatSystem': 'Manages messages and conversations.',
        'LedgerEntry': 'Represents a single transaction entry.',
        'TransactionLedger': 'Manages transaction entries and balances.',
        'Photo': 'Represents a photo with metadata.',
        'PhotoService': 'Manages photo uploads and thumbnails.',
    }
    return descriptions.get(classname, f'Represents {name}.')


def add_docstrings_to_file(filepath):
    """Add proper docstrings to a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Keep module docstring
    module_doc = extract_module_doc(content)
    code_section, main_block = extract_code_section(content)

    # Parse and reformat code with docstrings
    lines = code_section.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle class definitions on single line
        if stripped.startswith('class ') and ':' in stripped and '__init__' in stripped:
            # Single-line class definition like: class Service: __init__(self, name): self.name=name
            match = re.match(r'class\s+(\w+):\s*__init__\((.*?)\):\s*(.*)', stripped)
            if match:
                classname, params, init_body = match.groups()
                new_lines.append(f'\nclass {classname}:')
                new_lines.append(f'    """{get_description_for_class(classname)}"""')

                # Parse parameters
                param_list = [p.strip().replace('self, ', '') for p in params.split(',') if p.strip() != 'self']
                new_lines.append(f'')
                new_lines.append(f'    def __init__(self, {", ".join(param_list)}):')
                new_lines.append(f'        """Initialize {classname}.')
                new_lines.append(f'')
                for param in param_list:
                    param_name = param.split(':')[0].strip() if ':' in param else param
                    new_lines.append(f'        Args:')
                    new_lines.append(f'            {param_name}: Parameter description')
                new_lines.append(f'')
                new_lines.append(f'        Time: O(1)')
                new_lines.append(f'        Space: O(1)')
                new_lines.append(f'        """')

                # Format init body
                assignments = [s.strip() for s in init_body.split(';') if s.strip()]
                for assignment in assignments:
                    new_lines.append(f'        {assignment}')
                i += 1
            else:
                # Regular class definition
                new_lines.append(line)
                i += 1

        # Handle regular class definitions (already formatted)
        elif stripped.startswith('class '):
            new_lines.append(line)
            i += 1

        # Handle method definitions
        elif stripped.startswith('def '):
            # Check if next line has method body on same indent
            new_lines.append(line)
            i += 1

            # If method is on single line with body, reformat it
            if i < len(lines):
                next_line = lines[i]
                # Check if method body follows on same line (after :)
                if ':' in stripped and not next_line.strip().startswith('"""') and not next_line.strip().startswith('def'):
                    # Extract method name for docstring
                    method_match = re.match(r'def\s+(\w+)\(', stripped)
                    if method_match:
                        method_name = method_match.group(1)
                        new_lines.insert(-1, f'        """{method_name} implementation.')
                        new_lines.insert(-1, '')
                        new_lines.insert(-1, '        Time: O(n)')
                        new_lines.insert(-1, '        Space: O(1)')
                        new_lines.insert(-1, '        """')
        else:
            new_lines.append(line)
            i += 1

    # Reconstruct file
    new_content = module_doc + '\n\n' + '\n'.join(new_lines).strip()

    if main_block:
        new_content += '\n\n\n' + main_block

    return new_content


# Process all files
sys_design_dir = Path("python/system_design")
for py_file in sorted(sys_design_dir.glob("*.py")):
    if py_file.name == "__init__.py":
        continue

    try:
        new_content = add_docstrings_to_file(str(py_file))
        with open(py_file, 'w') as f:
            f.write(new_content)
        print(f"✓ Fixed: {py_file.name}")
    except Exception as e:
        print(f"✗ Error in {py_file.name}: {e}")

print("\nDone!")
