"""
2019 SHS PUMF configuration.
Uses SAS7BDAT files; no variable renaming (identity mapping).
"""

from pathlib import Path
from .year_config_base import YearConfigBase


class YearConfig2019(YearConfigBase):
    """Configuration for 2019 SHS PUMF."""

    @property
    def year(self) -> int:
        return 2019

    def get_data_paths(self) -> dict:
        data_dir = Path("SHS_EDM_2019/Data/SAS")
        return {
            "data_dir": data_dir,
            "main_file": data_dir / "pumf_shs2019.sas7bdat",
            "bsw_file": data_dir / "pumf_shs2019_bsw.sas7bdat",
        }

    def get_variable_mapping(self) -> dict:
        # 2019 SAS column names -> canonical app column names
        return {
            "CASEID": "CaseID",
            "WEIGHTD": "WeightD",
            "HH_TOTINC": "HH_TotInc",
            "PROV": "Prov",
            "HHTYPE6": "HHType6",
            "HHSIZE": "HHSize",
            "DWELTYP": "DwellTyp",
            "TENURE": "Tenure",
            "NUMBEDR": "Numbedr",
            "RP_AGEGP": "RP_AgeGrp",
            "RP_AGEGRP": "RP_AgeGrp",
            "RP_GEN": "RP_Gender",
            "RP_MAST": "RP_MarStat",
            "RP_EDUC": "RP_Educ",
            "SP_AGEGP": "SP_AgeGrp",
            "SP_AGEGRP": "SP_AgeGrp",
            "SP_GEN": "SP_Gender",
            "SP_EDUC": "SP_Educ",
            "SPOUSEYN": "SpouseYN",
            "P0TO4YN": "P0to4YN",
            "P5TO15YN": "P5to15YN",
            "OWNVEH": "VehicleYN",
            "OWNRV": "RecVehYN",
            "MAJINS": "HH_MajIncSrc",
        }

    def get_value_labels(self) -> dict:
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
            },
        }

    def get_income_column(self) -> str:
        """Canonical column name after apply_rename (HH_TotInc)."""
        return "HH_TotInc"
