"Airflow tasks"
# pylint: disable=import-outside-toplevel

from typing import Dict

from airflow.decorators import task

# from dags.config.config import PATH_TO_PYTHON_BINARY

EXTENSION: Dict[str, str] = {"raw": "txt", "csv": "csv"}


@task(task_id="get_run_data", multiple_outputs=True)
def get_current_data(query: str, date: str) -> Dict[str, str]:
    """Returns the date and paths used for the current run of the etl process.

    Args:
        query (str), {"measured", "forecast"}: type of data required
        date (str): data_interval_end as airflow gives it in the format
        2022-07-28T16:20:00+00:00

    Returns:
        Tuple[str, str, str]: date, raw_file_relative_path and
            cleaned_relative_path
    """
    from weather_api.etl_extras import get_run_data

    return get_run_data(query, date)
