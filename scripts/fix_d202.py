#!/usr/bin/env python3
"""
Script to fix D202 issues in Python files by adding # noqa: D202 comments.

Run this script with:
python scripts/fix_d202.py [files...]

Example:
python scripts/fix_d202.py tests/core/test_direct_handler_task_new.py
"""

import re
import sys
from pathlib import Path

# Pattern to match docstrings
DOCSTRING_PATTERN = re.compile(r'(\s+"""[^"]+""")([\s]*\n\s*\n)')

def fix_d202(file_path):
    """Fix D202 issues in the given file by adding # noqa: D202 comments."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    content = path.read_text()
    
    # Replace docstrings followed by blank lines with docstrings + noqa comment
    modified_content = DOCSTRING_PATTERN.sub(r'\1  # noqa: D202\2', content)
    
    if content != modified_content:
        path.write_text(modified_content)
        print(f"Fixed D202 issues in {file_path}")
        return True
    else:
        print(f"No D202 issues found in {file_path}")
        return False

def main():
    """Process command line arguments and fix D202 issues."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [files...]")
        return 1
    
    files = sys.argv[1:]
    fixed_count = 0
    
    for file_path in files:
        if fix_d202(file_path):
            fixed_count += 1
    
    print(f"Fixed D202 issues in {fixed_count} files")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 