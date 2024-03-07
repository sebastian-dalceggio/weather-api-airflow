FROM apache/airflow:2.8.2-python3.10

USER root
RUN apt update && apt install git -y

USER 50000
RUN pip install poetry
RUN pip install 'git+https://github.com/sebastian-dalceggio/weather-api.git#egg=weather_api_airflow&subdirectory=airflow_scripts'
WORKDIR /opt/airflow/
RUN poetry config virtualenvs.in-project true
RUN git clone https://github.com/sebastian-dalceggio/weather-api.git
RUN cd weather-api && poetry install --with etl