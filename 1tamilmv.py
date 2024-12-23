from bs4 import BeautifulSoup
from extensions import delete_all,seedr_download,aria2_download,upload_video
from seedrcc import Login,Seedr
import requests

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

filename = "magnet_links.txt"  # @param {type:"string"}
sites_filename = "1tamilmv_index.txt"  # New file to store site URLs

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

# Load existing site URLs from the sites file
try:
    with open(sites_filename, "r") as file:
        existing_sites = set(file.read().splitlines())
except FileNotFoundError:
    existing_sites = set()

# Open the files to write the magnet link and site URL, and close them immediately after writing
with open(filename, "a") as magnet_file, open(sites_filename, "a") as sites_file:
    for site in sorted(links):
        # Skip the site if it is already in the existing sites set
        if site in existing_sites:
            continue
        print("Working on", site)
        magnets = get_magnetic_urls(site)
        for magnet in reversed(magnets):  # You might want to sort this if needed
            if magnet not in existing_magnet_links:
                id, urls = seedr_download(magnet, seedr)
                for filepath, encoded_url in urls.items():
                    aria2_download(filepath, encoded_url)
                    upload_video(chat_id, filepath, THUMBNAIL_PATH)
                seedr.deleteFolder(id)
                magnet_file.write(magnet + "\n")
                magnet_file.flush()  # Ensure data is written immediately

                existing_magnet_links.add(magnet)

        # Write the site URL to the sites file
        sites_file.write(site + "\n")
        sites_file.flush()  # Ensure data is written immediately
        existing_sites.add(site)  # Add the site to the set of existing sites
