# Structural Differences: 2019 vs 2021 SHS PUMF

## 1. File Format and Data Loading

| Aspect | 2019 | 2021 |
|--------|------|------|
| Main data | SAS7BDAT (`pumf_shs2019.sas7bdat`) | Fixed-width TXT (`PUMF_SHS_2021.txt`, LRECL=3980) |
| Bootstrap weights | SAS7BDAT (`pumf_shs2019_bsw.sas7bdat`) | Fixed-width TXT (`pumf_shs2021_bsw_flatfile.txt`, LRECL=28007) |
| Data directory | `SHS_EDM_2019/Data/SAS` | `RY2021/Data/TXT` |

## 2. Variable Name Changes (Filter/Demographic)

| 2019 (app canonical) | 2021 (PUMF layout) | Notes |
|----------------------|--------------------|-------|
| HH_TOTINC | HHTOTINC | No underscore |
| HHTYPE6 (1 char) | HHTYPE6 (2 chars) | 2021 uses "01"-"06" vs "1"-"6" |
| P0TO4YN, P5TO15YN, etc. | P0TO4, P5TO15, etc. | YN suffix removed |
| RP_AGEGRP | RP_AGEGP | Abbreviation |
| RP_GENDER | RP_GEN | Shortened |
| RP_MARSTAT | RP_MAST | Shortened |
| SP_AGEGRP | SP_AGEGP | Same as RP |
| SP_GENDER | SP_GEN | Shortened |
| VEHICLEYN | OWNVEH | Different variable name |
| RECVEHYN | OWNRV | Different variable name |
| HH_MAJINCSRC | MAJINS | Different variable name |

## 3. Record Layout Shifts

- **2019**: HH_TOTINC at 96-106; CC001 at 108-118; TC001 at 3672-3682; TE001 at 3705-3715
- **2021**: HHTOTINC at 64-74; CC001 at 120-130; TC001 at 3651-3661; TE001 at 3684-3694

2019 has RP_TOTINC, SP_TOTINC, OTH_TOTINC before HH_TOTINC; 2021 has HHEMPIN, HHINVST, HHGTR, HHOTHINC instead.

## 4. Spending Variable Code Changes

| 2019 | 2021 | Notes |
|------|------|-------|
| RE090 | RE091 | Renamed |
| RE124 | RE125 | Renamed |
| RE127 | RE128 | Renamed |
| RE140 | RE142 | Renamed |
| HO004 | HO050 | Replaced |
| HO005 | HO052 | Replaced |
| TR021 | (removed) | Not in 2021 |
| TR022 | (removed) | Not in 2021 |

2021 adds FD1100 (new variable).

## 5. Weights and Bootstrap

- **Survey weight**: WEIGHTD (both years, position 7-24)
- **Bootstrap**: BSW1-BSW1000, merge on CaseID (both years)
- BSW layout identical: CaseID 1-6, then 28.10 per weight

## 6. Hierarchy

- 2019: Built from `SHS_EDM_2019/Documentation/Expenditure category hierarchy/Hierarchy of expenditure categories, PUMF 2019.xlsx`
- 2021: No hierarchy Excel in RY2021; application uses `hierarchy_structure.json` (2019) for 2021

## 7. Assumptions

- Value codes for MAJINS match HH_MAJINCSRC (1-5)
- HHTYPE6 codes "01"-"06" in 2021 have same meaning as "1"-"6" in 2019
- OWNVEH/OWNRV have same value codes (1=Yes, 2=No) as VEHICLEYN/RECVEHYN
