import sys
import requests
from bs4 import BeautifulSoup

print("Argomenti totali:", len(sys.argv))
print("Nome dello script:", sys.argv[0])
print("Argomenti:", sys.argv[1:])

def get_volume_count(opera_url):
    response=requests.get(opera_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return len(soup.find_all("div",class_="volume-element"))

if len(sys.argv)==2:
    print("L'opera ha ",get_volume_count(sys.argv[1])," volumi")
