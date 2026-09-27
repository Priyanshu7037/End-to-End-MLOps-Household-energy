from etl.extract import extract_from_s3
from etl.validate import validate_dataset
from etl.transform import transform_dataset

from etl.load import (
    load_to_staging,
    validate_staging,
    promote_to_curated,
)

from etl.metadata import (
    start_etl_run,
    complete_etl_run,
    fail_etl_run,
)


PIPELINE_NAME = "household_energy_etl"
SOURCE_FILE = "raw/household_energy_consumption.csv"


def run_pipeline():

    print("\n")
    print("=" * 60)
    print("HOUSEHOLD ENERGY ETL PIPELINE")
    print("=" * 60)

    run_id = None

    try:

        # -------------------------------------------------
        # 1. EXTRACT
        # -------------------------------------------------

        df = extract_from_s3()

        # -------------------------------------------------
        # 2. START ETL RUN
        # -------------------------------------------------

        run_id = start_etl_run(
            pipeline_name=PIPELINE_NAME,
            source_file=SOURCE_FILE,
            rows_extracted=len(df),
        )

        # -------------------------------------------------
        # 3. VALIDATE
        # -------------------------------------------------

        validate_dataset(df)

        # -------------------------------------------------
        # 4. TRANSFORM
        # -------------------------------------------------

        df = transform_dataset(df)

        # -------------------------------------------------
        # 5. LOAD → STAGING
        # -------------------------------------------------

        load_to_staging(df)

        # -------------------------------------------------
        # 6. VALIDATE STAGING
        # -------------------------------------------------

        validate_staging()

        # -------------------------------------------------
        # 7. PROMOTE → CURATED
        # -------------------------------------------------

        rows_curated = promote_to_curated()

        # -------------------------------------------------
        # 8. MARK SUCCESS
        # -------------------------------------------------

        complete_etl_run(
            run_id=run_id,
            rows_loaded=rows_curated,
        )

        print("\n")
        print("=" * 60)
        print("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"Rows extracted : {len(df):,}")
        print(f"Rows curated   : {rows_curated:,}")
        print(f"Run ID         : {run_id}")

    except Exception as error:

        print("\n")
        print("=" * 60)
        print("✗ ETL PIPELINE FAILED")
        print("=" * 60)

        print(f"Error: {error}")

        if run_id is not None:
            fail_etl_run(
                run_id=run_id,
                error_message=error,
            )

        raise


if __name__ == "__main__":
    run_pipeline()