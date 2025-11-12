import pandas as pd
import re

# Read the hierarchy file
df = pd.read_excel('SHS_EDM_2019/Documentation/Expenditure category hierarchy/Hierarchy of expenditure categories, PUMF 2019.xlsx', header=6)

# Extract hierarchy structure
hierarchy = []
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
        path = []
        for col_idx in range(1, 8):  # Columns 1-7 (Level_0 to Level_6)
            val = row.iloc[col_idx]
            if pd.notna(val) and str(val).strip():
                path.append(str(val).strip())
        
        hierarchy.append({
            'level': level,
            'var_code': var_code,
            'var_name': var_name,
            'path': path
        })

# Print sample
print(f"Total variables: {len(hierarchy)}")
print("\nFirst 50 entries:")
for i, h in enumerate(hierarchy[:50]):
    indent = "  " * h['level']
    print(f"{indent}Level {h['level']}: {h['var_code']} - {h['var_name']}")

# Group by level to understand structure
print("\n\nVariables by level:")
for level in range(7):
    vars_at_level = [h for h in hierarchy if h['level'] == level]
    print(f"\nLevel {level}: {len(vars_at_level)} variables")
    for h in vars_at_level[:10]:
        print(f"  {h['var_code']} - {h['var_name'][:60]}")

