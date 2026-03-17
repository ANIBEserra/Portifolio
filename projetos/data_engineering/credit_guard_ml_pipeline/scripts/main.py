import requests
import json
import os
import pandas as pd
from time import sleep
import re
from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime
from pathlib import Path
import pytz
from dotenv import load_dotenv
import sys
import shutil

sys.path.append(str(Path(__file__).resolve().parent.parent))
from configs.mapping import (
    RENAME_QSA, RENAME_CNAE, RENAME_REGIME, FULL_METADATA_MAP
)

load_dotenv()

# config base directory
BASE_DIR = Path(__file__).resolve().parent.parent
KEY_PATH = os.path.join(BASE_DIR, 'key-google.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

# config data paths
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'input', 'cnpjs.csv')
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw')
GITHUB_DATA_PATH = os.path.join(BASE_DIR, 'data', 'github')
SILVER_DATA_PATH = os.path.join(BASE_DIR, 'data', 'silver')

os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(GITHUB_DATA_PATH, exist_ok=True)
os.makedirs(SILVER_DATA_PATH, exist_ok=True)

# config google cloud and github
CLIENT = storage.Client()
CLIENT_BQ = bigquery.Client()
BUCKET = CLIENT.bucket('credit-guard-raw-sa-east1')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# -------------------------- AUXILIARY FUNCTIONS --------------------------
def expand_and_rename(df_orig: pd.DataFrame, col_name: str, rename_dict: dict) -> pd.DataFrame:
    if col_name in df_orig.columns and not df_orig[col_name].dropna().empty:
        extracted = df_orig[col_name].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {})
        df_norm = pd.json_normalize(extracted)
        return df_norm.rename(columns=rename_dict)
    return pd.DataFrame()
    
# -------------------------- RAW DATA INGESTION  FUNCTIONS --------------------------
def buscar_cnpj(cnpj):
    cnpj= re.sub(r'\D', '', str(cnpj))
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        response = requests.get(url)
        if response.status_code==200:
            data = response.json()
            
            fuso_br = pytz.timezone('America/Sao_Paulo') # SP timezone
            today = datetime.now(fuso_br).strftime('%Y-%m-%d') # today's date
            file_path = os.path.join(RAW_DATA_PATH, f"{cnpj}_{today}.json") # file path

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"File saved successfully at: {file_path}")

        else:
            print(f"{response.status_code} for cnpj {cnpj}")
    except Exception as e:
        print(f"Connection failed {e}")


def data_injection_raw(file_name):
    try:
        fuso_br = pytz.timezone('America/Sao_Paulo') # SP timezone
        today = datetime.now(fuso_br).strftime('%Y-%m-%d') # today's date
        local_path = os.path.join(RAW_DATA_PATH, file_name) # local path
        
        cloud_destination = f"raw/cnpj/ingestion_date={today}/{file_name}" # cloud path
        blob = BUCKET.blob(cloud_destination)
        blob.upload_from_filename(local_path)
        print(f'file {file_name} successfully uploaded to {cloud_destination}')

    except Exception as e:
        print(f"Error uploading file: {e}")


# -------------------------- SILVER DATA FUNCTIONS --------------------------
def process_raw_to_dataframes(path_name: str) -> dict:
    all_data_frames = {}

    fuso_br = pytz.timezone('America/Sao_Paulo') # SP timezone
    today = datetime.now(fuso_br).replace(microsecond=0) # today's date

    alias_map = {k: v['alias'] for k, v in FULL_METADATA_MAP.items()}
    type_map = {v['alias']: v['type'] for k, v in FULL_METADATA_MAP.items()}

    for file in os.listdir(path_name):
        if file.endswith('.json'):
            full_path = os.path.join(path_name, file)

            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.json_normalize(data)

                # Using auxiliary function defined above
                df_qsa = expand_and_rename(df, 'qsa', RENAME_QSA)
                df_cnae = expand_and_rename(df, 'cnaes_secundarios', RENAME_CNAE)
                df_regime_trib = expand_and_rename(df, 'regime_tributario', RENAME_REGIME)

                df_final = pd.concat([df, df_qsa, df_cnae, df_regime_trib], axis=1)

                df_final = df_final.rename(columns=alias_map) #renane using alias map

                for col, target_type in type_map.items(): # change type using type map
                    if col in df_final.columns:
                        if target_type == 'str':
                            df_final[col] = df_final[col].fillna('').astype(target_type)
                        else:
                            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0).astype(target_type)
                
                df_final = df_final.drop(columns=['qsa', 'cnaes_secundarios', 'regime_tributario'], errors='ignore')
                df_final['DTEXTREF'] = pd.to_datetime(today)

                all_data_frames[file] = df_final
    return all_data_frames
    

def save_to_silver( dfs_dict : dict) -> None:

    fuso_br = pytz.timezone('America/Sao_Paulo') #timezone of Brazil
    today = datetime.now(fuso_br).strftime('%Y-%m-%d') #today's date

    for file_name, df in dfs_dict.items():
        cnpj_prefix = file_name.split('_')[0]
        file_path = os.path.join(SILVER_DATA_PATH, f"{cnpj_prefix}_{today}.parquet")

        try:
            df.to_parquet(file_path)
            print(f"File saved successfully at: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")


