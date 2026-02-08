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

load_dotenv()

# config base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# config key path (now points to root directory)
KEY_PATH = os.path.join(BASE_DIR, 'key-google.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

# config data paths
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'input', 'cnpjs.csv')
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_DATA_PATH, exist_ok=True)
GITHUB_DATA_PATH = os.path.join(BASE_DIR, 'data', 'github')
os.makedirs(GITHUB_DATA_PATH, exist_ok=True)

CLIENT = storage.Client()
BUCKET = CLIENT.bucket('credit-guard-raw-sa-east1')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def buscar_cnpj(cnpj):
    cnpj= re.sub(r'\D', '', str(cnpj))
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    
    try:
        response = requests.get(url)
        if response.status_code==200:
            data = response.json()
            # Define timezone of São Paulo
            fuso_br = pytz.timezone('America/Sao_Paulo')
            today = datetime.now(fuso_br).strftime('%Y-%m-%d')
            file_path = os.path.join(RAW_DATA_PATH, f"{cnpj}_{today}.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
                print(f"File saved successfully at: {file_path}")
        else:
            print(f"{response.status_code} for cnpj {cnpj}")
    except Exception as e:
        print(f"Connection failed {e}")


def data_injection(file_name):

    #local path 
    fuso_br = pytz.timezone('America/Sao_Paulo')
    today = datetime.now(fuso_br).strftime('%Y-%m-%d')
    local_path = os.path.join(RAW_DATA_PATH, file_name)
    
    #cloud path
    cloud_destination = f"raw/cnpj/ingestion_date={today}/{file_name}"

    # Uploading
    blob = BUCKET.blob(cloud_destination)
    blob.upload_from_filename(local_path)

    print(f'file {file_name} successfully uploaded')

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


df_input = pd.read_csv(INPUT_PATH, dtype={'CNPJ': str})
for cnpj in df_input['CNPJ']:
    buscar_cnpj(cnpj)
    sleep(2.5)

local_files = os.listdir(RAW_DATA_PATH)
for file in local_files:
    if file.endswith('.json'):
        data_injection(file)
    else:
        pass

get_github_workflow()

