"""
Base configuration interface for year-specific SHS PUMF settings.
Implementations provide paths, variable mappings, and value labels.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class YearConfigBase(ABC):
    """Abstract base for year-specific PUMF configuration."""

    @property
    @abstractmethod
    def year(self) -> int:
        """Survey year (e.g., 2019, 2021)."""
        pass

    @abstractmethod
    def get_data_paths(self) -> Dict[str, Path]:
        """
        Return paths for main data and bootstrap weights.
        Keys: 'main_file', 'bsw_file', 'data_dir'
        """
        pass

    @abstractmethod
    def get_variable_mapping(self) -> Dict[str, str]:
        """
        Map PUMF variable names to canonical app column names.
        PUMF name -> canonical name. Empty dict means no renaming.
        """
        pass

    @abstractmethod
    def get_value_labels(self) -> Dict[str, Dict[str, str]]:
        """
        Value label mappings for filter variables.
        Keys are canonical variable names (e.g., PROV, HHTYPE6).
        Values are {code: label} dicts.
        """
        pass

    def get_filter_columns(self) -> list:
        """
        List of canonical filter column names used by the app.
        Default implementation derives from value labels.
        """
        return list(self.get_value_labels().keys())

    def get_spending_code_mapping(self) -> dict:
        """
        Map spending codes from a reference year to this year where they differ.
        Returns {ref_code: this_year_code}. Codes not in mapping are unchanged.
        Default: empty dict (no mapping).
        """
        return {}

    def apply_rename(self, df):
        """
        Apply variable mapping to DataFrame columns.
        Override if custom logic needed (e.g., HHTYPE6 normalization).
        """
        mapping = self.get_variable_mapping()
        if not mapping:
            return df
        rename = {k: v for k, v in mapping.items() if k in df.columns}
        return df.rename(columns=rename)
