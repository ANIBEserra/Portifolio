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

# config base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# config key path (now points to root directory)
KEY_PATH = os.path.join(BASE_DIR, 'key-google.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH

# config data paths
INPUT_PATH = os.path.join(BASE_DIR, 'data', 'input', 'cnpjs.csv')
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_DATA_PATH, exist_ok=True)

CLIENT = storage.Client()
BUCKET = CLIENT.bucket('credit-guard-raw-sa-east1')

def buscar_cnpj(cnpj):
    cnpj= re.sub(r'\D', '', str(cnpj))
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    
    try:
        response = requests.get(url)
        if response.status_code==200:
            data = response.json()
            # Define o fuso horário de São Paulo
            fuso_br = pytz.timezone('America/Sao_Paulo')
            today = datetime.now(fuso_br).strftime('%Y-%m-%d')
            file_path = os.path.join(RAW_DATA_PATH, f"{cnpj}_{today}.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
                print(f"Arquivo salvo com sucesso em: {file_path}")
        else:
            print(f"{response.status_code} para o cnpj {cnpj}")
    except Exception as e:
        print(f"Falha na conexão {e}")


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