#@markdown **Seedr Magnetic URL to Direct Link Telegram**

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import MessageHandler, Filters
from bs4 import BeautifulSoup
import urllib.parse
from seedrcc import Login, Seedr
import math
from time import sleep

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Seedr account
Username = "herotesthero2@gmail.com"  # Add your Seedr username
Password = "NKOqLps^t(22BEI9IZv#6"  # Add your Seedr password
account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

# Function to convert size
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def seedr_download(MagneticURL, chat_id, bot):
    delete_all()
    add = seedr.addTorrent(MagneticURL)
    if add["result"] == True:
        table = seedr.listContents()
        i = 0
        last_progress = -1
        while len(table['torrents']) != 0 and i < 30:
            for torrent in table['torrents']:
                size = convert_size(torrent['size'])
                message = f"{torrent['id']}: {torrent['name']}, {size}, {torrent['progress']}%"
                send_message_to_chat(bot, chat_id, message)
                if last_progress != torrent['progress']:
                    
                    i = 0
                    last_progress = torrent['progress']
            table = seedr.listContents()
            sleep(1)
            i += 1
            if i == 30:
                seedr.deleteTorrent(torrent['id'])
                break

        if len(table['folders']) != 0:
            message = "Completed torrents:"
            send_message_to_chat(bot, chat_id, message)
            for folder in table['folders']:
                message = f"\n{folder['id']}: {folder['name']}, {convert_size(folder['size'])}"
                send_message_to_chat(bot, chat_id, message)
                table = seedr.listContents(folder['id'])
                if len(table['files']) == 0:
                    message = "No files in this folder."
                    send_message_to_chat(bot, chat_id, message)
                else:
                    message = "\tFiles:"
                    send_message_to_chat(bot, chat_id, message)
                    for file in table['files']:
                        message = f"\t{file['folder_file_id']}: {file['name']}, {convert_size(file['size'])}, Video={file['play_video']}"
                        send_message_to_chat(bot, chat_id, message)
                        if file['play_video'] == True:
                            if file['size'] / (1024**3) < 1.98:
                                link = seedr.fetchFile(file['folder_file_id'])
                                quoted_link = urllib.parse.unquote(link["url"])
                                encoded_url = urllib.parse.quote(quoted_link, safe=':/?&=()[]')
                                message = f"Encoded URL: {encoded_url}"
                                send_message_to_chat(bot, chat_id, message)
                            else:
                                message = f"File size {convert_size(file['size'])} is Greater than 2GB"
                                send_message_to_chat(bot, chat_id, message)
                seedr.deleteFolder(folder['id'])
    else:
        send_message_to_chat(bot, chat_id, "Error adding torrent to Seedr.")

def delete_all():
    #@title **List All**
    table = seedr.listContents()
    if len(table['torrents']) != 0:
        for torrent in table['torrents']:
            seedr.deleteTorrent(torrent['id'])
    if len(table['folders']) != 0:
        for folder in table['folders']:
            seedr.deleteFolder(folder['id'])

# Command handler for /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send a /magnet command with a URL to process in Seedr.')

# Function to send messages to the chat
def send_message_to_chat(bot, chat_id, message):
    try:
        bot.send_message(chat_id, message)
    except Exception as e:
        print(f"Error sending message to chat: {e}")

# Command handler for /magnet command
def magnet(update: Update, context: CallbackContext) -> None:
    # Extract the URL from the /magnet command
    magnet_url = context.args[0] if context.args else None
    chat_id = update.message.chat_id

    if magnet_url:
        update.message.reply_text(f"Processing magnet URL in Seedr...")
        seedr_download(magnet_url, chat_id, context.bot)
    else:
        update.message.reply_text("Please provide a valid magnet URL after /magnet.")

# Command handler for unknown commands
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, I didn't understand that command.")

# Main function to start the bot
def main():
    # Add your Telegram bot token
    updater = Updater("5942550686:AAEkBVyp0U0zhP3z7ylmw4m2KS-pTD9UyZQ", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("magnet", magnet))

    # Register unknown command handler
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
