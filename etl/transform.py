import pandas as pd


def transform_dataset(df):
    print("\n" + "=" * 50)
    print("STARTING DATA TRANSFORMATION")
    print("=" * 50)

    df = df.copy()

    # -------------------------
    # Date transformation
    # -------------------------
    df["Date"] = pd.to_datetime(df["Date"])

    # -------------------------
    # Boolean transformation
    # -------------------------
    df["Has_AC"] = (
        df["Has_AC"]
        .map({
            "Yes": True,
            "No": False
        })
    )

    # -------------------------
    # Explicit numeric types
    # -------------------------
    df["Household_Size"] = (
        df["Household_Size"].astype("int16")
    )

    df["Energy_Consumption_kWh"] = (
        df["Energy_Consumption_kWh"].astype("float64")
    )

    df["Avg_Temperature_C"] = (
        df["Avg_Temperature_C"].astype("float64")
    )

    df["Peak_Hours_Usage_kWh"] = (
        df["Peak_Hours_Usage_kWh"].astype("float64")
    )

    # -------------------------
    # Rename columns for database
    # -------------------------
    df = df.rename(columns={
        "Household_ID": "household_id",
        "Date": "date",
        "Energy_Consumption_kWh": "energy_consumption_kwh",
        "Household_Size": "household_size",
        "Avg_Temperature_C": "avg_temperature_c",
        "Has_AC": "has_ac",
        "Peak_Hours_Usage_kWh": "peak_hours_usage_kwh",
    })

    # -------------------------
    # Transformation summary
    # -------------------------

    print("\n✓ Date converted")
    print("✓ Has_AC converted to boolean")
    print("✓ Numeric types standardized")
    print("✓ Column names normalized for PostgreSQL")

    print("\nTransformed columns:")
    print(df.columns.tolist())

    print("\nTransformed data:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\n" + "=" * 50)
    print("✓ TRANSFORMATION COMPLETE")
    print("=" * 50)

    return df