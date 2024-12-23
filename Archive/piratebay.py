from bs4 import BeautifulSoup
from extensions import seedr_download
from time import time
from seedrcc import Login,Seedr
import requests

Username  = "herobenhero3@gmail.com" #@param {type:"string"}
Password  = "NfrYj7JL@vID&amp;iznJL^VN" #@param {type:"string"}
chat_id = '-1001826079620'

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


filename = "magnet_links_piratebay.txt"

alternative_sites = [
    'https://thepiratebay7.com',
    'https://thepiratebay0.org',
    'https://thepiratebay10.org',
    'https://pirateproxy.live',
    'https://thehiddenbay.com',
    'https://piratebay.live',
    'https://thepiratebay.zone',
    'https://tpb.party',
    'https://thepiratebay.party',
    'https://piratebay.party',
    'https://piratebayproxy.live',
    'https://pirateproxylive.org',
    'https://thepiratebay1.com',
    'https://thepiratebay1.live',
    'https://thepiratebays.info',
    'https://thepiratebays.live',
    'https://thepiratebay1.top',
    'https://thepiratebay1.info',
    'https://thepiratebay.rocks',
    'https://thepiratebay.vet'
]

for Site in alternative_sites:
    if get_magnetic_urls(Site+'/browse/207'):
        break
        
# Load existing magnet links from the file
try:
    with open(filename, "r") as file:
        existing_magnet_links = set(file.read().splitlines())
except FileNotFoundError:
    existing_magnet_links = set()

delete_all()

try:
    # Open the file in append mode to add new magnet links
    with open(filename, "a") as file:
        start_time = time()
        for i in range(35,1,-1):
            URL = f"{Site}/browse/207/{i}/3"
            print(URL)            
            magnets = get_magnetic_urls(URL)
            print(magnets)
            for magnet in magnets:
                if magnet not in existing_magnet_links:
                    # Write new magnet links to the file
                    seedr_download(magnet,seedr,chat_id)
                    file.write(magnet + "\n")
                    existing_magnet_links.add(magnet)
    
            # elapsed_time = time() - start_time
            # if elapsed_time > 0.8 * 60 * 60:  # 5 hours in seconds
            #     print("Stopping script after 2.5 hours.")
            #     break
              
except Exception as e:
    print("Error Occured :",e)
