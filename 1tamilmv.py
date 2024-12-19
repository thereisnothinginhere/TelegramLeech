from bs4 import BeautifulSoup
from extensions import delete_all,seedr_download,aria2_download,upload_video
from time import time
from seedrcc import Login,Seedr
import requests
import subprocess
import os

Username  = "herobenhero2@gmail.com" #@param {type:"string"}
Password  = "JBD7!xN@oTSkrhKd7Pch" #@param {type:"string"}

chat_id = '-1002068315295'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

CHAT_ID = '-1002068315295' #@param {type:"string"}
THUMBNAIL_PATH = 'Thumbnail.jpg' #@param {type:"string"}

def get_magnetic_urls(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
    magnets = [link['href'] for link in magnetic_links]
    return magnets


Site = "https://www.1tamilmv.ac/"  # @param {type:"string"}

delete_all(seedr)

filename = "magnet_links.txt"

# Initial sync to fetch existing magnet links
command = f"rclone sync College:/Shared/Telegram/{filename} ./"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
process.communicate()  # Wait for initial sync to complete

# Fetching links
response = requests.get(Site)
soup = BeautifulSoup(response.text, 'html.parser')
links = [link['href'] for link in soup.find_all('a', href=lambda x: x and x.startswith(Site + 'index.php?/forums/topic/'))]

# Load existing magnet links from the file
try:
    with open(filename, "r") as file:
        existing_magnet_links = set(file.read().splitlines())
except FileNotFoundError:
    existing_magnet_links = set()

for site in sorted(links):
    magnets = get_magnetic_urls(site)
    for magnet in reversed(magnets):  # You might want to sort this if needed
        if magnet not in existing_magnet_links:
            id, urls = seedr_download(magnet, seedr)
            for filepath, encoded_url in urls.items():
                aria2_download(filepath, encoded_url)
                upload_video(chat_id, filepath, THUMBNAIL_PATH)
            seedr.deleteFolder(id)

            # Write new magnet to the file
            with open(filename, "a") as file:
                file.write(magnet + "\n")
                file.flush()

            # Sync the updated file
            command = f"rclone sync ./{filename} College:/Shared/Telegram/{filename}"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.communicate()  # Wait for sync to complete

            existing_magnet_links.add(magnet)
