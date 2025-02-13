from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import requests
import os
import subprocess
import time
import sys
import threading

def run_script(script_name):
    subprocess.run(["python", script_name])

if len(sys.argv) > 1:
    start_time = time.time()
    max_duration = int(sys.argv[1]) * 60  # Convert minutes to seconds
    # Start background threads
    scripts = ["1337xdaily.py", "eztvdaily.py", "piratebay.py", "ytsdaily.py"]
    threads = []
    for script in scripts:
        thread = threading.Thread(target=run_script, args=(script,))
        thread.start()
        threads.append(thread)

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

Site = "https://www.1tamilmv.bike/"

def check_site_exists(last_part):
    response = requests.get(f"https://db.herobenhero.workers.dev/SELECT COUNT(*) as count FROM tele_tamilmv WHERE \"index\" = '{last_part}'")
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'results' in data:
            return data['results'][0]['count'] > 0
    return False

def add_site(last_part):
    requests.post(f"https://db.herobenhero.workers.dev/INSERT INTO tele_tamilmv ('index') VALUES ('{last_part}')")

# Your existing code for fetching links
response = requests.get(Site)
soup = BeautifulSoup(response.text, 'html.parser')
links = [link['href'] for link in soup.find_all('a', href=lambda x: x and x.startswith(Site + 'index.php?/forums/topic/'))]

def get_last_part(url):
    # Extract the last part of the URL
    raw_last_part = url.split('/')[-1]
    
    # Split by '-' and take the first part
    first_part = raw_last_part.split('-')[0]
    
    # Append '-0' to the first part
    return f"{first_part}-0"

delete_all(seedr)

for site in sorted(links):
    last_part = get_last_part(site)
    if check_site_exists(last_part):
        continue
    print("Working on", site)
    magnets = get_magnetic_urls(site)
    for magnet in reversed(magnets):
        id, urls = seedr_download(magnet, seedr)
        for filepath, encoded_url in urls.items():
            if aria2_download(filepath, encoded_url):
                upload_video(chat_id, filepath, THUMBNAIL_PATH)
                os.remove(filepath)
        seedr.deleteFolder(id)
    add_site(last_part)
    
    if len(sys.argv) > 1:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_duration:
            print("Maximum duration exceeded, terminating script.")
            break
