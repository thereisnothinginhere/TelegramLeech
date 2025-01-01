from bs4 import BeautifulSoup
from extensions import delete_all, seedr_download, aria2_download, upload_video
from seedrcc import Login, Seedr
import requests
import os
import subprocess

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

Site = "https://www.1tamilmv.legal/"

sites_filename = "1tamilmv_index.txt"

response = requests.get(Site)
soup = BeautifulSoup(response.text, 'html.parser')
links = [link['href'] for link in soup.find_all('a', href=lambda x: x and x.startswith(Site + 'index.php?/forums/topic/'))]

def get_last_part(url):
    return url.split('/')[-1]

# Fetch the sites file using rclone
subprocess.run(["rclone", "copy", f"College:Shared/Telegram/{sites_filename}", "."])

try:
    with open(sites_filename, "r") as file:
        existing_sites = set(file.read().splitlines())
except FileNotFoundError:
    existing_sites = set()

delete_all(seedr)

with open(sites_filename, "a") as sites_file:
    for site in sorted(links):
        last_part = get_last_part(site)
        if last_part in existing_sites:
            continue
        print("Working on", site)
        magnets = get_magnetic_urls(site)
        for magnet in reversed(magnets):
            id, urls = seedr_download(magnet, seedr)
            for filepath, encoded_url in urls.items():
                aria2_download(filepath, encoded_url)
                upload_video(chat_id, c, THUMBNAIL_PATH)
                os.remove(name: Build Telegram API Server for Windows
on:
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    permissions:
      contents: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install Chocolatey
      run: Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    - name: Install Visual Studio Build Tools
      run: choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --includeOptional"

    - name: Install Dependencies
      run: choco install -y git cmake

    - name: Clone Repositories and Install Vcpkg
      run: |
        git clone --recursive https://github.com/tdlib/telegram-bot-api.git
        cd telegram-bot-api
        git clone https://github.com/Microsoft/vcpkg.git
        cd vcpkg
        ./bootstrap-vcpkg.bat

    - name: Install x64 Dependencies
      run: |
        cd D:/a/windowsbotserver/telegram-bot-api/vcpkg
        ./vcpkg.exe install gperf:x64-windows openssl:x64-windows zlib:x64-windows

    - name: Build x64 Version
      run: |
        cd D:/a/windowsbotserver/telegram-bot-api
        Remove-Item build -Force -Recurse -ErrorAction SilentlyContinue
        mkdir build
        cd build
        cmake -A x64 -DCMAKE_INSTALL_PREFIX:PATH=.. -DCMAKE_TOOLCHAIN_FILE:FILEPATH=../vcpkg/scripts/buildsystems/vcpkg.cmake ..
        cmake --build . --target install --config Release
        mkdir -p ../Windows-x64
        Copy-Item ../bin/* ../Windows-x64/ -Recurse

    - name: Install x86 Dependencies
      run: |
        cd D:/a/windowsbotserver/telegram-bot-api/vcpkg
        ./vcpkg.exe install gperf:x86-windows openssl:x86-windows zlib:x86-windows

    - name: Build x86 Version
      run: |
        cd D:/a/windowsbotserver/telegram-bot-api
        Remove-Item build -Force -Recurse -ErrorAction SilentlyContinue
        mkdir build
        cd build
        cmake -A Win32 -DCMAKE_INSTALL_PREFIX:PATH=.. -DCMAKE_TOOLCHAIN_FILE:FILEPATH=../vcpkg/scripts/buildsystems/vcpkg.cmake ..
        cmake --build . --target install --config Release
        mkdir -p ../Windows-x32
        Copy-Item ../bin/* ../Windows-x32/ -Recurse

    - name: Commit and Push
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add telegram-bot-api/Windows-x64/* telegram-bot-api/Windows-x32/*
        git commit -m "Updated Windows binaries for x64 and x32"
        git push
)
            seedr.deleteFolder(id)
        sites_file.write(last_part + "\n")
        sites_file.flush()
        existing_sites.add(last_part)
        # Sync the updated sites file using rclone
        subprocess.run(["rclone", "sync", f"{sites_filename}", "College:Shared/Telegram/"])
