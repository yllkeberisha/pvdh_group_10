# London Airbnb Listings Exploration

This project provides a read-only initial inspection of the London listings
dataset from Inside Airbnb. It reports the dataset shape, column names and
types, first five rows, descriptive statistics, missing values, exact duplicate
rows, and unique-value counts. It does not clean or transform the data.

## Project layout

```text
.
├── dataset/
│   └── listings.csv.gz
├── reports/
│   └── listings_inspection.txt
├── scripts/
│   └── inspect_listings.py
├── requirements.txt
└── README.md
```

## Setup

Use Python 3.10 or newer. From the project root, create and activate a virtual
environment in PowerShell, then install the dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Pass the path to an uncompressed CSV or a gzip-compressed `.csv.gz` file:

```powershell
python scripts\inspect_listings.py dataset\listings.csv.gz
python scripts\inspect_listings.py path\to\listings.csv.gz
```

The report is printed to the console and saved by default to
`reports/listings_inspection.txt`. Choose another report location with
`--report`:

```powershell
python scripts\inspect_listings.py dataset\listings.csv --report reports\my_inspection.txt
```

The input dataset is only read; the script does not modify it.
