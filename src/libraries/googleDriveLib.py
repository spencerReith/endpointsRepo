import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = 'photosapi-438001-003e9239a438.json'  # Update with your path
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service

def upload_file(file_path):
    service = authenticate()
    folder_id = '1jyldlg-MiPoOaYYg6zPZ79Rm99xoX1GT'

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')  # Adjust MIME type if needed
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID:', file.get('id'))
    return file.get('id')


def find_file_by_name(file_name):
    service = authenticate()
    query = f"name='{file_name}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print(f"No files found with the name: {file_name}")
        return None
    else:
        file_id = items[0]['id']
        file_url = f"https://drive.google.com/uc?id={file_id}"
        return file_id, file_url



# if __name__ == '__main__':
#     file_path = '4302.jpeg'  # Update with your file path
#     upload_file(file_path)
