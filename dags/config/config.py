"Config variables for airflow"

from decouple import AutoConfig  # type: ignore

PATH_TO_PYTHON_BINARY: str = "/opt/airflow/weather-api/.venv/bin/python"

# env section

dconfig = AutoConfig()

LOCAL_DATABASE_TYPE: str = dconfig("LOCAL_DATABASE_TYPE", cast=str)
LOCAL_DATABASE_USER: str = dconfig("LOCAL_DATABASE_USER", cast=str)
LOCAL_DATABASE_PASSWORD: str = dconfig("LOCAL_DATABASE_PASSWORD", cast=str)
LOCAL_DATABASE_HOST: str = dconfig("LOCAL_DATABASE_HOST", cast=str)
LOCAL_DATABASE_NAME: str = dconfig("LOCAL_DATABASE_NAME", cast=str)
LOCAL_DATABASE: str = (
    f"{LOCAL_DATABASE_TYPE}://{LOCAL_DATABASE_USER}:{LOCAL_DATABASE_PASSWORD}@"
    f"{LOCAL_DATABASE_HOST}/{LOCAL_DATABASE_NAME}"
)
