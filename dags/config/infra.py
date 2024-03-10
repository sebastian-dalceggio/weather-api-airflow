"Infra data"

from pathlib import Path
from config.config import LOCAL_DATABASE

storage_folder_path = Path("/opt/airflow/storage/")
database_uri = LOCAL_DATABASE
