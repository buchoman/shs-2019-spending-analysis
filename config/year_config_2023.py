"""
2023 SHS PUMF configuration.
Uses fixed-width TXT files; maps 2023 variable names to canonical app names.
"""

from pathlib import Path
from .year_config_base import YearConfigBase
from .year_config_2021 import YearConfig2021, VAR_RENAME_2021


class YearConfig2023(YearConfigBase):
    """Configuration for 2023 SHS PUMF."""

    @property
    def year(self) -> int:
        return 2023

    def get_data_paths(self) -> dict:
        data_dir = Path("RY2023/Data/TXT")
        return {
            "data_dir": data_dir,
            "main_file": data_dir / "PUMF_SHS_2023.txt",
            "bsw_file": data_dir / "pumf_shs2023_bsw_flatfile.txt",
            "layout_file": Path("RY2023/Reading cards/STATA/pumf_SHS_2023.dct"),
            "bsw_layout_file": Path("RY2023/Data/TXT/pumf_shs2023_bsw_layout.txt"),
        }

    def get_variable_mapping(self) -> dict:
        return VAR_RENAME_2021.copy()

    def get_value_labels(self) -> dict:
        return YearConfig2021().get_value_labels()

    def get_spending_code_mapping(self) -> dict:
        """
        Map 2019-reference spending codes to 2023 equivalents where they differ.
        Returns {ref_code: 2023_code}. Codes not in mapping are unchanged.
        """
        mapping = YearConfig2021().get_spending_code_mapping()
        mapping.update({
            "CS008": "CS009",
            "RE062": "RE083",
            "RE063": "RE084",
            "RE066": "RE087",
            "TR030": "TR080",
        })
        return mapping

    def get_extra_spending_codes(self) -> dict:
        """Spending codes that exist only in 2023 (not in SPENDING_CATEGORIES)."""
        return {
            "Communications": ["CS014", "CS015", "CS016", "CS017"],
            "Transportation": ["TR043"],
        }
