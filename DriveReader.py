import io
import os
import pickle

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



class DriveReader: 
    ## Static Variables
    _SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


    def __init__(self):
        """
        Initialize the class and creates the service for interacting with Google Drive
        """

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = "credentials/token.pickle"
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try: 
                    flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", self._SCOPES)
                except FileNotFoundError as e: 
                    raise FileNotFoundError("You probably need to generate a credentials file for the application.", e)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

        self._service = build("drive", "v3", credentials=creds)        



    def GetDriveFolderId(self, folder_name: str):
        """
        folder_name: The name of the drive folder.

        Returns: The Id for that Drive folder with folder_name.
        """
        page_token = None
        folders = []

        ## Search for all objects with the given name
        while True:
            response = self._service.files().list(q="name = '" + folder_name + "'",
                                                  spaces="drive",
                                                  fields="nextPageToken, files(id, name, mimeType)",
                                                  pageToken=page_token).execute()
            for file in response.get("files", []):
                folders.append((file.get("name"), file.get("id"), file.get("mimeType")))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        ## Get a list of entries that are actually folders
        to_be_returned = []
        for a in folders:
            if a[2] == "application/vnd.google-apps.folder": 
                to_be_returned.append(a)
        if len(to_be_returned) > 1: 
            raise Exception("Multiple folders found.")
        elif len(to_be_returned) == 0:
            raise Exception("No folders found.")

        return to_be_returned[0][1]



    def ListFilesInDriveFolder(self, parent_id: str):
        """
        parent_id: The id of the parent directory/folder. 

        Returns: A dictionary: file name -> file id
        """

        all_files = []

        page_token = None
        while True:
            ## Query the API to get the next set of files
            response = self._service.files().list(q="'" + str(parent_id) + "' in parents",
                                                  spaces="drive",
                                                  fields="nextPageToken, files(id, name)",
                                                  pageToken=page_token).execute()

            ## Add the files in this page to the list
            for file in response.get("files", []):
                all_files.append((file.get("name"), file.get("id")))
            
            ## No token -> No more files
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        ## Convert the list of files to a dictionary
        to_be_returned = {}
        for f in all_files:
            name = f[0]
            id = f[1]
            to_be_returned[name] = id
        return to_be_returned



    def DownloadFile(self, file_id: str, write_path: str):
        """
        file_id: The id of the file. 
        write_path: Where the file will be saved.

        Returns: N/A.
        """
        fh = io.BytesIO()

        request = self._service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        with open(write_path, "wb") as f:
            f.write(fh.getbuffer())
