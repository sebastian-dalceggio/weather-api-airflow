"Airflow dag definition"
# pylint: disable=cell-var-from-loop

from typing import Dict

from airflow.decorators import dag
from airflow.models.baseoperator import chain
from airflow.models.dag import DAG
import pendulum

from scripts.tasks import (
    get_current_data,
    download_raw,
    get_csv,
    do_migrations,
    get_trigger,
    get_load_dag_data,
    load_to_database,
    check_load_to_database,
)
from scripts.sensors import file_available_sensor

from config.queries import QUERIES
from config.config import LOCAL_DATABASE_NAME, SODA_CONFIGURATION_PATH
from config.infra import storage_folder_path, database_uri

DAGS: Dict[str, DAG] = {}

for query_data in QUERIES:

    @dag(
        dag_id=f"{query_data.query}",
        schedule="@daily",
        start_date=query_data.start_date,
        end_date=query_data.end_date,
        max_active_runs=1,
    )
    def weather_api_dag():
        """Weather api dag"""

        query = query_data.query
        current_data = get_current_data(query, "{{  data_interval_end }}")
        raw_file_relative_path = current_data["raw_file_relative_path"]
        csv_file_relative_path = current_data["csv_file_relative_path"]

        date = current_data["date"]

        exists = file_available_sensor(query, date)

        download = download_raw(
            query, date, storage_folder_path, raw_file_relative_path
        )
        csv = get_csv(
            query,
            date,
            storage_folder_path,
            raw_file_relative_path,
            csv_file_relative_path,
        )
        trigger_load = get_trigger(query, date, "load_data_dag", csv_file_relative_path)

        chain(current_data, exists, download, csv, trigger_load)

    DAGS[query_data.query] = weather_api_dag()


@dag(
    dag_id="load_data_dag",
    start_date=pendulum.today(),
    max_active_runs=1,
)
def load_dag():
    """Load data dag"""
    load_dag_data = get_load_dag_data()  # pylint: disable=no-value-for-parameter
    query = load_dag_data["query"]
    date = load_dag_data["date"]
    csv_file_relative_path = load_dag_data["csv_file_relative_path"]

    migrations = do_migrations(database_uri, storage_folder_path)
    load = load_to_database(
        query, database_uri, storage_folder_path, csv_file_relative_path
    )
    first_check = check_load_to_database(
        query, date, LOCAL_DATABASE_NAME, SODA_CONFIGURATION_PATH
    )
    chain(load_dag_data, migrations, load, first_check)


load_dag()
