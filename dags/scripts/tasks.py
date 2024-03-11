"Airflow tasks"
# pylint: disable=import-outside-toplevel

from typing import Dict

from airflow.decorators import task
from airflow.models.dagrun import DagRun
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
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
        Dict[str, str]: date, raw_file_relative_path and cleaned_relative_path
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


@task.external_python(task_id="do_migrations", python=PATH_TO_PYTHON_BINARY)
def do_migrations(
    database_uri: str,
    folder_path,
) -> None:
    """Transforms the text file into a csv file.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        database_uri (str): uri of the database
        folder_path (Union[Path, CloudPath]): folder where the file will be saved
    """
    from weather_api.etl import migrate_database

    full_version_locations = folder_path / "versions"
    migrate_database(database_uri, full_version_locations)


@task.external_python(task_id="load_static_data", python=PATH_TO_PYTHON_BINARY)
def static_data(
    static_data_type: str,
    database_uri: str,
) -> None:
    """Transforms the text file into a csv file.

    Args:
        static_data (str), {"stations"}: type of data.
        database_uri (str): uri of the database
    """
    from weather_api.etl import load_static_data

    load_static_data(static_data_type, database_uri)


def get_trigger(
    query: str, date: str, load_dag_id: str, csv_file_relative_path
) -> TriggerDagRunOperator:
    """Returns a dag trigger operator used to trigger the load_dag.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        date (str): date required in the format YYYYMMDD
        load_dag_id (str): id of the load_dag
        csv_file_relative_path (Path | CloudPath): relative path for the file from folder_path

    Returns:
        TriggerDagRunOperator: dag trigger operator
    """
    return TriggerDagRunOperator(
        task_id="trigger_load",
        trigger_dag_id=load_dag_id,
        conf={
            "query": query,
            "date": date,
            "csv_file_relative_path": str(csv_file_relative_path),
        },
    )


@task
def get_load_dag_data(dag_run: DagRun) -> Dict[str, str]:
    """Gets data from the dag that triggered the load_dag.

    Args:
        dag_run (DagRun): data of the dag that trigered the load_dag.

    Returns:
        Dict[str, str]: query, date, csv_file_relative_path
    """
    load_dag_data = {}
    load_dag_data["query"] = dag_run.conf.get("query")
    load_dag_data["date"] = dag_run.conf.get("date")
    load_dag_data["csv_file_relative_path"] = dag_run.conf.get("csv_file_relative_path")
    return load_dag_data


@task.external_python(task_id="load_to_database", python=PATH_TO_PYTHON_BINARY)
def load_to_database(
    query: str, database_uri: str, folder_path, csv_file_relative_path: str
) -> None:
    """Loads the csv data into the database.

    Args:
        query (str): {"measured", "forecast"}: type of data required
        database_uri (str): uri of the database
        folder_path (Union[Path, CloudPath]): folder where the file will be saved
        csv_file_relative_path (str): relative path for the file from folder_path
    """
    from weather_api.etl import to_database

    full_csv_file_path = folder_path / csv_file_relative_path
    to_database(query, full_csv_file_path, database_uri)


@task.external_python(task_id="check_load_to_database", python=PATH_TO_PYTHON_BINARY)
def check_load_to_database(
    query: str, date: str, data_source_name: str, configuration_file_path
) -> None:
    """Data validation on the query tables using Soda.

    Args:
        query (str), {"measured", "forecast", "observations", "solar_radiation"}: type of data.
        date (str): date required in the format YYYYMMDD.
        data_source_name (str): data source name.
        configuration_file_path (Path): path to the datasource configuration path.
    """
    from weather_api.etl import check_to_database

    check_to_database(query, date, data_source_name, configuration_file_path)
