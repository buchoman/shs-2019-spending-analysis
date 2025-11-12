"""
Detailed analysis of hierarchy to determine items that balance with TC001.
Uses the Excel file directly to understand parent-child relationships via path structure.
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

# Read the hierarchy Excel file
hierarchy_file = Path('SHS_EDM_2019/Documentation/Expenditure category hierarchy/Hierarchy of expenditure categories, PUMF 2019.xlsx')

print("Reading hierarchy file...")
df = pd.read_excel(hierarchy_file, header=6)

# Extract hierarchy structure with path information
hierarchy_data = []
for i in range(len(df)):
    row = df.iloc[i]
    try:
        level = int(row.iloc[0]) if pd.notna(row.iloc[0]) else None
    except (ValueError, TypeError):
        continue
    if level is None:
        continue
    
    # Get variable name from last column
    var_name = str(row.iloc[-1]).strip() if pd.notna(row.iloc[-1]) else None
    if var_name is None or var_name == 'nan':
        continue
    
    # Extract variable code
    import re
    match = re.match(r'^([A-Z]+\d+[A-Z]*)', var_name)
    if match:
        var_code = match.group(1)
        
        # Get the full path through hierarchy
        # Column A (index 0) = level number
        # Column B (index 1) = Level_0 (TE001)
        # Column C (index 2) = Level_1 (TC001, etc.)
        # Column D (index 3) = Level_2 (FD001, SH001, etc.)
        # Column E (index 4) = Level_3 (FD003, FD990, etc.)
        # Column F (index 5) = Level_4 (FD100, FD200, etc.)
        path = []
        for col_idx in range(1, 8):  # Columns B through H (Level_0 through Level_6)
            val = row.iloc[col_idx]
            if pd.notna(val) and str(val).strip():
                path.append(str(val).strip())
        
        # Extract description
        desc_match = re.match(r'^[A-Z]+\d+[A-Z]*\s*-\s*(.+)', var_name)
        description = desc_match.group(1) if desc_match else var_name
        
        hierarchy_data.append({
            'level': level,
            'var_code': var_code,
            'var_name': var_name,
            'description': description,
            'path': path
        })

print(f"Total variables found: {len(hierarchy_data)}")

# Build proper parent-child relationships using path structure
var_to_node = {}
for item in hierarchy_data:
    var_code = item['var_code']
    level = item['level']
    path = item['path']
    
    # Find parent: parent should be at level-1 with path that is prefix of current path
    parent = None
    if level > 0:
        for other_item in hierarchy_data:
            if other_item['level'] == level - 1:
                other_path = other_item['path']
                # Parent path should be a prefix of current path
                if len(other_path) < len(path):
                    if other_path == path[:len(other_path)]:
                        parent = other_item['var_code']
                        break
    
    var_to_node[var_code] = {
        'var_code': var_code,
        'level': level,
        'description': item['description'],
        'var_name': item['var_name'],
        'parent': parent,
        'children': [],
        'path': path
    }

# Build children lists
for var_code, node in var_to_node.items():
    if node['parent'] and node['parent'] in var_to_node:
        var_to_node[node['parent']]['children'].append(var_code)

# Group by level
level_vars = defaultdict(list)
for var_code, node in var_to_node.items():
    level_vars[node['level']].append(var_code)

# Sort each level
for level in level_vars:
    level_vars[level].sort()

print("\n" + "="*80)
print("HIERARCHY STRUCTURE WITH PARENT-CHILD RELATIONSHIPS")
print("="*80)

# Show structure
print("\nLevel 1 (Direct children of TE001):")
for var in sorted(level_vars.get(1, [])):
    node = var_to_node[var]
    print(f"  {var}: {node['description']}")

print("\nLevel 2 (Major categories - children of TC001):")
for var in sorted(level_vars.get(2, [])):
    node = var_to_node[var]
    children = [c for c in node['children'] if var_to_node[c]['level'] == 3]
    print(f"  {var}: {node['description']} -> {len(children)} Level 3 children")

print("\nLevel 3 items (Subcategories):")
level3_count = 0
for var in sorted(level_vars.get(3, [])):
    node = var_to_node[var]
    children = [c for c in node['children'] if var_to_node[c]['level'] == 4]
    if children:
        print(f"  {var}: {node['description']} -> {len(children)} Level 4 children")
        level3_count += 1
    if level3_count >= 10:
        break

# Determine which items to include
print("\n" + "="*80)
print("DETERMINING ITEMS TO INCLUDE FOR TC001 BALANCE (MAX LEVEL 4)")
print("="*80)

items_to_include = set()
items_to_exclude = set()  # Parent totals

# Strategy: For each Level 2 category, find the most detailed items (up to Level 4)
# Include Level 4 if available, otherwise Level 3, otherwise Level 2

print("\nAnalyzing each Level 2 category:\n")

for level2_var in sorted(level_vars.get(2, [])):
    level2_node = var_to_node[level2_var]
    print(f"\n{level2_var} ({level2_node['description']}):")
    
    # Get Level 3 children
    level3_children = [c for c in level2_node['children'] 
                      if var_to_node[c]['level'] == 3]
    
    if not level3_children:
        # No Level 3 children, use Level 2 itself
        items_to_include.add(level2_var)
        print(f"  -> Include Level 2: {level2_var} (no Level 3 children)")
    else:
        # Process each Level 3 child
        for level3_var in sorted(level3_children):
            level3_node = var_to_node[level3_var]
            
            # Get Level 4 children
            level4_children = [c for c in level3_node['children'] 
                              if var_to_node[c]['level'] == 4]
            
            if not level4_children:
                # No Level 4 children, use Level 3
                items_to_include.add(level3_var)
                print(f"  -> Include Level 3: {level3_var} ({level3_node['description']})")
            else:
                # Has Level 4 children, include all Level 4 and exclude Level 3 parent
                items_to_exclude.add(level3_var)
                for level4_var in sorted(level4_children):
                    items_to_include.add(level4_var)
                    level4_node = var_to_node[level4_var]
                print(f"  -> Include {len(level4_children)} Level 4 items, exclude Level 3: {level3_var}")
                for level4_var in sorted(level4_children)[:3]:  # Show first 3
                    print(f"      - {level4_var}: {var_to_node[level4_var]['description']}")
                if len(level4_children) > 3:
                    print(f"      ... and {len(level4_children) - 3} more")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

included_by_level = defaultdict(list)
for var in items_to_include:
    level = var_to_node[var]['level']
    included_by_level[level].append(var)

print(f"\nTotal items to include: {len(items_to_include)}")
print(f"Total parent items to exclude: {len(items_to_exclude)}")

print("\nItems to include by level:")
for level in sorted(included_by_level.keys()):
    vars_at_level = sorted(included_by_level[level])
    print(f"\n  Level {level}: {len(vars_at_level)} items")
    for var in vars_at_level:
        node = var_to_node[var]
        print(f"    {var}: {node['description']}")

print(f"\n\nItems to exclude (parent totals):")
for var in sorted(items_to_exclude):
    node = var_to_node[var]
    print(f"  {var}: {node['description']} (sum of Level 4 children)")

# Save recommendations
recommendations = {
    'items_to_include': sorted(list(items_to_include)),
    'items_to_exclude': sorted(list(items_to_exclude)),
    'included_by_level': {str(k): sorted(v) for k, v in included_by_level.items()},
    'excluded_items': sorted(list(items_to_exclude)),
    'strategy': 'Include Level 4 items where available, otherwise Level 3, otherwise Level 2. Maximum level: 4.',
    'max_level': 4,
    'total_items': len(items_to_include)
}

with open('hierarchy_balance_recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f"\n\nRecommendations saved to: hierarchy_balance_recommendations.json")
print("\n" + "="*80)

