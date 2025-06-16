import os
import subprocess
import math
from seedrcc import Login,Seedr
from time import sleep
import urllib.parse
from urllib.parse import unquote
import requests

# User Inputs
TELEGRAM_TOKEN = '5942550686:AAFbd7hUu9HMN80D2Y2rNP7aj4FMCyZvAhk'  # Important secret in caps
API_HASH = 'e18a786351fb201760b000217ff60500'  # Important secret in caps
API_ID = '10437406'
API_SERVER_URL = 'http://localhost:8081/bot'

def get_video_duration(file_path):
    try:
        cmd_duration = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
        output_duration = subprocess.check_output(cmd_duration, shell=True).decode('utf-8').strip()
        return int(float(output_duration))
    except:
        return 0

def generate_thumbnail(file_path):
    thumbnail_path = 'Sample.jpg'
    cmd_thumbnail = f'ffmpeg -i "{file_path}" -ss 00:00:01 -vframes 1 "{thumbnail_path}"'
    subprocess.call(cmd_thumbnail, shell=True)
    return thumbnail_path

def upload_video(CHAT_ID, file_path, thumbnail_path=None):

    duration = get_video_duration(file_path)
    if not thumbnail_path:
        thumbnail_path = generate_thumbnail(file_path)
    caption = os.path.basename(file_path)

    if not check_bot_status():
        return

    print("Uploading Video...")
    while True:
        try:
            with open(file_path, 'rb') as video, open(thumbnail_path, 'rb') as thumb:
                files = {'video': video, 'thumb': thumb}
                data = {'chat_id': CHAT_ID, 'duration': duration, 'caption': caption}
                response = requests.post(f"{API_SERVER_URL}{TELEGRAM_TOKEN}/sendVideo", files=files, data=data)
                response_data = response.json()
                if response_data['ok']:
                    print(f'Video {file_path} sent successfully!')
                    break
                else:
                    print(response_data)
                    print(f'Failed to send video {file_path}. Retrying in 30 seconds...')
                    sleep(30)
        except:
            continue

def convert_size(size_bytes):
    """Convert the size in bytes to a more human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def delete_all(seedr):
    table=seedr.listContents()
    if len(table['torrents']) != 0:
        for torrent in table['torrents']:
            seedr.deleteTorrent(torrent['id'])
    if len(table['folders']) != 0:
        for folder in table['folders']:
            seedr.deleteFolder(folder['id'])

def seedr_download(MagneticURL,seedr):
    add=seedr.addTorrent(MagneticURL)
    folder={}
    folder['id']=0
    file_urls={}
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
            if i==30:
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
                          if file['size'] < 2000000000:
                              link=seedr.fetchFile(file['folder_file_id'])
                              # print('\t',link["url"])
                              quoted_link = urllib.parse.unquote(link["url"])
                              encoded_url = urllib.parse.quote(quoted_link, safe=':/?&=()[]')
                              # print(encoded_url)
                              print(file['name'],encoded_url)
                              file_urls[file['name']] = encoded_url
                          else:
                            print(f"File size {convert_size(file['size'])} is Greater than 2GB")
    return folder['id'],file_urls

def aria2_download(filename, link):
    print(f"Downloading {filename} with {link}")

    command = f"aria2c -o '{filename}' -c -s 2 -x 2 -k 1M -j 1 '{link}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"Download error: {stderr.decode('utf-8')}")
        return 0
    
    print(f"Download completed for {filename}")
    return filename

def check_bot_status():
    url = f"{API_SERVER_URL}{TELEGRAM_TOKEN}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Bot is Working")
            return True
        else:
            os.system(f"nohup ./telegram-bot-api --api-hash {API_HASH} --api-id {API_ID} --local &")
            sleep(3)
            response = requests.get(url)
            if response.status_code == 200:
                print("Bot started successfully")
                return True
            else:
                raise Exception('Failed to start the bot.')
    except Exception as e:
        print(e)
        os.system(f"nohup ./telegram-bot-api --api-hash {API_HASH} --api-id {API_ID} --local &")
        sleep(3)
        response = requests.get(url)
        if response.status_code == 200:
            print("Bot started successfully")
            return True
        else:
            raise Exception('Failed to start the bot.')
        return False
