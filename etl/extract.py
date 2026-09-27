import io
import boto3
import pandas as pd

AWS_PROFILE = "mlops-dev"
AWS_REGION = "eu-north-1"
BUCKET_NAME = "priyanshu-mlops-household-energy-2026"
S3_KEY = "raw/household_energy_consumption.csv"


def extract_from_s3():
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION,
    )

    s3 = session.client("s3")

    print(f"Reading: s3://{BUCKET_NAME}/{S3_KEY}")

    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=S3_KEY
    )

    df = pd.read_csv(
        io.BytesIO(response["Body"].read())
    )

    print("\n✓ Dataset loaded from S3")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst 5 rows:")
    print(df.head())

    return df


if __name__ == "__main__":
    extract_from_s3()