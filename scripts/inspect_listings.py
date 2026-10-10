"""Print and save a read-only initial inspection of an Airbnb listings CSV."""

import argparse
import logging
from pathlib import Path

import pandas as pd


LOGGER = logging.getLogger(__name__)
DEFAULT_REPORT = Path("reports") / "listings_inspection.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a CSV or gzip-compressed CSV listings dataset."
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="path to a .csv or .csv.gz dataset",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"path for the inspection report (default: {DEFAULT_REPORT})",
    )
    return parser.parse_args()


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load a CSV; Pandas infers gzip compression from the .csv.gz suffix."""
    return pd.read_csv(dataset_path, low_memory=False)


def build_report(dataset_path: Path, dataframe: pd.DataFrame) -> str:
    missing_counts = dataframe.isna().sum()
    missing = pd.DataFrame(
        {
            "missing_count": missing_counts,
            "missing_percentage": (
                missing_counts.div(len(dataframe)).mul(100)
                if len(dataframe)
                else 0.0
            ),
        }
    )
    unique_counts = dataframe.nunique(dropna=False)

    sections = [
        f"Initial dataset inspection: {dataset_path}",
        "=" * 80,
        f"Rows: {len(dataframe):,}",
        f"Columns: {len(dataframe.columns):,}",
        "",
        "Column names and data types",
        "-" * 80,
        dataframe.dtypes.to_string(),
        "",
        "First five rows",
        "-" * 80,
        dataframe.head().to_string(index=False),
        "",
        "Basic descriptive statistics (all columns)",
        "-" * 80,
        dataframe.describe(include="all").transpose().to_string(),
        "",
        "Missing values by column",
        "-" * 80,
        missing.to_string(
            formatters={"missing_percentage": lambda value: f"{value:.2f}%"}
        ),
        "",
        f"Exact duplicate rows: {dataframe.duplicated().sum():,}",
        "",
        "Unique values by column (including missing values)",
        "-" * 80,
        unique_counts.to_string(),
        "",
    ]
    return "\n".join(sections)


def main() -> int:
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    args = parse_args()
    dataset_path = args.dataset
    report_path = args.report

    if not dataset_path.is_file():
        LOGGER.error("Dataset file does not exist or is not a file: %s", dataset_path)
        return 1
    if not dataset_path.name.lower().endswith((".csv", ".csv.gz")):
        LOGGER.error("Dataset must have a .csv or .csv.gz extension: %s", dataset_path)
        return 1
    if dataset_path.resolve() == report_path.resolve():
        LOGGER.error("Report path must not be the same as the input dataset.")
        return 1

    try:
        dataframe = load_dataset(dataset_path)
        report = build_report(dataset_path, dataframe)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    except (OSError, UnicodeError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        LOGGER.error("Could not inspect the dataset or save the report: %s", exc)
        return 1

    print(report)
    print(f"Report saved to: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
