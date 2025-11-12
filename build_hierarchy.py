import pandas as pd
import re
import json

# Read the hierarchy file
df = pd.read_excel('SHS_EDM_2019/Documentation/Expenditure category hierarchy/Hierarchy of expenditure categories, PUMF 2019.xlsx', header=6)

# Extract hierarchy structure
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
    
    # Extract variable code (e.g., "FD001" from "FD001 - Food expenditures")
    match = re.match(r'^([A-Z]+\d+[A-Z]*)', var_name)
    if match:
        var_code = match.group(1)
        
        # Get the full path through hierarchy
        # Level 1 is in column C (index 2), Level 2 in column D (index 3), etc.
        # Column A (index 0) = level number, Column B (index 1) = Level_0, Column C (index 2) = Level_1
        path = []
        for col_idx in range(2, 9):  # Columns C through I (indices 2-8) = Level_1 through Level_6
            val = row.iloc[col_idx]
            if pd.notna(val) and str(val).strip():
                path.append(str(val).strip())
        
        # Extract description from var_name (after the code)
        desc_match = re.match(r'^[A-Z]+\d+[A-Z]*\s*-\s*(.+)', var_name)
        description = desc_match.group(1) if desc_match else var_name
        
        hierarchy_data.append({
            'level': level,
            'var_code': var_code,
            'var_name': var_name,
            'description': description,
            'path': path
        })

# Build hierarchy tree structure
def build_hierarchy_tree(hierarchy_data):
    """Build a tree structure from flat hierarchy data"""
    var_to_node = {}  # Map var_code to its node
    processed = []  # Track processed items in order
    
    for item in hierarchy_data:
        var_code = item['var_code']
        level = item['level']
        description = item['description']
        path = item['path']
        
        # Create node
        node = {
            'var_code': var_code,
            'level': level,
            'description': description,
            'path': path,
            'children': [],
            'parent': None
        }
        
        # Find parent by looking at the path structure
        # Parent should be at level-1 and have a path that is a prefix of current path
        parent = None
        for prev_item in reversed(processed):  # Check in reverse order (most recent first)
            if prev_item['level'] == level - 1:
                # Check if previous item's path is a prefix of current path
                prev_path = prev_item['path']
                if len(prev_path) < len(path):
                    # Check if paths match up to parent's length
                    if prev_path == path[:len(prev_path)]:
                        parent = prev_item['var_code']
                        break
        
        node['parent'] = parent
        var_to_node[var_code] = node
        
        if parent and parent in var_to_node:
            var_to_node[parent]['children'].append(var_code)
        
        processed.append(item)
    
    return var_to_node

var_to_node = build_hierarchy_tree(hierarchy_data)

# Get all variables at each level (for summing)
def get_vars_at_level(level, var_to_node):
    """Get all variables at a specific level"""
    return [code for code, node in var_to_node.items() if node['level'] == level]

# Get variables at each level
level_vars = {}
for level in range(7):
    level_vars[level] = get_vars_at_level(level, var_to_node)

# Build parent-child groups (siblings at same level under same parent)
def get_sibling_groups(var_to_node):
    """Group variables by their parent and level"""
    groups = {}  # (parent, level) -> [var_codes]
    for var_code, node in var_to_node.items():
        key = (node['parent'], node['level'])
        if key not in groups:
            groups[key] = []
        groups[key].append(var_code)
    return groups

# Print summary
print("Hierarchy Summary:")
print(f"Total variables: {len(var_to_node)}")
print("\nVariables by level:")
for level in sorted(level_vars.keys()):
    vars_at_level = level_vars[level]
    print(f"Level {level}: {len(vars_at_level)} variables")
    if len(vars_at_level) <= 20:
        for var in vars_at_level[:10]:
            node = var_to_node[var]
            print(f"  {var} - {node['description'][:60]}")

# Save to JSON for use in app
sibling_groups = get_sibling_groups(var_to_node)

hierarchy_structure = {
    'var_to_node': {k: {
        'var_code': v['var_code'],
        'level': v['level'],
        'description': v['description'],
        'parent': v['parent'],
        'children': v['children']
    } for k, v in var_to_node.items()},
    'level_vars': level_vars,
    'sibling_groups': {f"{parent}_{level}": vars_list for (parent, level), vars_list in sibling_groups.items()}
}

with open('hierarchy_structure.json', 'w') as f:
    json.dump(hierarchy_structure, f, indent=2)

print("\n\nHierarchy structure saved to hierarchy_structure.json")

