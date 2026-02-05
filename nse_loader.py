from __future__ import annotations

from typing import IO, List, Tuple

import pandas as pd


EXPECTED_COLUMNS: List[str] = [
    "DATE",
    "SERIES",
    "OPEN",
    "HIGH",
    "LOW",
    "PREV. CLOSE",
    "LTP",
    "CLOSE",
    "VWAP",
    "52W H",
    "52W L",
    "VOLUME",
    "VALUE",
    "NO. OF TRADES",
]


def _norm_key(col: str) -> str:
    """
    Normalize a column name for comparison:
    - strip leading/trailing whitespace
    - collapse multiple internal spaces
    - uppercase
    """
    return " ".join(col.strip().upper().split())


def _normalize_and_validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and normalize NSE CSV columns.

    - Ensures all EXPECTED_COLUMNS are present (case-insensitive, ignores extra spaces).
    - Renames columns to the canonical EXPECTED_COLUMNS.
    """
    # Map normalized key -> original column name
    col_map = {_norm_key(c): c for c in df.columns}

    missing = [col for col in EXPECTED_COLUMNS if _norm_key(col) not in col_map]
    if missing:
        raise ValueError(
            "Missing expected columns in CSV: "
            + ", ".join(missing)
            + ". Please ensure you downloaded the standard NSE CSV."
        )

    # Build rename dict from original CSV names to canonical names
    rename_dict = {col_map[_norm_key(col)]: col for col in EXPECTED_COLUMNS}
    df = df.rename(columns=rename_dict)
    return df


def load_nse_csv(file: IO[bytes]) -> pd.DataFrame:
    """
    Load and clean an NSE CSV file with the expected columns.

    Steps:
    - Read CSV.
    - Validate and normalize columns.
    - Parse DATE.
    - Convert numeric columns.
    - Drop rows with missing DATE or CLOSE.
    - Sort by DATE.
    """
    df = pd.read_csv(file)
    df = _normalize_and_validate_columns(df)

    # Parse DATE (NSE often uses DD-MMM-YYYY)
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce", dayfirst=True)

    # Numeric columns (all except DATE and SERIES)
    numeric_cols = [
        c
        for c in EXPECTED_COLUMNS
        if c not in {"DATE", "SERIES"}
    ]
    for col in numeric_cols:
        # Remove thousands separators like "1,444.00"
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with invalid dates or no closing price
    df = df.dropna(subset=["DATE", "CLOSE"])

    # Sort chronologically
    df = df.sort_values("DATE").reset_index(drop=True)

    return df


def get_date_bounds(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Return min and max DATE for convenience."""
    return df["DATE"].min(), df["DATE"].max()


if __name__ == "__main__":
    # Simple manual test stub (expects local file for quick checks)
    import pathlib

    sample_path = pathlib.Path("data") / "sample_nse.csv"
    if sample_path.exists():
        with open(sample_path, "rb") as f:
            df_test = load_nse_csv(f)
        print(df_test.head())
        print("Date range:", get_date_bounds(df_test))
    else:
        print("Place a sample_nse.csv in the data/ folder for a quick test.")

