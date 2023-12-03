from bs4 import BeautifulSoup
from time import sleep,time
import subprocess
import os
import random
import subprocess
from telegram import Bot, InputMediaVideo
from telegram.ext import Updater
import math
from seedrcc import Login,Seedr
from time import sleep
import urllib.parse
from urllib.parse import unquote
import requests

Username  = "herotesthero1@gmail.com" #@param {type:"string"}
Password  = "t&amp;hFsoVFkjoOyw13" #@param {type:"string"}

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

API_SERVER_URL = 'http://localhost:8081/bot'
TELEGRAM_TOKEN = '5942550686:AAEkBVyp0U0zhP3z7ylmw4m2KS-pTD9UyZQ'
chat_id = '-1002068315295' #@param {type:"string"}

def convert_size(size_bytes):
    """Convert the size in bytes to a more human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_video_duration(file_path):
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    return int(float(output))

def generate_thumbnail(video_path, time, thumbnail_path):
    cmd = f'ffmpeg -i "{video_path}" -ss {time} -vframes 1 "{thumbnail_path}"'
    subprocess.call(cmd, shell=True)

def send_video_file(file_path, thumbnail_path):
    print(f"Sending {file_path} to Telegram")

    time = '00:00:01'
    # generate_thumbnail(file_path, time, thumbnail_path)

    if not os.path.exists(file_path):
        print(f'File {file_path} not found.')
        return

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, base_url=API_SERVER_URL)
    bot = updater.bot

    duration = get_video_duration(file_path)

    with open(file_path, 'rb') as file, open('Thumbnail.jpg', 'rb') as thumb:
        bot.send_video(chat_id=chat_id, video=file, duration=duration, thumb=thumb, timeout=999, caption=file_path)

    print(f'Video {file_path} sent successfully!')
    os.remove(file_path)

def aria2_download(filename, link):
    print(f"Downloading {filename} with {link}")

    command = f"aria2c -o '{filename}' --summary-interval=1 --max-connection-per-server=2 '{link}'"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    send_video_file(filename, filename +'.jpg')

def seedr_download(MagneticURL):
  add=seedr.addTorrent(MagneticURL)
  if add["result"]==True:
    table=seedr.listContents()
    i = 0
    last_progress = -1
    while len(table['torrents']) != 0 and i < 30:
        for torrent in table['torrents']:
            size = convert_size(torrent['size'])
            print(f"{torrent['id']}: {torrent['name']}, {size}, {torrent['progress']}%")
            if last_progress != torrent['progress']:
                i = 0
                last_progress = torrent['progress']
        table = seedr.listContents()
        sleep(1)
        i += 1
        if i==15:
          seedr.deleteTorrent(torrent['id'])
          break

    if len(table['folders']) != 0:
        print("Completed torrents:")
        for folder in table['folders']:
            print()
            size = convert_size(folder['size'])
            print(f"{folder['id']}: {folder['name']}, {size}")
            table=seedr.listContents(folder['id'])
            # seedr.deleteFolder(folder['id'])
            if len(table['files']) == 0:
                print("No files in this folder.")
            else:
                print("\tFiles:")
                for file in table['files']:
                    print(f"\t{file['folder_file_id']}: {file['name']}, {convert_size(file['size'])}, Video={file['play_video']}")
                    if file['play_video']==True:
                      if file['size'] / (1024**3) < 2:
                          link=seedr.fetchFile(file['folder_file_id'])
                          # print('\t',link["url"])
                          quoted_link = urllib.parse.unquote(link["url"])
                          encoded_url = urllib.parse.quote(quoted_link, safe=':/?&=()[]')
                          # print(encoded_url)
                          aria2_download(file['name'],encoded_url)
                      else:
                        print(f"File size {convert_size(file['size'])} is Greater than 2GB")
                      seedr.deleteFolder(folder['id'])

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

def delete_all():
    #@title **List All**
    table=seedr.listContents()
    if len(table['torrents']) != 0:
        for torrent in table['torrents']:
            seedr.deleteTorrent(torrent['id'])
    if len(table['folders']) != 0:
        for folder in table['folders']:
            seedr.deleteFolder(folder['id'])

import requests
from bs4 import BeautifulSoup

Site = "https://www.1tamilmv.phd/"  # @param {type:"string"}
filename = "magnet_links.txt"

# Load existing magnet links from the file
try:
    with open(filename, "r") as file:
        existing_magnet_links = set(file.read().splitlines())
except FileNotFoundError:
    existing_magnet_links = set()

# Send an HTTP request to the web server
response = requests.get(Site)

# Parse the HTML code of the web page
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links on the page that start with https://www.1tamilmv.autos/index.php?/forums/topic/
links = soup.find_all('a', href=lambda x: x and x.startswith(Site+'index.php?/forums/topic/') and x.endswith('-0'))

# subprocess.Popen('git config user.name "GitHub Actions"', shell=True, stdout=subprocess.PIPE)
# subprocess.Popen('git config user.email "actions@github.com"', shell=True, stdout=subprocess.PIPE)
delete_all()
# Open the file in append mode to add new magnet links
with open(filename, "a") as file:
    # start_time = time()
    for link in reversed(links):
        magnets = get_magnetic_urls(link['href'])
        for magnet in magnets:
            if magnet not in existing_magnet_links:
                # Write new magnet links to the file
                # seedr_download(magnet)
                file.write(magnet + "\n")
                existing_magnet_links.add(magnet)

        git_add_process = subprocess.Popen("sh git.sh", shell=True, stdout=subprocess.PIPE)
        git_add_process.wait()
        break
        
        # git_add_process = subprocess.Popen("git add magnet_links.txt", shell=True, stdout=subprocess.PIPE)
        # git_add_process.wait()

        # git_commit_process = subprocess.Popen('git commit -m "Updated"', shell=True, stdout=subprocess.PIPE)
        # git_commit_process.wait()

        # elapsed_time = time() - start_time
        # if elapsed_time > 0.5 * 60 * 60:  # 5 hours in seconds
        #     print("Stopping script after 2.5 hours.")
        #     break
