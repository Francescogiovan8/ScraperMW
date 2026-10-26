import os
import sys
import requests
from bs4 import BeautifulSoup
from PIL import Image
import shutil


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

def get_chapter_url_img_list(chapter_link, chapter_num_page):
    img_url_list=[]
    for x in range(chapter_num_page):
        actual_url=chapter_link+"/"+str(x+1)
        response=requests.get(actual_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image=soup.find("div",id="page")
        image_url=image.find("img", class_="img-fluid")["src"]
        print(image_url)
        img_url_list.append(image_url)
    return img_url_list

def get_opera_name(opera_url):
    response=requests.get(opera_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find("h1",class_="name").get_text(strip=True)
    return name

def download_volume(opera_url,volume_number):
    opera_name=get_opera_name(opera_url)
    #print(opera_name)
    chapter_number=0
    chapters_link=get_chapter_url_list(opera_url,volume_number)
    for chapter_link in chapters_link:
        chapter_number+=1
        num_page=0
        chapter_url_img_list=get_chapter_url_img_list(chapter_link, get_chapter_page_numer(chapter_link))
        for img in chapter_url_img_list:
            response = requests.get(img)
            num_page+=1

            # Crea cartelle
            dir_path = f"{opera_name}/volume-{volume_number}/capitolo-{chapter_number}"
            os.makedirs(dir_path, exist_ok=True)
            filename = os.path.join(dir_path, f"{num_page}.jpg")

            response.raise_for_status()  # altri errori HTTP
            # Salva l'immagine
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Pagina {num_page} del capitolo {chapter_number} scaricata!")

    create_pdf(opera_name, volume_number)

    dir_path = f"{opera_name}/volume-{volume_number}"

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def download_all_volumes(opera_url):
    volumes_num=get_volume_count(opera_url)
    for x in range(volumes_num):
        print("SCARICO IL VOLUME",x+1)
        download_volume(opera_url,x+1)

def create_pdf(opera_name,volume_num):
    root = f"{opera_name}/volume-{volume_num}"
    immagini = []

    # Elenco cartelle capitoli, es: capitolo-122, capitolo-123, ...
    capitoli = sorted(
        [d for d in os.listdir(root) if d.startswith("capitolo-")],
        key=lambda x: int(x.split("-")[1])  # ordina per numero capitolo
    )

    for cap in capitoli:
        cartella = os.path.join(root, cap)

        # Elenco pagine in ordine numerico
        pagine = sorted(
            [f for f in os.listdir(cartella) if f.endswith(".jpg")],
            key=lambda x: int(x.split(".")[0])
        )

        for pagina in pagine:
            path_img = os.path.join(cartella, pagina)
            immagini.append(path_img)

    if not immagini:
        print("Nessuna immagine trovata, impossibile creare PDF.")
        return

    # Apri tutte le immagini con Pillow
    pil_images = [Image.open(img).convert("RGB") for img in immagini]

    # Prima immagine è la "copertina"
    pdf_path = f"{opera_name}/volume-{volume_num}.pdf"
    pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
    print(f"\n📕 PDF creato correttamente: {pdf_path}")

if len(sys.argv)==2:
    download_all_volumes(sys.argv[1])
elif len(sys.argv)==3:
    download_volume(sys.argv[1],int(sys.argv[2]))
