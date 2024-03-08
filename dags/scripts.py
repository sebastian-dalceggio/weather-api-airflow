"Airflow dag definition"
# pylint: disable=cell-var-from-loop

from typing import Dict

from airflow.decorators import dag
from airflow.models.baseoperator import chain
from airflow.models.dag import DAG

from dags.config import QUERIES
from dags.config.infra import storage_folder_path
from dags.tasks import get_current_data, download_raw
from dags.sensors import file_available_sensor

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

        date = current_data["date"]

        exists = file_available_sensor(query, date)

        download = download_raw(
            query, date, storage_folder_path, raw_file_relative_path
        )
        chain(current_data, exists, download)

    DAGS[query_data.query] = weather_api_dag()
