# weather-api-airflow

## Introduction

In this reposotory is implemented the package [weather-api](https://github.com/sebastian-dalceggio/weather-api) in Airflow to get data from the National Meteorological Service of Argentina (SMN).

## Docker

Airflow is started using Docker, using the docker-compose.yaml file from the official docs, making the necessary changes. A Postgres database is added to this same file, which will be used to load all the data.

A custom Docker image is used. The weather-api-airflow package is installed in the Airflow environment. It has the weather-api package as a dependency without the "etl" group. On the other hand, the weather-api package with the "etl" dependency group is installed in a virtual envirnment, which will be used for some of the tasks.

## Dags

The process has two dags:

1.  weather_api_dag: one is generated for each query using a for loop. Its function is to extract, validate and convert the data to CSV.
2.  load_data: load the CSV files into the database and perform subsequent transformations.

The tasks of each of the dags are detailed below. Those marked with an asterisk are those that run within the virtual environment.

### weather_api_dag

This dag has the following tasks:

1.  get_current_data: it returns the needed arguments for the subsequent tasks of the current execution.
2.  file_available_sensor: it checks the existence of a file in the origin. If there is no file, it repeats the verification every 30 minutes with a timeout of 24 hs.
3.  download_raw*: it downloads the text file and validate its composition.
4.  get_csv*: it transforms the file text into a CSV file and then saves it.
5.  trigger_load: it triggers the load_data dag.

### load_data

This dag has the following tasks:

1.  get_load_dag_data: it returns the needed arguments for the subsequent tasks of the current execution.
2.  do_migrations*: it creates or modifies the tables in the database.
3.  load_to_database*: it loads the CSV files in the database.
4.  check_load_to_database*: it validates the data in the database.