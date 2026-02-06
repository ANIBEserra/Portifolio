from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from docker.types import Mount

# Configurações padrão para a tarefa
default_args = {
    'owner': 'beatriz_beserra',
    'depends_on_past': False,
    'start_date': datetime(2026, 2, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definição da DAG
with DAG(
    'pipeline_ingestao_cnpj',
    default_args=default_args,
    description='Orquestrador para busca de CNPJs e upload para o GCS',
    schedule_interval='50 11 * * *', # 11:50 UTC é 08:50 BRT
    catchup=False,               # Não tenta rodar dias retroativos
    tags=['cnpj', 'gcs'],
) as dag:

    # A tarefa que executa o container
    task_rodar_projeto = DockerOperator(
        task_id='executar_busca_cnpj',
        image='pipeline-cnpj:latest',        # Nome da imagem que você buildou
        api_version='auto',
        auto_remove=True,                    # Deleta o container após terminar
        docker_url='unix://var/run/docker.sock', # Permite falar com o Docker Host
        network_mode='bridge',
        # OPCIONAL: Se precisar mapear volumes locais para persistência no Windows,
        # você usaria o parâmetro 'mounts' aqui.
    )

    task_rodar_projeto