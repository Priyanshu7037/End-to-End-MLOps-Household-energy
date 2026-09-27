import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    raise ValueError(
        "Missing database configuration in .env"
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
    query={"sslmode": "require"},
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
)


# =========================================================
# LOAD INTO STAGING
# =========================================================

def load_to_staging(df):
    """
    Load the current ETL result into staging.

    Staging represents the data produced by
    the current pipeline execution.
    """

    print("\n" + "=" * 60)
    print("LOADING DATA INTO STAGING")
    print("=" * 60)

    with engine.begin() as connection:

        # Staging is temporary/current-run data.
        connection.execute(
            text("TRUNCATE TABLE staging.household_energy")
        )

        df.to_sql(
            name="household_energy",
            schema="staging",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
        )

    print(
        f"✓ Loaded {len(df):,} rows "
        "into staging.household_energy"
    )

    return len(df)


# =========================================================
# STAGING QUALITY CHECK
# =========================================================

def validate_staging():
    """
    Validate the data currently present in staging.
    """

    print("\n" + "=" * 60)
    print("VALIDATING STAGING DATA")
    print("=" * 60)

    checks = {}

    with engine.connect() as connection:

        # Row count
        row_count = connection.execute(
            text(
                "SELECT COUNT(*) "
                "FROM staging.household_energy"
            )
        ).scalar_one()

        checks["row_count"] = row_count

        # NULL check
        null_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.household_energy
                WHERE household_id IS NULL
                   OR date IS NULL
                   OR energy_consumption_kwh IS NULL
                   OR household_size IS NULL
                   OR avg_temperature_c IS NULL
                   OR has_ac IS NULL
                   OR peak_hours_usage_kwh IS NULL
            """)
        ).scalar_one()

        checks["null_count"] = null_count

        # Negative energy values
        negative_energy = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.household_energy
                WHERE energy_consumption_kwh < 0
            """)
        ).scalar_one()

        checks["negative_energy"] = negative_energy

        # Invalid household size
        invalid_household_size = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.household_energy
                WHERE household_size <= 0
            """)
        ).scalar_one()

        checks["invalid_household_size"] = invalid_household_size

    print(f"Rows in staging       : {checks['row_count']:,}")
    print(f"NULL values           : {checks['null_count']:,}")
    print(f"Negative energy       : {checks['negative_energy']:,}")
    print(
        "Invalid household size: "
        f"{checks['invalid_household_size']:,}"
    )

    # Overall quality decision
    if checks["row_count"] == 0:
        raise ValueError("Staging table is empty.")

    if checks["null_count"] > 0:
        raise ValueError("Staging contains NULL values.")

    if checks["negative_energy"] > 0:
        raise ValueError(
            "Staging contains negative energy values."
        )

    if checks["invalid_household_size"] > 0:
        raise ValueError(
            "Staging contains invalid household sizes."
        )

    print("\n✓ STAGING QUALITY CHECK PASSED")

    return True


# =========================================================
# PROMOTE STAGING → CURATED
# =========================================================

def promote_to_curated():
    """
    Promote validated staging data into curated.

    Curated is only updated after staging passes
    all quality checks.
    """

    print("\n" + "=" * 60)
    print("PROMOTING STAGING → CURATED")
    print("=" * 60)

    with engine.begin() as connection:

        # Replace curated dataset only after staging
        # has successfully passed validation.
        connection.execute(
            text("TRUNCATE TABLE curated.household_energy")
        )

        connection.execute(
            text("""
                INSERT INTO curated.household_energy (
                    household_id,
                    date,
                    energy_consumption_kwh,
                    household_size,
                    avg_temperature_c,
                    has_ac,
                    peak_hours_usage_kwh
                )
                SELECT
                    household_id,
                    date,
                    energy_consumption_kwh,
                    household_size,
                    avg_temperature_c,
                    has_ac,
                    peak_hours_usage_kwh
                FROM staging.household_energy
            """)
        )

        row_count = connection.execute(
            text(
                "SELECT COUNT(*) "
                "FROM curated.household_energy"
            )
        ).scalar_one()

    print(
        f"✓ Promoted {row_count:,} rows "
        "into curated.household_energy"
    )

    return row_count