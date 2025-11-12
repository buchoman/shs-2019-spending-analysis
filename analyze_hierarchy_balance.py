"""
Analyze hierarchy structure to determine which items should be included
to balance with TC001 (Total Current Consumption), going up to Level 4 maximum.
"""

import pandas as pd
import json
from pathlib import Path

# Read the hierarchy Excel file
hierarchy_file = Path('SHS_EDM_2019/Documentation/Expenditure category hierarchy/Hierarchy of expenditure categories, PUMF 2019.xlsx')

print("Reading hierarchy file...")
df = pd.read_excel(hierarchy_file, header=6)

# Extract hierarchy structure with full details
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
        
        # Get the full path through hierarchy (Level_1 through Level_6)
        path = []
        for col_idx in range(2, 9):  # Columns C through I
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

# Build parent-child relationships
var_to_node = {}
for item in hierarchy_data:
    var_code = item['var_code']
    level = item['level']
    
    # Find parent by looking for item at level-1 with matching path prefix
    parent = None
    if level > 0:
        for other_item in hierarchy_data:
            if other_item['level'] == level - 1:
                other_path = other_item['path']
                current_path = item['path']
                # Check if other_path is a prefix of current_path
                if len(other_path) < len(current_path):
                    if other_path == current_path[:len(other_path)]:
                        parent = other_item['var_code']
                        break
    
    var_to_node[var_code] = {
        'var_code': var_code,
        'level': level,
        'description': item['description'],
        'var_name': item['var_name'],
        'parent': parent,
        'children': [],
        'path': item['path']
    }

# Build children lists
for var_code, node in var_to_node.items():
    if node['parent'] and node['parent'] in var_to_node:
        var_to_node[node['parent']]['children'].append(var_code)

# Group by level
level_vars = {}
for var_code, node in var_to_node.items():
    level = node['level']
    if level not in level_vars:
        level_vars[level] = []
    level_vars[level].append(var_code)

# Sort each level
for level in level_vars:
    level_vars[level].sort()

print("\n" + "="*80)
print("HIERARCHY STRUCTURE ANALYSIS")
print("="*80)

# Show Level 1 (should include TC001)
print("\nLevel 1 (Direct children of TE001 - Total Expenditure):")
for var in sorted(level_vars.get(1, [])):
    node = var_to_node[var]
    print(f"  {var}: {node['description']}")

# Show Level 2 (Major categories that should sum to TC001)
print("\nLevel 2 (Major expenditure categories - should sum to TC001):")
for var in sorted(level_vars.get(2, [])):
    node = var_to_node[var]
    children_count = len(node['children'])
    print(f"  {var}: {node['description']} (has {children_count} children)")

# Show Level 3 items
print("\nLevel 3 items (Subcategories):")
level3_items = sorted(level_vars.get(3, []))
print(f"  Total: {len(level3_items)} items")
for var in level3_items[:10]:  # Show first 10
    node = var_to_node[var]
    children_count = len(node['children'])
    print(f"  {var}: {node['description']} (has {children_count} children)")
if len(level3_items) > 10:
    print(f"  ... and {len(level3_items) - 10} more")

# Show Level 4 items
print("\nLevel 4 items (Detailed subcategories - MAXIMUM LEVEL):")
level4_items = sorted(level_vars.get(4, []))
print(f"  Total: {len(level4_items)} items")
for var in level4_items[:15]:  # Show first 15
    node = var_to_node[var]
    children_count = len(node['children'])
    print(f"  {var}: {node['description']} (has {children_count} children)")
if len(level4_items) > 15:
    print(f"  ... and {len(level4_items) - 15} more")

# Determine which items to include for balancing with TC001
# Strategy: Include the most detailed items (Level 4) where available,
# but fall back to Level 3 if no Level 4 children exist
print("\n" + "="*80)
print("RECOMMENDED ITEMS TO INCLUDE FOR TC001 BALANCE")
print("="*80)
print("\nStrategy: Include Level 4 items where they exist, otherwise use Level 3 items")
print("This ensures maximum detail while avoiding double-counting.\n")

items_to_include = set()
items_to_exclude = set()  # Parent totals that should be excluded

# Start from Level 2 categories and work down
for level2_var in sorted(level_vars.get(2, [])):
    level2_node = var_to_node[level2_var]
    
    # Check if this Level 2 item has Level 3 children
    level3_children = [c for c in level2_node['children'] if var_to_node[c]['level'] == 3]
    
    if not level3_children:
        # No Level 3 children, use Level 2 item itself
        items_to_include.add(level2_var)
        print(f"  Include Level 2: {level2_var} ({level2_node['description']}) - no Level 3 children")
    else:
        # Has Level 3 children, check each Level 3 item
        for level3_var in sorted(level3_children):
            level3_node = var_to_node[level3_var]
            
            # Check if this Level 3 item has Level 4 children
            level4_children = [c for c in level3_node['children'] if var_to_node[c]['level'] == 4]
            
            if not level4_children:
                # No Level 4 children, use Level 3 item
                items_to_include.add(level3_var)
                print(f"    Include Level 3: {level3_var} ({level3_node['description']}) - no Level 4 children")
            else:
                # Has Level 4 children, include all Level 4 items and exclude Level 3 parent
                items_to_exclude.add(level3_var)
                for level4_var in sorted(level4_children):
                    items_to_include.add(level4_var)
                    level4_node = var_to_node[level4_var]
                    print(f"      Include Level 4: {level4_var} ({level4_node['description']})")
                print(f"    Exclude Level 3 parent: {level3_var} (sum of Level 4 children)")

# Also check for any Level 3 items that are direct children of TC001 (not under Level 2)
# Actually, based on hierarchy, Level 2 items are direct children of TC001
# But we should also check if there are any Level 3 items directly under TC001
tc001_children = var_to_node.get('TC001', {}).get('children', [])
if tc001_children:
    print("\nDirect children of TC001:")
    for child in sorted(tc001_children):
        child_node = var_to_node[child]
        print(f"  {child}: Level {child_node['level']} - {child_node['description']}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal items to include: {len(items_to_include)}")
print(f"Total parent items to exclude: {len(items_to_exclude)}")

# Group by level
included_by_level = {}
for var in items_to_include:
    level = var_to_node[var]['level']
    if level not in included_by_level:
        included_by_level[level] = []
    included_by_level[level].append(var)

print("\nItems to include by level:")
for level in sorted(included_by_level.keys()):
    vars_at_level = sorted(included_by_level[level])
    print(f"  Level {level}: {len(vars_at_level)} items")
    if len(vars_at_level) <= 20:
        for var in vars_at_level:
            print(f"    {var}: {var_to_node[var]['description']}")
    else:
        for var in vars_at_level[:10]:
            print(f"    {var}: {var_to_node[var]['description']}")
        print(f"    ... and {len(vars_at_level) - 10} more")

# Save the recommended items list
recommendations = {
    'items_to_include': sorted(list(items_to_include)),
    'items_to_exclude': sorted(list(items_to_exclude)),
    'included_by_level': {str(k): sorted(v) for k, v in included_by_level.items()},
    'strategy': 'Include Level 4 items where available, otherwise Level 3, otherwise Level 2',
    'max_level': 4
}

with open('hierarchy_balance_recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f"\n\nRecommendations saved to: hierarchy_balance_recommendations.json")
print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("1. Review the recommended items list")
print("2. Verify these items sum to TC001 in the actual data")
print("3. Update app.py to use these items instead of current Level 3 only filter")
print("="*80)

