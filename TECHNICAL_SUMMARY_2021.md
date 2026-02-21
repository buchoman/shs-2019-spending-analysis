# Technical Summary: 2021 SHS PUMF Migration

## Structural Differences Between 2019 and 2021

See [config/STRUCTURAL_DIFFERENCES_2019_2021.md](config/STRUCTURAL_DIFFERENCES_2019_2021.md) for a detailed comparison.

Key differences:
- **File format**: 2019 uses SAS7BDAT; 2021 uses fixed-width TXT only (no SAS files provided).
- **Variable names**: Several filter/demographic variables renamed (e.g., HHTOTINC vs HH_TOTINC, OWNVEH vs VEHICLEYN).
- **Spending codes**: RE090→RE091, RE124→RE125, RE127→RE128, RE140→RE142; HO004/HO005→HO050/HO052; TR021/TR022 removed.
- **Record layout**: Column positions shifted; 2021 LRECL=3980 vs 2019 LRECL≈4046.

## Code Changes Made

### New Files

| File | Purpose |
|------|---------|
| `config/year_config_base.py` | Abstract config interface |
| `config/year_config_2019.py` | 2019 paths and value labels |
| `config/year_config_2021.py` | 2021 paths, variable mapping, value labels, spending code mapping |
| `config/STRUCTURAL_DIFFERENCES_2019_2021.md` | Structural differences documentation |
| `loaders/fixed_width_loader.py` | Parse fixed-width TXT using Stata .dct and SAS BSW layout |
| `app_2021.py` | 2021 Streamlit app (parallel to app.py) |
| `build_hierarchy_2021.py` | Checks for 2021 hierarchy Excel; uses 2019 hierarchy if none found |

### Modifications

- **app_2021.py**: Uses fixed-width loader, year config, applies variable rename after load, applies spending code mapping, updated citations to 2021.
- **2019 app.py**: Unchanged (per plan).

### Configuration Layer

- `get_data_paths()`: Returns main file, BSW file, layout paths.
- `get_variable_mapping()`: PUMF column names → canonical app names.
- `get_value_labels()`: Value labels for filter variables.
- `get_spending_code_mapping()`: 2019 spending codes → 2021 equivalents (or None to exclude).

## Risks and Validation Concerns

1. **Spending code differences**: Some 2019 codes may have different semantics in 2021 (e.g., HO050/HO052 vs HO004/HO005). Manual review recommended.
2. **HHTYPE6 value codes**: 2021 uses "01"-"06"; VALUE_LABELS include both formats.
3. **Hierarchy**: 2021 uses 2019 hierarchy; if StatCan publishes a 2021-specific hierarchy, it should be integrated.
4. **Encoding**: Fixed-width TXT uses UTF-8; if data use Latin-1, encoding may need adjustment.
5. **Missing variables**: TR021, TR022 excluded from 2021 analysis; results may differ from 2019.

## Suggested Improvements for Future PUMF Releases

1. **Unified app with year selector**: Single app that loads config by year and switches data loader.
2. **Generic layout parser**: Parse .dct or SAS `_i.SAS` generically so new years only need new layout files.
3. **Variable registry**: CSV/JSON mapping (PUMF_var, canonical_name, year) for all years.
4. **Automated layout diff**: Script to compare two PUMF layouts and output variable/position changes.
5. **Hierarchy from config**: Store hierarchy path in year config; build from year-specific Excel when available.

## Running the 2021 Application

```bash
streamlit run app_2021.py
```

Data must be in `RY2021/Data/TXT/`:
- `PUMF_SHS_2021.txt` (main PUMF)
- `pumf_shs2021_bsw_flatfile.txt` (bootstrap weights)

Layout files in `RY2021/Reading cards/STATA/` and `RY2021/Data/TXT/` must be present.
