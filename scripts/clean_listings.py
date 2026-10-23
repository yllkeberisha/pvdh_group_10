"""Clean an Airbnb listings CSV, handle its missing values, and save a report."""

import argparse
import logging
from pathlib import Path

import pandas as pd


LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT = Path("dataset") / "listings_clean.csv"
DEFAULT_REPORT = Path("reports") / "listings_cleaning.txt"
PRICE_UPPER_QUANTILE = 0.99
BOOLEAN_COLUMNS = [
    "host_is_superhost",
    "host_has_profile_pic",
    "host_identity_verified",
    "has_availability",
]
INTEGER_COLUMNS = [
    "bedrooms",
    "beds",
    "host_listings_count",
    "hosts_time_as_user_years",
    "hosts_time_as_user_months",
    "hosts_time_as_host_years",
    "hosts_time_as_host_months",
]
TEXT_FILL_VALUES = {
    "description": "No description",
    "host_about": "No description",
    "host_location": "Unknown",
    "license": "Unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a CSV or gzip-compressed CSV listings dataset."
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="path to a .csv or .csv.gz dataset",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"path for the cleaned dataset (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"path for the cleaning report (default: {DEFAULT_REPORT})",
    )
    return parser.parse_args()


def bathrooms_from_text(bathrooms_text: pd.Series) -> pd.Series:
    """Read the number from text such as '1.5 shared baths'; 'Half-bath' is 0.5."""
    text = bathrooms_text.astype("string")
    numbers = text.str.extract(r"(\d+(?:\.\d+)?)")[0].astype(float)
    half_bath = text.str.contains("half", case=False, na=False)
    return numbers.mask(numbers.isna() & half_bath, 0.5)


