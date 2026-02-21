"""
2021 SHS PUMF configuration.
Uses fixed-width TXT files; maps 2021 variable names to canonical app names.
"""

from pathlib import Path
from .year_config_base import YearConfigBase


# Map 2021 PUMF variable names to canonical app column names
VAR_RENAME_2021 = {
    "HHTOTINC": "HH_TotInc",
    "P0TO4": "P0to4YN",
    "P5TO15": "P5to15YN",
    "P16TO29": "P16to29YN",
    "P30TO64": "P30to64YN",
    "P65TO74": "P65to74YN",
    "P75PLUS": "P75plusYN",
    "RP_AGEGP": "RP_AgeGrp",
    "RP_GEN": "RP_Gender",
    "RP_MAST": "RP_MarStat",
    "SP_AGEGP": "SP_AgeGrp",
    "SP_GEN": "SP_Gender",
    "OWNVEH": "VehicleYN",
    "OWNRV": "RecVehYN",
    "MAJINS": "HH_MajIncSrc",
    # PROV, HHSIZE, DWELTYP, TENURE, NUMBEDR, RP_EDUC, SP_EDUC, SPOUSEYN unchanged
    # but SAS/Stata use uppercase; normalize to match app expectation
    "CASEID": "CaseID",
    "WEIGHTD": "WeightD",
    "PROV": "Prov",
    "HHTYPE6": "HHType6",
    "HHSIZE": "HHSize",
    "DWELTYP": "DwellTyp",
    "TENURE": "Tenure",
    "HHSIZE": "HHSize",
    "NUMBEDR": "Numbedr",
    "RP_EDUC": "RP_Educ",
    "SP_EDUC": "SP_Educ",
    "SPOUSEYN": "SpouseYN",
}


class YearConfig2021(YearConfigBase):
    """Configuration for 2021 SHS PUMF."""

    @property
    def year(self) -> int:
        return 2021

    def get_data_paths(self) -> dict:
        data_dir = Path("RY2021/Data/TXT")
        return {
            "data_dir": data_dir,
            "main_file": data_dir / "PUMF_SHS_2021.txt",
            "bsw_file": data_dir / "pumf_shs2021_bsw_flatfile.txt",
            "layout_file": Path("RY2021/Reading cards/STATA/PUMF_SHS_2021.dct"),
            "bsw_layout_file": Path("RY2021/Data/TXT/pumf_shs2021_bsw_layout.txt"),
        }

    def get_variable_mapping(self) -> dict:
        return VAR_RENAME_2021.copy()

    def get_value_labels(self) -> dict:
        # 2021 uses HHTYPE6 "01"-"06" (2 chars); MAJINS same as HH_MAJINCSRC
        return {
            "PROV": {
                "10": "Newfoundland and Labrador",
                "11": "Prince Edward Island",
                "12": "Nova Scotia",
                "13": "New Brunswick",
                "24": "Quebec",
                "35": "Ontario",
                "46": "Manitoba",
                "47": "Saskatchewan",
                "48": "Alberta",
                "59": "British Columbia",
                "63": "Territorial capitals",
            },
            "HHTYPE6": {
                "1": "One person household",
                "2": "Couple without children",
                "3": "Couple with children",
                "4": "Couple with other related or unrelated persons",
                "5": "Lone parent family with no additional persons",
                "6": "Other household with related or unrelated persons",
                "01": "One person household",
                "02": "Couple without children",
                "03": "Couple with children",
                "04": "Couples with other related or unrelated persons",
                "05": "Lone parent family",
                "06": "Other households with related or unrelated persons",
            },
            "HHSIZE": {"1": "1", "2": "2", "3": "3", "4": "4 or more"},
            "P0TO4YN": {"1": "Yes", "2": "No"},
            "P5TO15YN": {"1": "Yes", "2": "No"},
            "P16TO29YN": {"1": "Yes", "2": "No"},
            "P30TO64YN": {"1": "Yes", "2": "No"},
            "P65TO74YN": {"1": "Yes", "2": "No"},
            "P75PLUSYN": {"1": "Yes", "2": "No"},
            "RP_AGEGRP": {
                "01": "Less than 30 years",
                "02": "30 to 39 years",
                "03": "40 to 54 years",
                "04": "55 to 64 years",
                "05": "65 to 74 years",
                "06": "75 years and over",
            },
            "RP_GENDER": {"1": "Male", "2": "Female"},
            "RP_MARSTAT": {
                "1": "Married or common-law",
                "2": "Single, never married",
                "3": "Separated, widowed or divorced",
            },
            "RP_EDUC": {
                "1": "Less than high school diploma or its equivalent",
                "2": "High school diploma, high school equivalency certificate, or not stated",
                "3": "Certificate or diploma from a trades school, college, CEGEP or other non-university educational institution",
                "4": "University certificate or diploma",
                "9": "Masked records (Prince Edward Island and the territorial capitals)",
            },
            "SPOUSEYN": {"1": "Yes", "2": "No"},
            "SP_AGEGRP": {
                "01": "Less than 30 years",
                "02": "30 to 39 years",
                "03": "40 to 54 years",
                "04": "55 to 64 years",
                "05": "65 to 74 years",
                "06": "75 years and over",
                "96": "No spouse",
            },
            "SP_GENDER": {"1": "Male", "2": "Female", "6": "No spouse"},
            "SP_EDUC": {
                "1": "Less than high school diploma or its equivalent",
                "2": "High school diploma, high school equivalency certificate, or not stated",
                "3": "Certificate or diploma from a trades school, college, CEGEP or other non-university educational institution",
                "4": "University certificate or diploma",
                "6": "No spouse",
                "9": "Masked records (Prince Edward Island and the territorial capitals)",
            },
            "DWELTYP": {
                "1": "Single detached",
                "2": "Double, row, terrace or duplex",
                "3": "Apartment or other",
            },
            "TENURE": {
                "1": "Owned with mortgage",
                "2": "Owned without mortgage",
                "3": "Rented",
            },
            "NUMBEDR": {"1": "1", "2": "2", "3": "3", "4": "4 or more"},
            "VEHICLEYN": {"1": "Yes", "2": "No"},
            "RECVEHYN": {"1": "Yes", "2": "No"},
            "HH_MAJINCSRC": {
                "1": "Earnings (employment income)",
                "2": "Investment income",
                "3": "Government transfer payments",
                "4": "Other income",
                "5": "All sources less than or equal to zero",
            },
        }

    def get_spending_code_mapping(self) -> dict:
        """
        Map 2019 spending codes to 2021 equivalents where they differ.
        Returns {2019_code: 2021_code}. Codes not in mapping are unchanged.
        """
        return {
            "RE090": "RE091",
            "RE124": "RE125",
            "RE127": "RE128",
            "RE140": "RE142",
            "HO004": "HO050",
            "HO005": "HO052",
            # TR021, TR022 not in 2021 - exclude (map to None)
            "TR021": None,
            "TR022": None,
        }
