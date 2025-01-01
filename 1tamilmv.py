from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import requests
import os
import subprocess

Username = "herobenhero2@gmail.com"
Password = "JBD7!xN@oTSkrhKd7Pch"
chat_id = '-1002068315295'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

CHAT_ID = '-1002068315295'
THUMBNAIL_PATH = 'Thumbnail.jpg'

def get_magnetic_urls(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
    return [link['href'] for link in magnetic_links]

Site = "https://www.1tamilmv.legal/"

sites_filename = "1tamilmv_index.txt"

response = requests.get(Site)
soup = BeautifulSoup(response.text, 'html.parser')
links = [link['href'] for link in soup.find_all('a', href=lambda x: x and x.startswith(Site + 'index.php?/forums/topic/'))]

def get_last_part(url):
    return url.split('/')[-1]

# Fetch the sites file using rclone
subprocess.run(["rclone", "copy", f"College:Shared/Telegram/{sites_filename}", "."])

try:
    with open(sites_filename, "r") as file:
        existing_sites = set(file.read().splitlines())
except FileNotFoundError:
    existing_sites = set()

delete_all(seedr)

with open(sites_filename, "a") as sites_file:
    for site in sorted(links):
        last_part = get_last_part(site)
        if last_part in existing_sites:
            continue
        print("Working on", site)
        magnets = get_magnetic_urls(site)
        for magnet in reversed(magnets):
            id, urls = seedr_download(magnet, seedr)
            for filepath, encoded_url in urls.items():
                aria2_download(filepath, encoded_url)
                upload_video(chat_id, filepath, THUMBNAIL_PATH)
                os.remove(filepath)
            seedr.deleteFolder(id)
        sites_file.write(last_part + "\n")
        sites_file.flush()
        existing_sites.add(last_part)
        # Sync the updated sites file using rclone
        subprocess.run(["rclone", "sync", f"{sites_filename}", "College:Shared/Telegram/"])
