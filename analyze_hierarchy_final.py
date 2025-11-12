"""
Final analysis using logical relationships based on variable codes and levels.
Determines which items (up to Level 4) should be included to balance with TC001.
"""

import json
from collections import defaultdict

# Load the existing hierarchy structure
with open('hierarchy_structure.json', 'r') as f:
    hierarchy = json.load(f)

var_to_node = hierarchy['var_to_node']
level_vars = hierarchy['level_vars']

# Build logical parent-child relationships based on variable code patterns
# and level structure
def infer_parent_child_relationships():
    """Infer parent-child relationships from variable codes and levels"""
    relationships = defaultdict(list)
    
    # Level 2 items are major categories
    level2_items = level_vars.get('2', [])
    level3_items = level_vars.get('3', [])
    level4_items = level_vars.get('4', [])
    
    # Map Level 3 to Level 2 based on prefix
    for level3_var in level3_items:
        level3_prefix = level3_var[:2]  # e.g., "FD" from "FD003"
        # Find matching Level 2 item
        for level2_var in level2_items:
            if level2_var.startswith(level3_prefix):
                relationships[level2_var].append(level3_var)
                break
    
    # Map Level 4 to Level 3 based on prefix and logical grouping
    for level4_var in level4_items:
        level4_prefix = level4_var[:2]  # e.g., "FD" from "FD100"
        # Find matching Level 3 item
        for level3_var in level3_items:
            if level3_var.startswith(level4_prefix):
                # Check if level4 is a subcategory
                # FD100, FD200, etc. are subcategories of FD003
                # FD991, FD995 are subcategories of FD990
                if level4_prefix == 'FD':
                    if level4_var.startswith('FD99'):
                        # Restaurant items go under FD990
                        if level3_var == 'FD990':
                            relationships[level3_var].append(level4_var)
                            break
                    else:
                        # Store items go under FD003
                        if level3_var == 'FD003':
                            relationships[level3_var].append(level4_var)
                            break
                else:
                    # For other prefixes, match by prefix
                    if level3_var.startswith(level4_prefix):
                        relationships[level3_var].append(level4_var)
                        break
    
    return relationships

relationships = infer_parent_child_relationships()

print("="*80)
print("HIERARCHY ANALYSIS FOR TC001 BALANCE (MAX LEVEL 4)")
print("="*80)

# Show structure
print("\nLevel 2 items (Major categories - should sum to TC001):")
for var in sorted(level_vars.get('2', [])):
    node = var_to_node[var]
    level3_children = relationships.get(var, [])
    print(f"  {var}: {node.get('description', var)} -> {len(level3_children)} Level 3 children")

print("\nLevel 3 items:")
level3_items = sorted(level_vars.get('3', []))
print(f"  Total: {len(level3_items)} items")
for var in level3_items[:15]:
    node = var_to_node[var]
    level4_children = relationships.get(var, [])
    if level4_children:
        print(f"  {var}: {node.get('description', var)} -> {len(level4_children)} Level 4 children")
    else:
        print(f"  {var}: {node.get('description', var)} (no Level 4 children)")

# Determine items to include
print("\n" + "="*80)
print("DETERMINING ITEMS TO INCLUDE FOR TC001 BALANCE")
print("="*80)
print("Strategy: Include Level 4 where available, otherwise Level 3, otherwise Level 2\n")

items_to_include = set()
items_to_exclude = set()

for level2_var in sorted(level_vars.get('2', [])):
    level2_node = var_to_node[level2_var]
    level3_children = relationships.get(level2_var, [])
    
    print(f"\n{level2_var} ({level2_node.get('description', level2_var)}):")
    
    if not level3_children:
        # No Level 3 children, use Level 2
        items_to_include.add(level2_var)
        print(f"  -> Include Level 2: {level2_var}")
    else:
        # Process Level 3 children
        for level3_var in sorted(level3_children):
            level3_node = var_to_node[level3_var]
            level4_children = relationships.get(level3_var, [])
            
            if not level4_children:
                # No Level 4 children, use Level 3
                items_to_include.add(level3_var)
                print(f"  -> Include Level 3: {level3_var} ({level3_node.get('description', level3_var)})")
            else:
                # Has Level 4 children, include all Level 4 and exclude Level 3
                items_to_exclude.add(level3_var)
                for level4_var in sorted(level4_children):
                    items_to_include.add(level4_var)
                print(f"  -> Include {len(level4_children)} Level 4 items, exclude Level 3: {level3_var}")
                # Show first few Level 4 items
                for level4_var in sorted(level4_children)[:3]:
                    level4_node = var_to_node[level4_var]
                    print(f"      - {level4_var}: {level4_node.get('description', level4_var)}")
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
        print(f"    {var}: {node.get('description', var)}")

if items_to_exclude:
    print(f"\n\nItems to exclude (parent totals):")
    for var in sorted(items_to_exclude):
        node = var_to_node[var]
        print(f"  {var}: {node.get('description', var)}")

# Save recommendations
recommendations = {
    'items_to_include': sorted(list(items_to_include)),
    'items_to_exclude': sorted(list(items_to_exclude)),
    'included_by_level': {str(k): sorted(v) for k, v in included_by_level.items()},
    'strategy': 'Include Level 4 items where available, otherwise Level 3, otherwise Level 2. Maximum level: 4.',
    'max_level': 4,
    'total_items': len(items_to_include)
}

with open('hierarchy_balance_recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f"\n\nRecommendations saved to: hierarchy_balance_recommendations.json")
print("="*80)

