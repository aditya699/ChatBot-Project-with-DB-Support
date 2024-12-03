'''
Author -Aditya Bhatt 20:15 PM 03-12-2024

NOTE : This will delete the logs folder and other unimportant stuff(will run this daily)
'''

import shutil
import os

# List of folders to delete
folders = ['logs', '__pycache__']

for folder in folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"{folder} folder deleted successfully")
    else:
        print(f"{folder} folder not found")