"""Clean an Airbnb listings CSV, handle its missing values, and save a report."""

import argparse
import logging
from pathlib import Path

import pandas as pd


LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT = Path("dataset") / "listings_clean.csv"
DEFAULT_REPORT = Path("reports") / "listings_cleaning.txt"
PRICE_UPPER_QUANTILE = 0.99
PRICE_DROP_QUANTILE = 0.999
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


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load a CSV; Pandas infers gzip compression from the .csv.gz suffix."""
    # As float64, host_profile_id (19 digits) would lose its last digits.
    return pd.read_csv(dataset_path, low_memory=False, dtype={"host_profile_id": "Int64"})


def bathrooms_from_text(bathrooms_text: pd.Series) -> pd.Series:
    """Read the number from text such as '1.5 shared baths'; 'Half-bath' is 0.5 and
    'No bathroom' is 0."""
    text = bathrooms_text.astype("string")
    numbers = text.str.extract(r"(\d+(?:\.\d+)?)")[0].astype(float)
    half_bath = text.str.contains("half", case=False, na=False)
    no_bath = text.str.contains(r"^no bath", case=False, na=False)
    return numbers.mask(numbers.isna() & half_bath, 0.5).mask(numbers.isna() & no_bath, 0.0)


def clean_dataset(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return the cleaned dataframe and a description of every step taken."""
    df = dataframe.copy()
    steps = []

    # bathrooms can be completely empty, but it is rebuilt from bathrooms_text below.
    empty_columns = [
        column for column in df.columns[df.isna().all()] if column != "bathrooms"
    ]
    df = df.drop(columns=empty_columns)
    steps.append(
        f"Dropped {len(empty_columns)} completely empty columns, because they "
        f"hold no information: {', '.join(empty_columns)}. bathrooms is kept, "
        "because it is rebuilt from bathrooms_text."
    )

    rows_before = len(df)
    df = df.drop_duplicates(subset="id")
    steps.append(f"Removed {rows_before - len(df):,} duplicate listings (same id).")

    df["price"] = pd.to_numeric(
        df["price"].astype("string").str.replace(r"[$,]", "", regex=True)
    )
    steps.append(
        "Converted price from text such as '$1,180.00' to a number by removing "
        "the '$' and the thousands commas."
    )

    rows_before = len(df)
    unpriced = df["price"].isna()
    unpriced_no_days = df.loc[unpriced, "availability_365"].eq(0).mean()
    priced_no_days = df.loc[~unpriced, "availability_365"].eq(0).mean()
    unpriced_previous = df.loc[unpriced, "source"].eq("previous scrape").mean()
    df = df.dropna(subset=["price"])
    steps.append(
        f"Dropped {rows_before - len(df):,} rows without a price. Price is the "
        "main variable for analysis, so filling it in would invent the values "
        f"we want to study. These listings are mostly not bookable: {unpriced_no_days:.0%} "
        "have no available days in the next year (against "
        f"{priced_no_days:.1%} of the listings with a price), and "
        f"{unpriced_previous:.0%} have source = 'previous scrape'."
    )

    rows_before = len(df)
    highest_price = df["price"].max()
    drop_limits = df.groupby("room_type")["price"].quantile(PRICE_DROP_QUANTILE)
    df = df[~df["price"].gt(df["room_type"].map(drop_limits))].copy()
    steps.append(
        f"Dropped {rows_before - len(df):,} rows with a price above the "
        f"{PRICE_DROP_QUANTILE * 100:.1f}th percentile of their own room type "
        f"({', '.join(f'{room} {limit:,.0f}' for room, limit in drop_limits.items())}; "
        f"the highest price was {highest_price:,.0f}). A price that is normal for an "
        "entire home can be an error for a single room. Prices this extreme distort "
        "averages and scaling, so they are removed before the 99th-percentile flag below."
    )

    previous = df["source"].eq("previous scrape")
    steps.append(
        f"Kept {int(previous.sum()):,} listings with a price and source = "
        f"'previous scrape' ({previous.mean():.1%} of the rows). Their median price is "
        f"{df.loc[previous, 'price'].median():,.0f} against "
        f"{df.loc[~previous, 'price'].median():,.0f} for the others, so nothing shows "
        "their prices are wrong. They do have fewer available days (median "
        f"{df.loc[previous, 'availability_365'].median():.0f} against "
        f"{df.loc[~previous, 'availability_365'].median():.0f})."
    )

    price_limit = df["price"].quantile(PRICE_UPPER_QUANTILE)
    df["price_above_p99"] = df["price"].gt(price_limit)
    steps.append(
        f"Flagged {int(df['price_above_p99'].sum()):,} listings with a price above "
        f"the {PRICE_UPPER_QUANTILE * 100:.0f}th percentile ({price_limit:,.2f}) in "
        "price_above_p99. They are kept, because they may be genuine luxury listings."
    )

    missing_bathrooms = int(df["bathrooms"].isna().sum())
    df["bathrooms"] = df["bathrooms"].fillna(bathrooms_from_text(df["bathrooms_text"]))
    steps.append(
        f"Filled {missing_bathrooms - int(df['bathrooms'].isna().sum()):,} missing "
        "bathrooms from the number in bathrooms_text (e.g. '1.5 baths' -> 1.5)."
    )

    for column in ["bathrooms", "bedrooms", "beds"]:
        missing = int(df[column].isna().sum())
        median_by_size = df.groupby("accommodates")[column].transform("median")
        df[column] = df[column].fillna(median_by_size).fillna(df[column].median())
        steps.append(
            f"Filled {missing:,} missing {column} with the median of listings "
            "that accommodate the same number of guests."
        )

    no_reviews = df["number_of_reviews"].eq(0) & df["reviews_per_month"].isna()
    df.loc[no_reviews, "reviews_per_month"] = 0
    steps.append(
        f"Filled {int(no_reviews.sum()):,} missing reviews_per_month with 0, only "
        "for listings with no reviews."
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
        df[column] = df[column].map({"t": True, "f": False}).astype("boolean")
    steps.append(
        f"Converted the 't'/'f' columns to True/False: {', '.join(BOOLEAN_COLUMNS)}. "
        "A missing value stays missing; it is not turned into False."
    )

    for column in INTEGER_COLUMNS:
        df[column] = df[column].round().astype("Int64")
    steps.append(
        "Stored counts such as bedrooms and beds as whole numbers (1, not 1.0)."
    )

    return df, steps


def missing_action(column: str, original: pd.DataFrame, cleaned: pd.DataFrame) -> str:
    """Say what cleaning did to a column that has missing values."""
    if column not in cleaned:
        return "column dropped"
    before = original.loc[cleaned.index, column].isna().sum()
    after = cleaned[column].isna().sum()
    if after < before:
        return "filled"
    return "rows dropped" if before == 0 else "kept missing"


def missing_value_table(original: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    """One row per column with missing values: how many before and after cleaning,
    and what cleaning did to it."""
    missing_before = original.isna().sum()
    missing_before = missing_before[missing_before.gt(0)]
    return pd.DataFrame(
        {
            "missing_before": missing_before,
            "missing_after": cleaned.isna().sum().reindex(missing_before.index),
            "action": [
                missing_action(column, original, cleaned)
                for column in missing_before.index
            ],
        }
    )


def build_report(
    dataset_path: Path, original: pd.DataFrame, cleaned: pd.DataFrame, steps: list[str]
) -> str:
    missing = missing_value_table(original, cleaned)
    missing["missing_before"] = missing["missing_before"].map("{:,}".format)
    missing["missing_after"] = missing["missing_after"].map(
        lambda value: "dropped" if pd.isna(value) else f"{int(value):,}"
    )

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
        "Missing values by column: before (all rows) and after (kept rows)",
        "-" * 80,
        missing.to_string(),
        "",
        "What the action means",
        "-" * 80,
        "column dropped: every row was empty. filled: see the steps above for how. "
        "rows dropped: the gap was only in rows that were removed. kept missing: "
        "left on purpose, for these reasons:",
        "- first_review, last_review and the review scores: a listing with no "
        "reviews has no date or score, and filling it in would give it one it "
        "never got.",
        "- description, host_location, host_about: free text, not filled with "
        "made-up text.",
        "- source: its only value is 'previous scrape'; it is a label.",
        "- bathrooms_text, price_quote_* and the minimum/maximum nights columns: "
        "small gaps that the price analysis does not need.",
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
        original = load_dataset(dataset_path)
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
