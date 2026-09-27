import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    raise ValueError("Missing database configuration in .env")


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


def start_etl_run(pipeline_name, source_file, rows_extracted):
    """
    Create a RUNNING record for the current ETL execution.
    """

    run_id = uuid.uuid4()

    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO metadata.etl_runs (
                    run_id,
                    pipeline_name,
                    source_file,
                    rows_extracted,
                    status
                )
                VALUES (
                    :run_id,
                    :pipeline_name,
                    :source_file,
                    :rows_extracted,
                    'RUNNING'
                )
            """),
            {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "source_file": source_file,
                "rows_extracted": rows_extracted,
            },
        )

    print(f"✓ ETL run started: {run_id}")

    return run_id


def complete_etl_run(run_id, rows_loaded):
    """
    Mark the ETL execution as successful.
    """

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE metadata.etl_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    rows_loaded = :rows_loaded,
                    status = 'SUCCESS'
                WHERE run_id = :run_id
            """),
            {
                "run_id": run_id,
                "rows_loaded": rows_loaded,
            },
        )

    print(f"✓ ETL run completed: {run_id}")


def fail_etl_run(run_id, error_message):
    """
    Mark the ETL execution as failed.
    """

    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE metadata.etl_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    status = 'FAILED',
                    error_message = :error_message
                WHERE run_id = :run_id
            """),
            {
                "run_id": run_id,
                "error_message": str(error_message),
            },
        )

    print(f"✗ ETL run failed: {run_id}")