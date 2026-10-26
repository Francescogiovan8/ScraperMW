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

def get_chapter_url_list(opera_url,volume_number):
    if(get_volume_count(opera_url)<volume_number or volume_number<1):
        print("ATTEZIONE! L'opera è formata da", get_volume_count(opera_url), "volumi!")
        return []
    response=requests.get(opera_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    volume=soup.find_all("div",class_="volume-element")[get_volume_count(opera_url)-volume_number]
    chapters = volume.find_all("div", class_="chapter")
    chapters_link = [
        chapter.find("a", class_="chap")["href"]
        for chapter in chapters
    ]
    chapters_link.reverse()
    return chapters_link

def get_chapter_number(opera_url,volume_number):
    if(get_volume_count(opera_url)<volume_number):
        print("ATTEZIONE! L'opera è formata solo da", get_volume_count(opera_url), "volumi!")
        return []
    response=requests.get(opera_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    volume=soup.find_all("div",class_="volume-element")[get_volume_count(opera_url)-volume_number]
    chapters = volume.find_all("div", class_="chapter")
    return len(chapters)

def get_chapter_page_numer(chapter_link):
    response=requests.get(chapter_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    select=soup.find("select",class_="page")
    options=select.find_all("option")
    return len(options)


if len(sys.argv)==2:
    print("L'opera ha ",get_volume_count(sys.argv[1])," volumi")
elif len(sys.argv)==3:
    print(get_chapter_number(sys.argv[1],int(sys.argv[2])))
    chapters_link=get_chapter_url_list(sys.argv[1],int(sys.argv[2]))
    print(get_chapter_page_numer(chapters_link[0]))
