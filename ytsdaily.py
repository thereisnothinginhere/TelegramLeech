from bs4 import BeautifulSoup
from extensions import delete_all,seedr_download,aria2_download,upload_video
from time import time
from seedrcc import Login,Seedr
import requests
import re
import os

Username  = "herobenhero6@gmail.com" #@param {type:"string"}
Password  = "WD4.8tTrZhbimB!" #@param {type:"string"}
chat_id = '-1002018178635'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

THUMBNAIL_PATH = 'Thumbnail.jpg' #@param {type:"string"}

def get_magnetic_urls(URL):
  # Send an HTTP request to the web server
  response = requests.get(URL)

  # Parse the HTML code of the web page
  soup = BeautifulSoup(response.text, 'html.parser')

  # Find all the <a> elements on the page that have a "magnet" href attribute
  magnetic_links = soup.find_all('a', href=lambda x: x and x.startswith('magnet:'))
  magnets=[]
  # Print the text of each magnetic link
  for link in magnetic_links:
    magnets.append(link['href'])
  return magnets


Site = "https://yts.mx/"  # @param {type:"string"}

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

# Send an HTTP request to the web server
response = requests.get(Site)

# Parse the HTML code of the web page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links on the page that start with the specified Site URL and 'movies/'
links = soup.find_all('a', href=lambda x: x and x.startswith(Site+'movies/'))
links = {link.get('href') for link in links if link.get('href') is not None}

try:
    for link in links:
        magnets = get_magnetic_urls(link)
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
