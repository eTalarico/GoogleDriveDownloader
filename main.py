import os 
import sys

from DriveReader import DriveReader



## Console inputs
## 1st argument: python file path 
## 2rd argument: 1: download, 0: only print summary
## 3nd argument: output directory
## 4th argument: Google Drive folder name

## Parse input to determine if the files actually be downloaded?
if len(sys.argv) >= 2: 
    if sys.argv[1] == "1":
        execute_download = True
    elif sys.argv[1] == "0":
        execute_download = False
    else: 
        raise ValueError("Second argument must be '1' or '0'.")
else: 
    raise ValueError("Must specify whether to download or print summary.")

## Parse input to determine the download directory
if len(sys.argv) >= 3:
    target_dir = sys.argv[2]
else: 
    raise ValueError("Must specify directory for downloading files.")

## Parse input to determine the Google Drive folder
if len(sys.argv) >= 4:
    drive_folder_name = sys.argv[3]
else:
    raise ValueError("Must specify a Google Drive folder.")

## Create the directory if it doesn't exist
try: 
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
except Exception as e:
    raise ValueError("Invalid input path.", e)



## Get all the files in the Drive
dr = DriveReader()
folder_id = dr.GetDriveFolderId(drive_folder_name)
files_in_drive = dr.ListFilesInDriveFolder(folder_id)

## Get all the files already in the directory
extant_files = os.listdir(target_dir)

## Summary of difference between what's been downloaded and what hasn't
not_downloaded = set(files_in_drive.keys()).difference(set(extant_files))
not_in_drive = set(extant_files).difference(set(files_in_drive.keys()))
print(str(len(not_downloaded)) + " file(s) not yet downloaded.")
print(str(len(not_in_drive)) + " file(s) not found in Drive folder.")
print()
if len(not_in_drive) > 0:
    print("Files not in drive: ")
    for f in not_in_drive:
        print("-- " + f)
    print()



## Download everything that isn't already in the directory
## Or just print the summary
if execute_download: 
    print("Downloading Songs:")
    for song_name in not_downloaded:
        song_id = files_in_drive[song_name]
        dr.DownloadFile(song_id, target_dir + "/" + song_name)
        print("-- " + song_name)
    print("Finished downloading file(s)!")
else: 
    print("Finished producing summary!")
