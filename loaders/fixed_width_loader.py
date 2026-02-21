"""
Fixed-width file loader for 2021 SHS PUMF.
Parses Stata .dct layout files and loads TXT data.
"""

import re
from pathlib import Path
from typing import Tuple, List, Optional

import pandas as pd


def _parse_dct(dct_path: Path) -> List[Tuple[str, int, int, str]]:
    """
    Parse Stata .dct file. Returns list of (varname, start, end, dtype).
    Positions are 1-based inclusive (Stata convention).
    """
    spec = []
    with open(dct_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("infix") or line.startswith("{") or line.startswith("}"):
                continue
            # Format: "str    CASEID   1 - 6" or "double WEIGHTD  7 - 24"
            m = re.match(r"(str|double)\s+(\S+)\s+(\d+)\s*-\s*(\d+)", line)
            if m:
                dtype, varname, start, end = m.groups()
                spec.append((varname, int(start), int(end), dtype))
    return spec


def _parse_bsw_layout_sas(layout_path: Path) -> List[Tuple[str, int, int]]:
    """
    Parse SAS-style BSW layout (e.g. pumf_shs2021_bsw_layout.txt).
    Returns list of (varname, start, end) - 1-based inclusive.
    """
    spec = []
    with open(layout_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # @1 CaseID  $6.  or  @7 BSW1  28.10
            m = re.match(r"@(\d+)\s+(\w+)\s+(\$?\d+\.?\d*)", line)
            if m:
                start = int(m.group(1))
                varname = m.group(2)
                fmt = m.group(3)
                if fmt.startswith("$"):
                    width = int(fmt[1:].split(".")[0])
                else:
                    width = int(fmt.split(".")[0])
                end = start + width - 1
                spec.append((varname, start, end))
    return spec


def load_fixed_width_pumf(
    file_path: Path,
    layout_path: Path,
    encoding: str = "utf-8",
) -> Tuple[pd.DataFrame, Optional[object]]:
    """
    Load main PUMF from fixed-width TXT using .dct layout.
    Returns (DataFrame, meta). Meta is None (for compatibility with pyreadstat).
    """
    spec = _parse_dct(layout_path)
    if not spec:
        raise ValueError(f"No variables parsed from layout: {layout_path}")

    names = [s[0] for s in spec]
    # pandas read_fwf: colspecs are (start, end) 0-based, end exclusive
    colspecs = [(s[1] - 1, s[2]) for s in spec]

    df = pd.read_fwf(
        file_path,
        colspecs=colspecs,
        names=names,
        header=None,
        encoding=encoding,
        dtype=None,
        keep_default_na=True,
    )

    # Convert numeric columns; keep CASEID as string for merge
    for i, (varname, _, _, dtype) in enumerate(spec):
        if dtype == "double":
            col = df.columns[i]
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif varname.upper() == "CASEID":
            col = df.columns[i]
            df[col] = df[col].astype(str).str.strip()

    return df, None


def load_fixed_width_bsw(
    file_path: Path,
    layout_path: Path,
    encoding: str = "utf-8",
) -> Tuple[pd.DataFrame, Optional[object]]:
    """
    Load bootstrap weights from fixed-width TXT.
    Layout is SAS-style (pumf_shs2021_bsw_layout.txt).
    Returns (DataFrame, meta). Meta is None.
    """
    spec = _parse_bsw_layout_sas(layout_path)
    if not spec:
        raise ValueError(f"No variables parsed from BSW layout: {layout_path}")

    names = [s[0] for s in spec]
    colspecs = [(s[1] - 1, s[2]) for s in spec]

    df = pd.read_fwf(
        file_path,
        colspecs=colspecs,
        names=names,
        header=None,
        encoding=encoding,
        dtype=None,
        keep_default_na=True,
    )

    # CaseID as string; BSW columns as numeric
    if "CaseID" in df.columns:
        df["CaseID"] = df["CaseID"].astype(str).str.strip()
    elif "caseid" in df.columns:
        df["caseid"] = df["caseid"].astype(str).str.strip()

    bsw_cols = [c for c in df.columns if c.upper().startswith("BSW")]
    for c in bsw_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df, None
