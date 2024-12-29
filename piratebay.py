from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from time import time
from seedrcc import Login, Seedr
import requests
import os
import subprocess

Username = "herobenhero3@gmail.com"
Password = "NfrYj7JL@vID&amp;iznJL^VN"
chat_id = '-1001826079620'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

THUMBNAIL_PATH = 'Thumbnail.jpg'

def get_magnetic_urls(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
    return [link['href'] for link in magnetic_links]

filename = "magnet_links_piratebay.txt"

alternative_sites = [
    'https://thepiratebay7.com',
    'https://thepiratebay0.org',
    'https://thepiratebay10.org',
    'https://pirateproxy.live',
    'https://thehiddenbay.com',
    'https://piratebay.live',
    'https://thepiratebay.zone',
    'https://tpb.party',
    'https://thepiratebay.party',
    'https://piratebay.party',
    'https://piratebayproxy.live',
    'https://pirateproxylive.org',
    'https://thepiratebay1.com',
    'https://thepiratebay1.live',
    'https://thepiratebays.info',
    'https://thepiratebays.live',
    'https://thepiratebay1.top',
    'https://thepiratebay1.info',
    'https://thepiratebay.rocks',
    'https://thepiratebay.vet'
]

for Site in alternative_sites:
    if get_magnetic_urls(Site+'/browse/207'):
        break

subprocess.run(["rclone", "copy", f"College:Shared/Telegram/{filename}", "."])

try:
    with open(filename, "r") as file:
        existing_magnet_links = set(file.read().splitlines())
except FileNotFoundError:
    existing_magnet_links = set()

delete_all(seedr)

try:
    with open(filename, "a") as file:
        for i in range(35, 1, -1):
            URL = f"{Site}/browse/207/{i}/3"
            magnets = get_magnetic_urls(URL)
            for magnet in magnets:
                if magnet not in existing_magnet_links:
                    id, urls = seedr_download(magnet, seedr)
                    for filepath, encoded_url in urls.items():
                        aria2_download(filepath, encoded_url)
                        upload_video(chat_id, filepath, THUMBNAIL_PATH)
                        os.remove(filepath)  # Delete file after uploading
                    seedr.deleteFolder(id)
                    file.write(magnet + "\n")
                    file.flush()
                    subprocess.run(["rclone", "sync", f"{filename}", "College:Shared/Telegram/"])
except Exception as e:
    print("Error Occurred:", e)
