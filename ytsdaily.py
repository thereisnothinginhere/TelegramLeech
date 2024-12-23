from bs4 import BeautifulSoup
from extensions import delete_all,seedr_download,aria2_download,upload_video
from time import time
from seedrcc import Login,Seedr
import requests

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
filename = "magnet_links_yts.txt"

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
links = soup.find_all('a', href=lambda x: x and x.startswith(Site+'movies/'))
links = {link.get('href') for link in links if link.get('href') is not None}

# subprocess.Popen('git config user.name "GitHub Actions"', shell=True, stdout=subprocess.PIPE)
# subprocess.Popen('git config user.email "actions@github.com"', shell=True, stdout=subprocess.PIPE)
try:
    # Open the file in append mode to add new magnet links
    with open(filename, "a") as file:
        start_time = time()
        for link in links:
            magnets = get_magnetic_urls(link)
            for magnet in magnets:
                if magnet not in existing_magnet_links:
                    id, urls = seedr_download(magnet, seedr)
                    for filepath, encoded_url in urls.items():
                        aria2_download(filepath, encoded_url)
                        upload_video(chat_id, filepath, THUMBNAIL_PATH)
                    seedr.deleteFolder(id)
                    file.write(magnet + "\n")
                    file.flush()  # Ensure data is written immediately
    
            # git_add_process = subprocess.Popen("sh git.sh", shell=True, stdout=subprocess.PIPE)
            # git_add_process.wait()
            # break
            
            # git_add_process = subprocess.Popen("git add magnet_links.txt", shell=True, stdout=subprocess.PIPE)
            # git_add_process.wait()
    
            # git_commit_process = subprocess.Popen('git commit -m "Updated"', shell=True, stdout=subprocess.PIPE)
            # git_commit_process.wait()
    
            # elapsed_time = time() - start_time
            # if elapsed_time > 0.2 * 60 * 60:  # 5 hours in seconds
            #     print("Stopping script after 2.5 hours.")
            #     break
except Exception as e:
    print("Error Occured :",e)
