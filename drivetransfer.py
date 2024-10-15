from __future__ import print_function

import io
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        # Get the source folder ID
        source_folder_id = 'your_source_folder_id'  # Replace with your source folder ID
        destination_folder_id = 'your_destination_folder_id'  # Replace with your destination folder ID

        # List files in the source folder
        results = service.files().list(
            q=f"'{source_folder_id}' in parents",
            fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found in the source folder.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                download_file(service, item['id'], item['name'])
                upload_file(service, item['name'], destination_folder_id)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def download_file(service, file_id, filename):
    """Downloads a file from Google Drive.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to download.
        filename: Name to save the file as.
    """
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')

    with open(filename, 'wb') as f:
        f.write(fh.getvalue())


def upload_file(service, filename, folder_id):
    """Uploads a file to Google Drive.

    Args:
        service: Drive API service instance.
        filename: Name of the file to upload.
        folder_id: ID of the folder to upload to.
    """
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filename,
                            mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print(F'File ID: {file.get("id")}')


if __name__ == '__main__':
    main()
