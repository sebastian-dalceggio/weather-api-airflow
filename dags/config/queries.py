"Queries airflow data"

import pendulum

from config.utils import QueryData

QUERIES = [
    QueryData(
        "measured",
        pendulum.datetime(2017, 11, 26, tz="America/Argentina/Buenos_Aires"),
        pendulum.datetime(2017, 11, 30, tz="America/Argentina/Buenos_Aires"),
    ),
    QueryData(
        "forecast",
        pendulum.datetime(2017, 12, 28, tz="America/Argentina/Buenos_Aires"),
        pendulum.datetime(2018, 1, 4, tz="America/Argentina/Buenos_Aires"),
    ),
    QueryData(
        "observations",
        pendulum.datetime(2023, 3, 28, tz="America/Argentina/Buenos_Aires"),
        pendulum.datetime(2023, 3, 30, tz="America/Argentina/Buenos_Aires"),
    ),
    QueryData(
        "solar_radiation",
        pendulum.datetime(2017, 12, 28, tz="America/Argentina/Buenos_Aires"),
        pendulum.datetime(2017, 12, 31, tz="America/Argentina/Buenos_Aires"),
    ),
]
