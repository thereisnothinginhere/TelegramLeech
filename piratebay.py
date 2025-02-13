from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from time import time
from seedrcc import Login, Seedr
import requests
import os
import re

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

def extract_btih(magnet):
    match = re.search(r'btih:([a-fA-F0-9]{40})', magnet)
    return match.group(1).lower() if match else None

def check_btih_exists(btih):
    response = requests.get(f"https://db.herobenhero.workers.dev/SELECT COUNT(*) AS count FROM magnets WHERE \"hash\" = '{btih}';")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'results' in data:
            return data['results'][0]['count'] > 0
    return False

def add_btih(btih):
    requests.post(f"https://db.herobenhero.workers.dev/INSERT INTO magnets ('hash') VALUES ('{btih}')")

delete_all(seedr)

try:
    for i in range(35, 1, -1):
        URL = f"{Site}/browse/207/{i}/3"
        magnets = get_magnetic_urls(URL)
        for magnet in magnets:
            btih = extract_btih(magnet)
            if btih and not check_btih_exists(btih):
                id, urls = seedr_download(magnet, seedr)
                for filepath, encoded_url in urls.items():
                    if aria2_download(filepath, encoded_url):
                        upload_video(chat_id, filepath, THUMBNAIL_PATH)
                        os.remove(filepath)  # Delete file after uploading
                seedr.deleteFolder(id)
                add_btih(btih)
except Exception as e:
    print("Error Occurred:", e)
