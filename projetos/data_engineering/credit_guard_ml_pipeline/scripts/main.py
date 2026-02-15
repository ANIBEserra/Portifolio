import requests
import json
import os
import pandas as pd
from time import sleep
import re
from google.cloud import storage
from datetime import datetime
from pathlib import Path
import pytz
from dotenv import load_dotenv
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from configs.mapping import (
    RENAME_QSA, RENAME_CNAE, RENAME_REGIME, FULL_METADATA_MAP,
    RAW_DATA_PATH, SILVER_DATA_PATH
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

os.makedirs(RAW_DATA_PATH, exist_ok=True)
os.makedirs(GITHUB_DATA_PATH, exist_ok=True)
os.makedirs(SILVER_DATA_PATH, exist_ok=True)

CLIENT = storage.Client()
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


def data_injection(file_name):

    fuso_br = pytz.timezone('America/Sao_Paulo') # SP timezone
    today = datetime.now(fuso_br).strftime('%Y-%m-%d') # today's date
    local_path = os.path.join(RAW_DATA_PATH, file_name) # local path
    
    cloud_destination = f"raw/cnpj/ingestion_date={today}/{file_name}" # cloud path
    blob = BUCKET.blob(cloud_destination)
    blob.upload_from_filename(local_path)
    print(f'file {file_name} successfully uploaded to {cloud_destination}')


# -------------------------- SILVER DATA FUNCTIONS --------------------------
def process_raw_to_dataframes(path_name: str) -> dict:
    all_data_frames = {}

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
                df_final = df_final.rename(columns=FULL_METADATA_MAP)
                df_final = df_final.drop(columns=['qsa', 'cnaes_secundarios', 'regime_tributario'], errors='ignore')

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


# -------------------------- ORCHESTRATION --------------------------

if __name__ == "__main__":
    # raw data ingestion (saving to local)
    df_input = pd.read_csv(INPUT_PATH, dtype={'CNPJ': str})
    for cnpj in df_input['CNPJ']:
        buscar_cnpj(cnpj)
        sleep(2.5)

    # raw data ingestion (saving to cloud)
    local_files = os.listdir(RAW_DATA_PATH)
    for file in local_files:
        if file.endswith('.json'):
            data_injection(file)
        else:
        pass

    # silver processing (transformations and saving to local)
    processed_dfs = process_raw_to_dataframes(RAW_DATA_PATH)
    save_to_silver(processed_dfs)

    print("RAW -> SILVER pipeline completed successfully!")

    # github api call (saving to local)
    get_github_workflow()