"Airflow sensors"

from airflow.decorators import task
from airflow.sensors.base import PokeReturnValue


@task.sensor(poke_interval=10, timeout=10, mode="reschedule")
def file_available_sensor(query: str, date: str) -> PokeReturnValue:
    """Downloads required data from SMN web.

    Args:
        query (str): {"measured", "forecast", "observations", "solar_radiation"}: type of data
            required
        date (str): date required in the format YYYYMMDD
    """
    from weather_api.etl_extras import (  # pylint: disable=import-outside-toplevel
        check_file_availability,
    )

    result = check_file_availability(query, date)
    return PokeReturnValue(is_done=result)