def data_injection_silver(file_name: str) -> None: 

    fuso_br = pytz.timezone('America/Sao_Paulo') # SP timezone
    today = datetime.now(fuso_br).strftime('%Y-%m-%d') # today's date
    file_path = os.path.join(SILVER_DATA_PATH, file_name) # local path
    
    cloud_destination = f"silver/cnpj/ingestion_date={today}/{file_name}" # cloud path
    blob = BUCKET.blob(cloud_destination)
    blob.upload_from_filename(file_path)
    print(f'file {file_name} successfully uploaded to {cloud_destination}')


# -------------------------- LOAD SILVER TO BIGQUERY --------------------------
def load_silver_to_bigquery() -> None:

    fuso_br = pytz.timezone('America/Sao_Paulo') #timezone of Brazil
    today = datetime.now(fuso_br).strftime('%Y-%m-%d') #today's date

    DATASET_ID = 'credit_guard_dataset_pipeline'
    TABLE_ID = f"{CLIENT_BQ.project}.{DATASET_ID}.credit_guard_cnpj_silver"

    try:
        if DATASET_ID not in [dataset.dataset_id for dataset in CLIENT_BQ.list_datasets()]:
            CLIENT_BQ.create_dataset(DATASET_ID, exists_ok=True)
    except Exception as e:
        print(f"Error creating dataset: {e}")


    job_config = bigquery.LoadJobConfig(
        source_format = bigquery.SourceFormat.PARQUET,
        write_disposition = 'WRITE_APPEND', #append new data to the table (more viable in big data scenarios)
        autodetect = True,
    )

    try:
        source_uri = f"gs://credit-guard-raw-sa-east1/silver/cnpj/ingestion_date={today}/*.parquet"
        print(f"Iniciating data charging {source_uri}...")
    except Exception as e:
        print(f"Error charging data: {e}")

    load_job = CLIENT_BQ.load_table_from_uri(
        source_uri,
        TABLE_ID,
        job_config=job_config
    )

    load_job.result()
    print(f"Charging ended successfully! Table {TABLE_ID} updated.")

    # --- Additional logs with error handler for parcial errors ---
    if load_job.errors:
        print("⚠️  Warning: Some rows failed to load:")
        for error in load_job.errors:
            print(f" - {error['message']}")
    else:
        print("✅ No errors reported during the load job.")

    destination_table = CLIENT_BQ.get_table(TABLE_ID)  # Faz uma chamada rápida para ler os metadados da tabela

    print(f"--- Job Summary ---")
    print(f"Job ID: {load_job.job_id}")
    print(f"Status: {load_job.state}")
    print(f"Rows loaded: {destination_table.num_rows}") # Total lines after updated
    print(f"Total size: {destination_table.num_bytes / 1024**2:.2f} MB")
    print(f"Table {TABLE_ID} updated successfully!")
        

# -------------------------- GITHUB API FUNCTIONS --------------------------
#github api call
def get_github_workflow():
    owner = 'ANIBEserra'
    repo = 'Portifolio' 
    workflow_id = '231418862'
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

    url_runs = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?per_page=1"
    
    try:
        # Get the last run ID
        response = requests.get(url_runs, headers=headers)
        if response.status_code == 200:
            run_data = response.json()
            run_id = run_data['workflow_runs'][0]['id']

        # Job Details
        url_jobs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
        response = requests.get(url_jobs, headers=headers)
        if response.status_code == 200:
            jobs_data = response.json()
            file_path = os.path.join(GITHUB_DATA_PATH, f"github_workflow_run.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(jobs_data, f, indent=4, ensure_ascii=False)
            return jobs_data

    except Exception as e:
        print(f"Error: {e}")


# ----------------------- CLEAN LOCAL TEMPORARY FILES -----------------------
def clean_local_temp_files():

    folders = [RAW_DATA_PATH, SILVER_DATA_PATH]
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting file: {file_path} - Error: {e}")

    print(f"✅ Local temporary files cleaned successfully.")


# -------------------------- ORCHESTRATION ---------------------------------

if __name__ == "__main__":
    # 1. raw data ingestion (saving to local)
    df_input = pd.read_csv(INPUT_PATH, dtype={'CNPJ': str})

    for cnpj in df_input['CNPJ']:
        buscar_cnpj(cnpj)
        sleep(2.5)

    # 2. raw data ingestion (saving to cloud)
    local_files = os.listdir(RAW_DATA_PATH)
    for file in local_files:
        if file.endswith('.json'):
            data_injection_raw(file)
        else:
            pass

    # 3. silver processing (transformations and saving to local)
    try:
        processed_dfs = process_raw_to_dataframes(RAW_DATA_PATH)
        save_to_silver(processed_dfs)
    except Exception as e:
        print(f"Error processing raw data to silver: {e}")

    # 4. silver data ingestion (saving to cloud)
    local_files = os.listdir(SILVER_DATA_PATH)
    for file in local_files:
        if file.endswith('.parquet'):
            data_injection_silver(file)
        else:
            pass

    # 5. silver data ingestion (saving to bigquery)
    load_silver_to_bigquery()

    # 6. github api call (saving to local)
    get_github_workflow()

    # 7. clean local temporary files
    clean_local_temp_files()

    print("ETL PIPELINE COMPLETED SUCCESSFULLY!")