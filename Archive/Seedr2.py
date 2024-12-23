import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import math
from seedrcc import Login, Seedr
from time import sleep
import urllib.parse

# ... (previous code remains unchanged)

import math
!pip install seedrcc
from seedrcc import Login,Seedr
from google.colab import output
from time import sleep
import urllib.parse
from urllib.parse import unquote
!apt install aria2
output.clear()

def convert_size(size_bytes):
    """Convert the size in bytes to a more human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

import requests

# def download_file(file_folder_id):
#     url = f'https://www.seedr.cc/download/file/{file_folder_id}/url'

#     cookies_string = '_pk_id.2.5294=85c0c8cdd84d4aab.1694282520.; _pk_ses.2.5294=1; RSESS_session=3b2db629bd7ebe42a3f4f3c87c88a6dd07b09346; RSESS_remember=8cffffc18edaaab0b8c83f8e1c71a8ba410a47ee' #@param {type:"string"}

#     response = requests.get(url, cookies=cookies_string_to_dict(cookies_string))

#     if response.status_code == 200:
#         download_data = response.json()
#         download_url = download_data["url"]
#         name = download_data["name"]
#         print(name)
#         print(download_url)
#         return name,download_url
#     return

# def cookies_string_to_dict(cookies_string):
#     cookies_dict = {}
#     for item in cookies_string.split(';'):
#         key, value = item.strip().split('=', 1)
#         cookies_dict[key] = value
#     return cookies_dict

#@title **Login**
Username  = "herotesthero2@gmail.com" #@param {type:"string"}
Password  = "NKOqLps^t(22BEI9IZv#6" #@param {type:"string"}

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)


# Define the seedr_download function
def seedr_download(update: Update, context: CallbackContext, MagneticURL: str) -> None:
    add = seedr.addTorrent(MagneticURL)
    if add["result"] == True:
        table = seedr.listContents()
        i = 0
        last_progress = -1
        message = None  # Store the message to be updated

        while len(table['torrents']) != 0 and i < 30:
            torrents_info = []
            for torrent in table['torrents']:
                size = convert_size(torrent['size'])
                torrents_info.append(f"{torrent['id']}: {torrent['name']}, {size}, {torrent['progress']}%")

                if last_progress != torrent['progress']:
                    i = 0
                    last_progress = torrent['progress']

            # Create a message to display the torrent information
            message_text = "\n".join(torrents_info)
            if message is None:
                message = context.bot.send_message(update.effective_chat.id, message_text)
            else:
                context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=message_text)

            table = seedr.listContents()
            sleep(1)
            i += 1

            if i == 30:
                seedr.deleteTorrent(torrent['id'])
                break

        if len(table['folders']) != 0:
            completed_torrents_info = ["Completed torrents:"]
            for folder in table['folders']:
                size = convert_size(folder['size'])
                completed_torrents_info.append(f"{folder['id']}: {folder['name']}, {size}")

                table = seedr.listContents(folder['id'])
                if len(table['files']) != 0:
                    files_info = ["\tFiles:"]
                    for file in table['files']:
                        files_info.append(f"\t{file['folder_file_id']}: {file['name']}, {convert_size(file['size'])}, Video={file['play_video']}")
                        if file['play_video'] == True and file['size'] / (1024 ** 3) < 1.98:
                            link = seedr.fetchFile(file['folder_file_id'])
                            quoted_link = urllib.parse.unquote(link["url"])
                            encoded_url = urllib.parse.quote(quoted_link, safe=':/?&=()[]')
                            files_info.append(encoded_url)

                    completed_torrents_info.extend(files_info)

            # Create a message to display the completed torrents information
            message_text = "\n".join(completed_torrents_info)
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=message_text)

            for folder in table['folders']:
                seedr.deleteFolder(folder['id'])

# ... (rest of the script remains unchanged)


# Define the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! I am your Seedr Bot. Send me a magnetic URL using /magnet command.')

# Define the magnet command
def magnet(update: Update, context: CallbackContext) -> None:
    # Get the magnetic URL from the user input
    magnet_url = context.args[0]

    # Call your Seedr function here
    name, encoded_url = seedr_download(magnet_url)

    # Update the message with Seedr download information
    update.message.reply_text(f"File Name: {name}\nEncoded URL: {encoded_url}")

# Initialize the bot and add the command handlers
def main() -> None:
    # Set your Telegram Bot Token here
    token = 'YOUR_TELEGRAM_BOT_TOKEN'
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register the command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("magnet", magnet, pass_args=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
