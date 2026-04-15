"""
reduce_dataset.py – Alfadataset

Program ma na celu obniżyć zapotrzebowanie na dane (reduce data demand).

Supports:
  • Random sampling       – keep only a fraction of rows
  • Column selection      – keep only the most informative features
  • Duplicate removal     – drop identical rows
  • Missing-value filter  – drop columns that exceed a missing-value threshold

Usage (CLI):
    python reduce_dataset.py \
        --input  data.csv \
        --output data_reduced.csv \
        --sample 0.5 \
        --drop-duplicates \
        --missing-threshold 0.3 \
        --columns col1 col2 col3

Usage (Python API):
    from reduce_dataset import DatasetReducer

    reducer = DatasetReducer("data.csv")
    reducer.drop_duplicates()
    reducer.filter_missing(threshold=0.3)
    reducer.sample(fraction=0.5)
    reducer.save("data_reduced.csv")
"""

from __future__ import annotations

import argparse
import sys

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None  # type: ignore[assignment]


class DatasetReducer:
    """Reduce a tabular dataset to lower memory / storage / processing demand."""

    def __init__(self, path: str) -> None:
        if pd is None:
            raise ImportError(
                "pandas is required. Install it with: pip install pandas"
            )
        self.path = path
        self.df: pd.DataFrame = pd.read_csv(path)
        print(
            f"Loaded '{path}': {len(self.df)} rows × {len(self.df.columns)} columns"
        )

    # ------------------------------------------------------------------
    # Reduction operations
    # ------------------------------------------------------------------

    def drop_duplicates(self) -> "DatasetReducer":
        """Remove identical rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        print(f"drop_duplicates: removed {removed} duplicate rows")
        return self

    def filter_missing(self, threshold: float = 0.3) -> "DatasetReducer":
        """Drop columns whose fraction of missing values exceeds *threshold*."""
        before = len(self.df.columns)
        missing_frac = self.df.isnull().mean()
        keep = missing_frac[missing_frac <= threshold].index
        self.df = self.df[keep]
        removed = before - len(self.df.columns)
        print(
            f"filter_missing(threshold={threshold}): removed {removed} column(s)"
        )
        return self

    def sample(
        self,
        fraction: float | None = None,
        n: int | None = None,
        random_state: int = 42,
    ) -> "DatasetReducer":
        """Keep a random *fraction* (0–1) or fixed number *n* of rows."""
        if fraction is None and n is None:
            raise ValueError("Provide exactly one of 'fraction' or 'n', not both or neither.")
        if fraction is not None and n is not None:
            raise ValueError("Provide exactly one of 'fraction' or 'n', not both or neither.")
        before = len(self.df)
        if fraction is not None:
            self.df = self.df.sample(frac=fraction, random_state=random_state)
        else:
            self.df = self.df.sample(n=n, random_state=random_state)
        print(f"sample: {before} → {len(self.df)} rows")
        return self

    def select_columns(self, columns: list[str]) -> "DatasetReducer":
        """Keep only the specified *columns*."""
        missing = [c for c in columns if c not in self.df.columns]
        if missing:
            raise ValueError(f"Columns not found in dataset: {missing}")
        before = len(self.df.columns)
        self.df = self.df[columns]
        print(
            f"select_columns: kept {len(self.df.columns)} of {before} column(s)"
        )
        return self

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def save(self, output_path: str, index: bool = False) -> None:
        """Write the reduced dataset to *output_path* (CSV)."""
        self.df.to_csv(output_path, index=index)
        print(
            f"Saved '{output_path}': "
            f"{len(self.df)} rows × {len(self.df.columns)} columns"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> None:
        """Print a brief summary of the current dataset."""
        print(
            f"Current dataset: {len(self.df)} rows × {len(self.df.columns)} columns"
        )
        missing = self.df.isnull().sum()
        cols_with_missing = missing[missing > 0]
        if not cols_with_missing.empty:
            print("Columns with missing values:")
            for col, cnt in cols_with_missing.items():
                pct = cnt / len(self.df) * 100
                print(f"  {col}: {cnt} ({pct:.1f}%)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Reduce a CSV dataset to lower data demand.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--input", required=True, help="Path to the input CSV file.")
    p.add_argument("--output", required=True, help="Path for the reduced CSV file.")
    p.add_argument(
        "--sample",
        type=float,
        default=None,
        metavar="FRACTION",
        help="Fraction of rows to keep (0 < FRACTION ≤ 1).",
    )
    p.add_argument(
        "--sample-n",
        type=int,
        default=None,
        metavar="N",
        help="Exact number of rows to keep.",
    )
    p.add_argument(
        "--drop-duplicates",
        action="store_true",
        help="Remove duplicate rows.",
    )
    p.add_argument(
        "--missing-threshold",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help=(
            "Drop columns where the fraction of missing values exceeds THRESHOLD "
            "(0–1)."
        ),
    )
    p.add_argument(
        "--columns",
        nargs="+",
        default=None,
        metavar="COL",
        help="Keep only these columns.",
    )
    p.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for sampling.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    reducer = DatasetReducer(args.input)

    if args.drop_duplicates:
        reducer.drop_duplicates()

    if args.missing_threshold is not None:
        reducer.filter_missing(threshold=args.missing_threshold)

    if args.columns:
        reducer.select_columns(args.columns)

    if args.sample is not None or args.sample_n is not None:
        reducer.sample(
            fraction=args.sample,
            n=args.sample_n,
            random_state=args.random_state,
        )

    reducer.summary()
    reducer.save(args.output)


if __name__ == "__main__":
    main(sys.argv[1:])