def clean_dataset(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return the cleaned dataframe and a description of every step taken."""
    df = dataframe.copy()
    steps = []

    missing_bathrooms = int(df["bathrooms"].isna().sum())
    df["bathrooms"] = df["bathrooms"].fillna(bathrooms_from_text(df["bathrooms_text"]))
    steps.append(
        f"Filled {missing_bathrooms - int(df['bathrooms'].isna().sum()):,} missing "
        "bathrooms from the number in bathrooms_text (e.g. '1.5 baths' -> 1.5)."
    )

    empty_columns = df.columns[df.isna().all()].tolist()
    df = df.drop(columns=empty_columns)
    steps.append(
        f"Dropped {len(empty_columns)} completely empty columns, because they "
        f"hold no information: {', '.join(empty_columns)}."
    )

    rows_before = len(df)
    df = df.drop_duplicates(subset="id")
    steps.append(f"Removed {rows_before - len(df):,} duplicate listings (same id).")

    df["price"] = pd.to_numeric(
        df["price"].astype("string").str.replace(r"[$,]", "", regex=True)
    )
    steps.append(
        "Converted price from text such as '$1,180.00' to a number. It is the "
        "price per night in the local currency; the '$' is only formatting."
    )

    rows_before = len(df)
    df = df.dropna(subset=["price"])
    steps.append(
        f"Dropped {rows_before - len(df):,} rows without a price. Price is the "
        "main variable for analysis, so filling it in would invent the values "
        "we want to study. Most of these listings have no available days in "
        "the next year, so they cannot be booked anyway."
    )

    rows_before = len(df)
    df = df.dropna(subset=["host_name"])
    steps.append(
        f"Dropped {rows_before - len(df):,} rows without any host information "
        "(host name, superhost status and listing counts were all missing)."
    )

    price_limit = df["price"].quantile(PRICE_UPPER_QUANTILE)
    rows_before = len(df)
    df = df[df["price"].le(price_limit)]
    steps.append(
        f"Removed {rows_before - len(df):,} outlier rows with a price above the "
        f"{PRICE_UPPER_QUANTILE * 100:.0f}th percentile ({price_limit:,.2f}). This "
        "removes placeholder prices that block bookings, but also some genuine "
        "luxury listings."
    )

    # Airbnb often leaves bedrooms empty for studios instead of recording 0.
    studio = (
        df["room_type"].eq("Entire home/apt")
        & df["bedrooms"].isna()
        & df["name"].str.contains("studio", case=False, na=False)
    )
    df.loc[studio, "bedrooms"] = 0
    steps.append(
        f"Set {int(studio.sum()):,} missing bedrooms to 0 for entire homes named "
        "as a studio, because Airbnb often leaves bedrooms empty for studios. "
        "Some hosts record their studio as 1 bedroom instead, so studios can "
        "have either 0 or 1 bedrooms."
    )

    for column in ["bathrooms", "bedrooms", "beds"]:
        missing = int(df[column].isna().sum())
        median_by_size = df.groupby("accommodates")[column].transform("median")
        df[column] = df[column].fillna(median_by_size).fillna(df[column].median())
        steps.append(
            f"Filled {missing:,} missing {column} with the median of listings "
            "that accommodate the same number of guests."
        )

    missing = int(df["reviews_per_month"].isna().sum())
    df["reviews_per_month"] = df["reviews_per_month"].fillna(0)
    steps.append(
        f"Filled {missing:,} missing reviews_per_month with 0, because they "
        "belong to listings with no reviews."
    )

    df["has_reviews"] = df["number_of_reviews"].gt(0)
    steps.append(
        f"Added a has_reviews column ({int((~df['has_reviews']).sum()):,} listings "
        "have no reviews). Their review scores are left missing, because filling "
        "them in would give unreviewed listings a typical score they never got."
    )

    missing = int(df["has_availability"].isna().sum())
    available = df["availability_365"].gt(0).map({True: "t", False: "f"})
    df["has_availability"] = df["has_availability"].fillna(available)
    steps.append(
        f"Filled {missing:,} missing has_availability from availability_365: "
        "'t' when the listing has any available days in the next year."
    )

    for column in BOOLEAN_COLUMNS:
        df[column] = df[column].eq("t")
    steps.append(
        f"Converted the 't'/'f' columns to True/False: {', '.join(BOOLEAN_COLUMNS)}."
    )

    for column in INTEGER_COLUMNS:
        df[column] = df[column].round().astype("Int64")
    steps.append(
        "Stored counts such as bedrooms and beds as whole numbers (1, not 1.0)."
    )

    for column, value in TEXT_FILL_VALUES.items():
        df[column] = df[column].fillna(value)
    steps.append(
        "Filled missing text: description and host_about with 'No description', "
        "host_location and license with 'Unknown'."
    )

    return df, steps


def build_report(
    dataset_path: Path, original: pd.DataFrame, cleaned: pd.DataFrame, steps: list[str]
) -> str:
    missing_before = original.isna().sum()
    missing_before = missing_before[missing_before.gt(0)]
    missing_after = cleaned.isna().sum().reindex(missing_before.index)
    missing = pd.DataFrame(
        {
            "missing_before": missing_before.map("{:,}".format),
            "missing_after": missing_after.map(
                lambda value: "dropped" if pd.isna(value) else f"{int(value):,}"
            ),
        }
    )
    remaining = cleaned.columns[cleaned.isna().any()].tolist()

    sections = [
        f"Cleaning and missing values: {dataset_path}",
        "=" * 80,
        f"Rows: {len(original):,} -> {len(cleaned):,}",
        f"Columns: {len(original.columns):,} -> {len(cleaned.columns):,}",
        f"Cells with missing values: {int(original.isna().sum().sum()):,} -> "
        f"{int(cleaned.isna().sum().sum()):,}",
        "",
        "Steps taken",
        "-" * 80,
        *(f"{number}. {step}" for number, step in enumerate(steps, start=1)),
        "",
        "Missing values by column, before and after",
        "-" * 80,
        missing.to_string(),
        "",
        "Columns still with missing values",
        "-" * 80,
        ", ".join(remaining) if remaining else "None",
        "These are left missing on purpose: first_review, last_review and the "
        "review scores have no value when a listing has no reviews.",
        "",
    ]
    return "\n".join(sections)


def main() -> int:
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    args = parse_args()
    dataset_path = args.dataset

    if not dataset_path.is_file():
        LOGGER.error("Dataset file does not exist or is not a file: %s", dataset_path)
        return 1
    if not dataset_path.name.lower().endswith((".csv", ".csv.gz")):
        LOGGER.error("Dataset must have a .csv or .csv.gz extension: %s", dataset_path)
        return 1
    if dataset_path.resolve() in (args.output.resolve(), args.report.resolve()):
        LOGGER.error("Output and report paths must not be the same as the input dataset.")
        return 1

    try:
        # As float64, host_profile_id (19 digits) would lose its last digits.
        original = pd.read_csv(
            dataset_path, low_memory=False, dtype={"host_profile_id": "Int64"}
        )
        cleaned, steps = clean_dataset(original)
        report = build_report(dataset_path, original, cleaned, steps)
        for path in (args.output, args.report):
            path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(args.output, index=False)
        args.report.write_text(report, encoding="utf-8")
    except (
        OSError,
        UnicodeError,
        ValueError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ) as exc:
        LOGGER.error("Could not clean the dataset or save the results: %s", exc)
        return 1

    print(report)
    print(f"Cleaned dataset saved to: {args.output}")
    print(f"Report saved to: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
