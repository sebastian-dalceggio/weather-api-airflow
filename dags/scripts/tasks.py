"Airflow tasks"
# pylint: disable=import-outside-toplevel

from typing import Dict

from airflow.decorators import task
import pendulum

from config.config import PATH_TO_PYTHON_BINARY

EXTENSION: Dict[str, str] = {"raw": "txt", "csv": "csv"}


@task(task_id="get_run_data", multiple_outputs=True)
def get_current_data(query: str, date: str) -> Dict[str, str]:
    """Returns the date and paths used for the current run of the etl process.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        date (str): data_interval_end as airflow gives it in the format
        2022-07-28T16:20:00+00:00

    Returns:
        Tuple[str, str, str]: date, raw_file_relative_path and
            cleaned_relative_path
    """
    from weather_api.etl_extras import get_run_data

    return get_run_data(query, date)


@task.external_python(
    task_id="download_raw",
    python=PATH_TO_PYTHON_BINARY,
    retries=1,
    retry_delay=pendulum.duration(minutes=30),
)
def download_raw(
    query: str, date: str, folder_path, raw_file_relative_path: str
) -> None:
    """Downloads raw data.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        date (str): date required in the format YYYYMMDD
        folder_path (Union[Path, CloudPath]): folder where the file will be saved
        raw_file_relative_path (str): relative path for the file from folder_path
    """
    from weather_api.etl import download, validate_raw

    full_raw_path = folder_path / raw_file_relative_path
    download(query, date, full_raw_path)
    validate_raw(query, date, full_raw_path)


@task.external_python(task_id="get_csv", python=PATH_TO_PYTHON_BINARY)
def get_csv(
    query: str,
    date: str,
    folder_path,
    text_file_relative_path: str,
    csv_file_relative_path: str,
) -> None:
    """Transforms the text file into a csv file.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        date (str): date required in the format YYYYMMDD
        folder_path (Union[Path, CloudPath]): folder where the file will be saved
        text_file_relative_path (str): relative path for the file from folder_path
        csv_file_relative_path (str): relative path for the file from folder_path
    """
    from weather_api.etl import to_csv

    full_text_file_path = folder_path / text_file_relative_path
    full_csv_file_path = folder_path / csv_file_relative_path
    to_csv(query, date, full_text_file_path, full_csv_file_path)
