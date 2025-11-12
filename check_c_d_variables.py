"""Check which variables have _C and _D versions in the data"""

import pyreadstat
from pathlib import Path

# Load data
data_file = Path('SHS_EDM_2019/Data/SAS/pumf_shs2019.sas7bdat')
df, meta = pyreadstat.read_sas7bdat(str(data_file))

# Items from ITEMS_FOR_TC001_BALANCE
items = [
    'CL014', 'CL015', 'CL016', 'CL017', 'CL023', 'CL026', 'CL990',
    'ED003', 'ED030',
    'FD100', 'FD200', 'FD300', 'FD400', 'FD500', 'FD600', 'FD700', 'FD800', 'FD991', 'FD995',
    'GC001',
    'HC022', 'HC025', 'HC061',
    'HF002',
    'HO003', 'HO004', 'HO005', 'HO006', 'HO010', 'HO014', 'HO018', 'HO022',
    'ME039', 'ME040',
    'PC002', 'PC020',
    'RE006', 'RE007', 'RE010', 'RE016', 'RE022', 'RE032', 'RE040', 'RE041', 'RE052', 'RE060', 'RE061', 'RE074', 'RE090', 'RE124', 'RE140', 'RE990',
    'RO002', 'RO003', 'RO004', 'RO005', 'RO010',
    'SH003', 'SH010', 'SH030', 'SH040', 'SH041', 'SH047', 'SH050',
    'TA005', 'TA006', 'TA007', 'TA008',
    'TR003', 'TR020', 'TR030', 'TR070',
    'TC001', 'TE001'
]

print("Variables with _C and/or _D versions:\n")
variables_with_c_d = {}

for item in items:
    c_var = item + '_C'
    d_var = item + '_D'
    has_c = c_var in df.columns
    has_d = d_var in df.columns
    
    if has_c or has_d:
        variables_with_c_d[item] = {'_C': has_c, '_D': has_d}
        print(f"{item}: _C={has_c}, _D={has_d}")

print(f"\n\nTotal variables with _C or _D: {len(variables_with_c_d)}")

# Also check parent totals that might have _C/_D
parent_totals = ['HC002', 'HO002', 'RE002', 'SH002', 'TR002']
print("\n\nParent totals with _C and/or _D:")
for item in parent_totals:
    c_var = item + '_C'
    d_var = item + '_D'
    has_c = c_var in df.columns
    has_d = d_var in df.columns
    if has_c or has_d:
        print(f"{item}: _C={has_c}, _D={has_d}")

