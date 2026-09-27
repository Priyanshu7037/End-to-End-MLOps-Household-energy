import pandas as pd


REQUIRED_COLUMNS = [
    "Household_ID",
    "Date",
    "Energy_Consumption_kWh",
    "Household_Size",
    "Avg_Temperature_C",
    "Has_AC",
    "Peak_Hours_Usage_kWh",
]

ALLOWED_AC_VALUES = {"Yes", "No"}


def validate_schema(df):
    print("\n=== SCHEMA VALIDATION ===")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("✓ Required columns present")


def validate_missing_values(df):
    print("\n=== MISSING VALUE VALIDATION ===")

    missing = df[REQUIRED_COLUMNS].isnull().sum()

    print(missing)

    total_missing = missing.sum()

    if total_missing > 0:
        raise ValueError(
            f"Dataset contains {total_missing} missing values"
        )

    print("✓ No missing values")


def validate_duplicates(df):
    print("\n=== DUPLICATE VALIDATION ===")

    duplicates = df.duplicated().sum()

    print(f"Duplicate rows: {duplicates}")

    if duplicates > 0:
        raise ValueError(
            f"Dataset contains {duplicates} duplicate rows"
        )

    print("✓ No duplicate rows")


def validate_dates(df):
    print("\n=== DATE VALIDATION ===")

    dates = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    invalid_dates = dates.isna().sum()

    print(f"Invalid dates: {invalid_dates}")

    if invalid_dates > 0:
        raise ValueError(
            f"Found {invalid_dates} invalid dates"
        )

    print("✓ All dates are valid")


def validate_numeric_values(df):
    print("\n=== NUMERIC VALIDATION ===")

    numeric_columns = [
        "Energy_Consumption_kWh",
        "Household_Size",
        "Avg_Temperature_C",
        "Peak_Hours_Usage_kWh",
    ]

    for column in numeric_columns:
        invalid = pd.to_numeric(
            df[column],
            errors="coerce"
        ).isna().sum()

        print(f"{column}: {invalid} invalid values")

        if invalid > 0:
            raise ValueError(
                f"{column} contains invalid numeric values"
            )

    print("✓ Numeric columns valid")


def validate_business_rules(df):
    print("\n=== BUSINESS RULE VALIDATION ===")

    # Household size
    invalid_household_size = (
        (df["Household_Size"] <= 0)
    ).sum()

    print(
        f"Invalid household sizes: "
        f"{invalid_household_size}"
    )

    if invalid_household_size > 0:
        raise ValueError(
            "Household_Size must be greater than 0"
        )

    # Energy consumption
    invalid_energy = (
        df["Energy_Consumption_kWh"] < 0
    ).sum()

    print(
        f"Negative energy consumption: "
        f"{invalid_energy}"
    )

    if invalid_energy > 0:
        raise ValueError(
            "Energy consumption cannot be negative"
        )

    # Peak usage
    invalid_peak = (
        df["Peak_Hours_Usage_kWh"] < 0
    ).sum()

    print(
        f"Negative peak usage: "
        f"{invalid_peak}"
    )

    if invalid_peak > 0:
        raise ValueError(
            "Peak hours usage cannot be negative"
        )

    # AC values
    invalid_ac = ~df["Has_AC"].isin(ALLOWED_AC_VALUES)

    invalid_ac_count = invalid_ac.sum()

    print(
        f"Invalid Has_AC values: "
        f"{invalid_ac_count}"
    )

    if invalid_ac_count > 0:
        raise ValueError(
            "Has_AC must contain only Yes or No"
        )

    print("✓ Business rules passed")


def validate_dataset(df):
    print("\n" + "=" * 50)
    print("STARTING DATA VALIDATION")
    print("=" * 50)

    validate_schema(df)
    validate_missing_values(df)
    validate_duplicates(df)
    validate_dates(df)
    validate_numeric_values(df)
    validate_business_rules(df)

    print("\n" + "=" * 50)
    print("✓ ALL VALIDATIONS PASSED")
    print("=" * 50)

    return True