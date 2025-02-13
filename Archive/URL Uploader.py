# telegram_bot.py
import os
from time import sleep
import requests
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

TELEGRAM_TOKEN = '5942550686:AAEkBVyp0U0zhP3z7ylmw4m2KS-pTD9UyZQ'
API_SERVER_URL = 'http://localhost:8081/bot'

def download_with_aria2(url, output_path, update, context, message_id):
    command = ["aria2c", url, "-o", output_path, "--summary-interval=1"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
    last_message_id = message_id  # Variable to store the message ID of the last sent message

    while True:
        # sleep(1)
        output = process.stdout.readline()
        # print(output)
        if "File already exists" in output:
            context.bot.edit_message_text(
                  chat_id=update.message.chat_id,
                  message_id=last_message_id,
                  text='File Already Exists'
              )
            break
        if process.poll() is not None:
            try:
              context.bot.edit_message_text(
                  chat_id=update.message.chat_id,
                  message_id=last_message_id,
                  text='Download Is Successful'
              )
            except:
              update.message.reply_text('Download Is Successful')
            break

        if output and '[#' in output:
            status = output.strip().split(" ")

            # Extracting information using string manipulation
            downloading_size = status[1].split('/')[0]
            total_size = status[1].split('/')[1].split('(')[0]
            cn = status[2].split(':')[1]
            dl = status[3].split(':')[1]

            # Constructing the reply text with extracted information
            reply_text = (
                f"File Name: {output_path}\n"
                f"Downloading Size: {downloading_size}\n"
                f"Total Size: {total_size}\n"
                f"CN: {cn}\n"
                f"DL: {dl}"
            )

            if len(status) == 5:
                eta = status[4].split(':')[1][:-1]
                reply_text += f"\nETA: {eta}"

            # Edit the last sent message if available, otherwise send a new one
            if last_message_id:
                try:
                    context.bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=last_message_id,
                        text=reply_text
                    )
                except Exception as e:
                    continue
            else:
                message = update.message.reply_text(reply_text)
                last_message_id = message.message_id
    return True

def start(update, context):
    update.message.reply_text('Hello! I am your custom bot.')


def send_document(file_name,update, context, message_id):
    context.bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=message_id,
                        text="Sending File"
                    )

    # Get the current working directory
    current_folder = os.getcwd()

    # Construct the file path
    file_path = os.path.join(current_folder, file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        update.message.reply_text(f'File {file_name} not found.')
        return

    # Send the document
    context.bot.send_document(chat_id=update.message.chat_id, document=open(file_path, 'rb'), filename=file_name)
    context.bot.edit_message_text(
                        chat_id=update.message.chat_id,
                        message_id=message_id,
                        text="File sent successfully!"
                    )

def upload(update, context):
    # Check if the user provided a link
    if len(context.args) == 0:
        update.message.reply_text('Please provide a link and an optional file name after the /upload command.')
        return

    link = context.args[0]

    # Check if the user provided a custom file name
    if len(context.args) > 1:
        file_name = context.args[1]
    else:
        file_name = link.split("/")[-1]

    message = update.message.reply_text(f"Filename: {file_name}\nLink: {link}")

    # Download the file from the provided link
    if download_with_aria2(link, file_name, update, context, message.message_id):
        # Call the send_document function
        send_document(file_name, update, context, message.message_id)
    else:
        update.message.reply_text('Failed to download the file.')

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, base_url=API_SERVER_URL)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("upload", upload))

    # Add error handler
    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()

def error_handler(update, context):
    """Log the error and send a message to the user."""
    print(f'Update "{update}" caused error "{context.error}"')
    # update.message.reply_text(f'An error occurred. Please try again later. Update caused error {context.error}')


if __name__ == '__main__':
    main()