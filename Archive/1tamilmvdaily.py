from bs4 import BeautifulSoup
from extensions import seedr_download
from time import time
from seedrcc import Login,Seedr
import requests

Username  = "herobenhero2@gmail.com" #@param {type:"string"}
Password  = "JBD7!xN@oTSkrhKd7Pch" #@param {type:"string"}
chat_id = '-1002050020170'

account = Login(Username, Password)
account.authorize()
seedr = Seedr(token=account.token)

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


Site = "https://www.1tamilmv.world/index.php?/forums/forum/11-web-hd-itunes-hd-bluray/"  # @param {type:"string"}
filename = "magnet_links_hd_tamil.txt"

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
links = {link.get('href') for link in links if link.get('href') is not None and 'omment' not in link['href']}

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
                    # Write new magnet links to the file
                    seedr_download(magnet,seedr,chat_id)
                    file.write(magnet + "\n")
                    existing_magnet_links.add(magnet)
    
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
