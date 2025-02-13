import requests
from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import os
import time
import sys

# Your existing setup code here
Username = "herobenhero2@gmail.com"
Password = "JBD7!xN@oTSkrhKd7Pch"
chat_id = '-1002068315295'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

CHAT_ID = '-1002068315295'
THUMBNAIL_PATH = 'Thumbnail.jpg'
Site = "https://www.1tamilmv.bike/"

def get_magnetic_urls(URL):
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
    return [link['href'] for link in magnetic_links]

def get_largest_index():
    response = requests.get("https://db.herobenhero.workers.dev/SELECT `index` FROM tele_tamilmv ORDER BY `index` DESC LIMIT 5")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'results' in data:
            largest_index = max(int(result['index'].split('-')[0]) for result in data['results'])
            return largest_index
    return 0

def check_index_exists(index):
    response = requests.get(f"https://db.herobenhero.workers.dev/SELECT COUNT(*) as count FROM tele_tamilmv WHERE \"index\" = '{index}'")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'results' in data:
            return data['results'][0]['count'] > 0
    return False

def add_index(index):
    requests.post(f"https://db.herobenhero.workers.dev/INSERT INTO tele_tamilmv ('index') VALUES ('{index}')")

def get_index_from_url(url):
    # Extract the index from the URL
    raw_last_part = url.split('/')[6]
    return int(raw_last_part.split('-')[0])

def main():
    start_time = time.time()
    max_duration = int(sys.argv[1]) * 60 if len(sys.argv) > 1 else float('inf')

    largest_known_index = get_largest_index()
    print(f"Largest known index: {largest_known_index}")

    delete_all(seedr)

    response = requests.get(Site)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link['href'] for link in soup.find_all('a', href=lambda x: x and x.startswith(Site + 'index.php?/forums/topic/'))]

    for site in sorted(links, reverse=True):
        current_index = get_index_from_url(site)
        
        if current_index <= largest_known_index:
            # print(f"Reached known index: {current_index}. Stopping.")
            continue

        if check_index_exists(f"{current_index}-0"):
            print(f"Index {current_index} already processed. Skipping.")
            continue

        print(f"Processing new index: {current_index}")
        magnets = get_magnetic_urls(site)
        for magnet in reversed(magnets):
            id, urls = seedr_download(magnet, seedr)
            for filepath, encoded_url in urls.items():
                if aria2_download(filepath, encoded_url):
                    upload_video(chat_id, filepath, THUMBNAIL_PATH)
                    os.remove(filepath)
            seedr.deleteFolder(id)
        
        add_index(f"{current_index}-0")

        if time.time() - start_time > max_duration:
            print("Maximum duration exceeded, terminating script.")
            break

if __name__ == "__main__":
    main()
