# GoogleDriveDownloader

A simple utility to download a Google Drive directory to a local folder. Note that you will need to authorize an application with access to the Google Drive using the Google Cloud Platform. Once you have the credentials, you can save them as credentials/credentials.json. 

Limitations: 
1. Cannot handle nested folders. 
2. Cannot download Google-specific files (ex. Google Docs)
An error will be thrown in either case. 