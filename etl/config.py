import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "energy_db")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "your_password")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def admin_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/postgres"


@dataclass
class MLflowConfig:
    tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    experiment_name: str = "household-energy"


@dataclass
class DataConfig:
    raw_path: str = "data/raw"
    processed_path: str = "data/processed"
    external_path: str = "data/external"
    chunk_size: int = 10000


@dataclass
class PipelineConfig:
    db: DatabaseConfig = DatabaseConfig()
    mlflow: MLflowConfig = MLflowConfig()
    data: DataConfig = DataConfig()
    batch_size: int = 1000
    validation_threshold: float = 0.95


config = PipelineConfig()