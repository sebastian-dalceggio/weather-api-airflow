# weather-api-airflow

## Introducción

En este repositorio se implenta el paquete [weather-api](https://github.com/sebastian-dalceggio/weather-api) en Airflow para la obtención de datos de la página web del servicio meteorológico nacional.

## Docker

Para utilizar Airflow se usa Docker, usando el archivo docker-compose.yaml que ofrece la documentación oficial, realizándole los cambios necesarios. A este mismo archivo se le agrega una base de datos Postgres en la cual se van a cargar todos los datos.

Se utiliza una imagen customizada de docker para poder instalarle el paquete weather-api. En el ambiente de Airflow se instala directamente el paquete weather-api-airflow el cual tiene como dependencia el paquete weather-api sin el grupo de dependencias "etl". Por otro lado el paquete weather-api con el grupo "etl" se instala en un virtual environment que va a ser utilizado por las tasks.

## Dags

El proceso cuenta con dos dags:

1.  weather_api_dag: el cual se genera para cada una de las queries usando un for loop. Su función es la de extraer, validar y convertir en csv los datos.
2.  load_data: el cual se encarga de cargar los archivos csv en la base de datos y de las transformaciones posteriores.

A continuación se detallan las tareas de cada uno de los dags. Las marcadas con asterisco son aquellas que corren dentro del virtual environment.

### weather_api_dag

Este dag cuenta con las siguientes tareas:

1.  get_current_data: devuelve los argumentos necesarios para las subsiguientes tareas para la actual corrida
2.  file_available_sensor: sensor que verifica la existencia del archivo en el origen. En caso de no existir, repite la búsqueda cada media hora con un time out de 24 hs.
3.  download_raw*: descarga el archivo de texto y valida su composición.
4.  get_csv:* transforma el archivo de texto en un archivo csv y lo guarda.
5.  trigger_load: dispara el funcionamiento del dag load_data.

### load_data

Este dag cuenta con las siguientes tareas:

1.  get_load_dag_data: devuelve los argumentos necesarios para las subsiguientes tareas para la actual corrida.
2.  do_migrations*: crea o modifica el esquema de las tablas en la base datos.
3.  load_to_database*: carga los archivos csv en la base datos.
4.  check_load_to_database*: valida los datos de las tablas de la base de datos.