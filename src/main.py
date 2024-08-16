import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Cargar credenciales desde config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Configuración de Airtable
API_KEY = config['AIRTABLE_API_KEY']
BASE_ID = config['AIRTABLE_BASE_ID']
TABLE_ID = config['AIRTABLE_TABLE_ID']

# Configuración de Google Sheets y Drive
SHEET_ID = config['GOOGLE_SHEET_ID']
CREDENTIALS_FILE = config['GOOGLE_CREDENTIALS_FILE']

# Alcance (scope) de Google Sheets y Drive
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Autenticación y acceso a Google Sheets y Drive
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(creds)

# Acceder a Google Sheet
sheet = client.open_by_key(SHEET_ID).sheet1

# Obtener todas las filas de datos desde la hoja
rows = sheet.get_all_values()

# Recorrer las filas comenzando desde la segunda fila (suponiendo que la primera es encabezado)
for i, row in enumerate(rows[1:], start=2):  # enumerate comienza en 2 para coincidir con los números de fila en Google Sheets
    date_time, gmail_account, subject, tweet_url, tweet_text, attachment_url, processed = row
    
    # Omitir si la fila ya ha sido procesada
    if processed.lower() == "yes":
        continue
    
    # Extraer el handle desde el URL del tweet
    handle = tweet_url.split('/')[3]
    name = handle
    
    # Convertir el URL de Google Drive a un URL de descarga
    file_id = attachment_url.split("id=")[-1]
    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    # Mostrar la información del tweet
    print(f"Del usuario llamado: {name}")
    print(f"Y cuya cuenta es: https://x.com/{handle}")
    print(f"Texto del tuit: {tweet_text}")
    print(f"URL del attachment: {direct_url}")
    
    # Datos que se enviarán a Airtable
    data = {
        "fields": {
            "Name": name,
            "Handle": f"https://x.com/{handle}",
            "Tweet Text": tweet_text,
            "URL": tweet_url,
            "Attachment": [{"url": direct_url}]
        }
    }
    
    # Endpoint de la API de Airtable
    endpoint_url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    
    # Headers HTTP para el request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enviar la entrada a Airtable
    response = requests.post(endpoint_url, json=data, headers=headers)
    
    # Confirmar la respuesta y marcar la fila como procesada
    if response.status_code == 200:
        print("Nueva entrada en Airtable, mi carnal!")
        sheet.update_cell(i, 7, "Yes")  # "Procesado" (Columna G en GSheets)
    else:
        print(f"Algo salió mal, idiota: {response.status_code}")
        print(response.json())

