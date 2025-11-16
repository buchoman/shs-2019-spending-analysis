"""Check if all 19 items have descriptions"""

# The 19 items that must be displayed
items = [
    'TE001', 'TC001', 'FD001', 'SH001', 'HO001', 'HF001', 'CL030', 
    'TR001', 'HC001', 'PC001', 'RE001', 'ED002', 'RO001', 'TA018', 
    'GC001', 'ME001', 'TX010', 'EP011', 'MG001'
]

# Read SPENDING_DESCRIPTIONS from app.py
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract SPENDING_DESCRIPTIONS dictionary
match = re.search(r'SPENDING_DESCRIPTIONS = \{([^}]+)\}', content, re.DOTALL)
if match:
    descs_text = match.group(1)
    # Simple extraction - look for "KEY": "VALUE" patterns
    descriptions = {}
    for item in items:
        pattern = f'"{item}":\\s*"([^"]+)"'
        match_item = re.search(pattern, descs_text)
        if match_item:
            descriptions[item] = match_item.group(1)
        else:
            descriptions[item] = "MISSING"

    print("Checking descriptions for all 19 items:\n")
    missing = [i for i in items if descriptions.get(i) == "MISSING"]
    
    if missing:
        print(f"Missing descriptions: {missing}\n")
    else:
        print("All items have descriptions!\n")
    
    print("All descriptions:")
    for item in items:
        print(f"  {item}: {descriptions.get(item, 'MISSING')}")
else:
    print("Could not find SPENDING_DESCRIPTIONS in app.py")



