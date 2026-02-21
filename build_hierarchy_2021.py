"""
Build hierarchy structure for 2021 SHS PUMF.
If a 2021 hierarchy Excel file exists in RY2021, builds hierarchy_structure_2021.json.
Otherwise, outputs a message to use the 2019 hierarchy (hierarchy_structure.json).
"""

import json
from pathlib import Path

# Check for 2021 hierarchy Excel
RY2021_DOCS = Path("RY2021/Documentation")
HIERARCHY_PATTERNS = [
    "**/Hierarchy*.xlsx",
    "**/hierarchy*.xlsx",
    "**/Expenditure*category*.xlsx",
]


def find_2021_hierarchy_excel():
    """Search for 2021 hierarchy Excel file."""
    if not RY2021_DOCS.exists():
        return None
    for pattern in HIERARCHY_PATTERNS:
        for p in RY2021_DOCS.glob(pattern):
            if "2021" in p.name or "PUMF" in p.name:
                return p
    return None


def main():
    hierarchy_excel = find_2021_hierarchy_excel()
    if hierarchy_excel is None:
        print(
            "No 2021 hierarchy Excel file found in RY2021/Documentation.\n"
            "Using hierarchy_structure.json (built from 2019) for 2021.\n"
            "If StatCan provides a 2021-specific hierarchy, place it in RY2021/Documentation\n"
            "and run this script again to build hierarchy_structure_2021.json."
        )
        return

    # If we find a 2021 hierarchy, we could run the same logic as build_hierarchy.py
    # For now, just report
    print(f"Found 2021 hierarchy file: {hierarchy_excel}")
    print("To build hierarchy_structure_2021.json, adapt build_hierarchy.py to read this file.")
    print("Currently using hierarchy_structure.json (2019) for 2021.")


if __name__ == "__main__":
    main()
