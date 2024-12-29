from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import requests
import os
import subprocess

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
filename = "magnet_links_1337x.txt"

def scrape_links(site_url):
    response = requests.get(site_url+'/popular-movies')
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=lambda x: x and x.startswith('/torrent/') and x.endswith('/'))
    return links

existing_magnet_links = set()

for mirror_site in get_mirrors():
    links = scrape_links(mirror_site)
    if links:
        break

delete_all(seedr)

if not links:
    print("No links found on any mirror site. Exiting.")
else:
    subprocess.run(["rclone", "copy", f"College:Shared/Telegram/{filename}", "."])

    try:
        with open(filename, "r") as file:
            existing_magnet_links = set(file.read().splitlines())
    except FileNotFoundError:
        pass

    try:
        with open(filename, "a") as file:
            for link in links:
                magnets = get_magnetic_urls(mirror_site + link['href'])
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
                        existing_magnet_links.add(magnet)
                        subprocess.run(["rclone", "sync", f"{filename}", "College:Shared/Telegram/"])
    except Exception as e:
        print(e)
