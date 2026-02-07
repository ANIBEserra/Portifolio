from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from docker.types import Mount

# standard task configs
default_args = {
    'owner': 'beatriz_beserra',
    'depends_on_past': False,
    'start_date': datetime(2026, 2, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Dag definition
with DAG(
    'pipeline_ingestao_cnpj',
    default_args=default_args,
    description='Orquestrador para busca de CNPJs e upload para o GCS',
    schedule_interval='50 11 * * *', # 11:50 UTC is 08:50 BRT
    catchup=False,               # Does not try to run past days
    tags=['cnpj', 'gcs'],
) as dag:

    # Task to run the container
    task_rodar_projeto = DockerOperator(
        task_id='executar_busca_cnpj',
        image='pipeline-cnpj:latest',        # Image name built
        api_version='auto',
        auto_remove=True,                    # Delete the container after it finishes
        docker_url='unix://var/run/docker.sock', # Connect to the Docker Host
        network_mode='bridge',
    )

    task_rodar_projeto