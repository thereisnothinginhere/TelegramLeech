from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import requests
import os
import re

Username = "herobenhero5@gmail.com"
Password = "zyHyuTfaGiC6:uP"
chat_id = '-1002080818562'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

THUMBNAIL_PATH = 'Thumbnail.jpg'

def get_magnetic_urls(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
    return [link['href'] for link in magnetic_links]

def get_mirrors():
    return [
        "https://www.1337x.st",
        "https://1377x.to",
        "https://www.13377x.tw/"
    ]

Site = "https://1337x.to"

def scrape_links(site_url):
    response = requests.get(site_url+'/popular-movies')
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=lambda x: x and x.startswith('/torrent/') and x.endswith('/'))
    return links

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

for mirror_site in get_mirrors():
    links = scrape_links(mirror_site)
    if links:
        break

delete_all(seedr)

if not links:
    print("No links found on any mirror site. Exiting.")
else:
    try:
        for link in links:
            magnets = get_magnetic_urls(mirror_site + link['href'])
            for magnet in set(magnets):
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
        print(e)
