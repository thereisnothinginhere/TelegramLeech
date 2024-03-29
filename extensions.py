from time import sleep
import subprocess
import os
from telegram.ext import Updater
import math
import urllib.parse
from telegram.error import RetryAfter

API_SERVER_URL = 'http://localhost:8081/bot'
TELEGRAM_TOKEN = '5942550686:AAEkBVyp0U0zhP3z7ylmw4m2KS-pTD9UyZQ'

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

def send_video_file(file_path, thumbnail_path, chat_id):
    print(f"Sending {file_path} to Telegram")

    time = '00:00:01'
    # generate_thumbnail(file_path, time, thumbnail_path)

    if not os.path.exists(file_path):
        print(f'File {file_path} not found.')
        return

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, base_url=API_SERVER_URL)
    bot = updater.bot

    duration = get_video_duration(file_path)
    thumbnail_path='Thumbnail.jpg'

    retries = 5  # Adjust the number of retries based on your needs
    for attempt in range(retries):
        try:
            with open(file_path, 'rb') as file, open(thumbnail_path, 'rb') as thumb:
                bot.send_video(chat_id=chat_id, video=file, duration=duration, thumb=thumb, timeout=999, caption=file_path)
            print(f'Video {file_path} sent successfully!')
            os.remove(file_path)
            break  # Exit the loop if successful
        except RetryAfter as e:
            sleep_time = e.retry_after  # Get the required wait time from the exception
            print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds and retrying.")
            sleep(sleep_time * 2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"Error sending video: {e}")
            sleep(60)
            # break  # Exit the loop on other errors

def get_audio_duration(file_path):
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    return int(float(output))

def send_audio_file(file_path,chat_id):
    if not os.path.exists(file_path):
        print(f'File {file_path} not found.')
        return

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, base_url=API_SERVER_URL)
    bot = updater.bot

    duration = get_audio_duration(file_path)

    with open(file_path, 'rb') as file:
        bot.send_audio(chat_ibotd=chat_id, audio=file, duration=duration, timeout=999)

    print(f'Audio {file_path} sent successfully!')

def aria2_download(filename, link, chat_id):
    print(f"Downloading {filename} with {link}")

    command = f"aria2c -o '{filename}' --summary-interval=1 --max-connection-per-server=2 '{link}'"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    if ".mp3" in filename:
        send_audio_file(filename,chat_id)
    else:
        send_video_file(filename, filename +'.jpg', chat_id)

def delete_all(seedr):
    #@title **List All**
    table=seedr.listContents()
    if len(table['torrents']) != 0:
        for torrent in table['torrents']:
            seedr.deleteTorrent(torrent['id'])
    if len(table['folders']) != 0:
        for folder in table['folders']:
            seedr.deleteFolder(folder['id'])

def seedr_download(MagneticURL,seedr, chat_id):
  delete_all(seedr)
  add=seedr.addTorrent(MagneticURL)
#   print(add)
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
                      if file['size'] / (1024**3) < 1.95:
                          link=seedr.fetchFile(file['folder_file_id'])
                          # print('\t',link["url"])
                          quoted_link = urllib.parse.unquote(link["url"])
                          encoded_url = urllib.parse.quote(quoted_link, safe=':/?&=()[]')
                          # print(encoded_url)
                          aria2_download(file['name'],encoded_url, chat_id)
                      else:
                        print(f"File size {convert_size(file['size'])} is Greater than 2GB")
            seedr.deleteFolder(folder['id'])