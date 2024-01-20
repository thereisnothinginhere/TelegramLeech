from bs4 import BeautifulSoup
from extensions import aria2_download
from time import time
import requests

chat_id = '-1002068315295'

filename = "masstamilan_links.txt"

# Load existing magnet links from the file
try:
    with open(filename, "r") as file:
        existing_magnet_links = set(file.read().splitlines())
except FileNotFoundError:
    existing_magnet_links = set()

#@markdown **MassTamilan Index Scrapper**
from bs4 import BeautifulSoup
import requests

# Make a request to the website
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}

url='https://masstamilan.dev' #@param {type:"string"}

response = requests.get(url, headers=headers)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the div with class 'gw'
div = soup.find('div', class_='gw')

# Find all 'a' tags within the 'div'
a_tags = div.find_all('a')

links=[]
# Extract and print out all 'href' attributes from the 'a' tags
for a in a_tags:
    links.append(url+a.get('href'))

# subprocess.Popen('git config user.name "GitHub Actions"', shell=True, stdout=subprocess.PIPE)
# subprocess.Popen('git config user.email "actions@github.com"', shell=True, stdout=subprocess.PIPE)
try:
    # Open the file in append mode to add new magnet links
    with open(filename, "a") as file:
        start_time = time()
        for link in links:
            # Split the URL by the '/' character
            site = '/'.join(link.rsplit('/', 2)[:2])

            response = requests.get(link, headers=headers)

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with class 'gw'
            div = soup.find('table', class_='firstleft')

            # Find all 'a' tags within the 'div'
            a_tags = div.find_all('a')

            # Extract and print out the text and 'href' attributes from the 'a' tags
            for a in a_tags:

                # Get the text of the 'a' tag
                text = a.get_text()
                # Get the 'href' attribute of the 'a' tag
                href = a.get('href')

                if text:
                    if '/downloader/' in href:
                        # Print the text and the full URL
                        # print('\n'+filename+' '+text.split(' ')[0]+".mp3")
                        # # print('\n'+filename+' '+text+".mp3")
                        # print(text, site+href)

                        aria2_download(filename+' '+text.split(' ')[0]+".mp3", site+href, chat_id)
                    else:
                        # print('\n'+text)
                        filename=text

            existing_magnet_links.add(link)
    
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
