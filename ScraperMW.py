import argparse
import re
import shutil
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image


TIMEOUT = 30


def fetch_soup(url, session):
    """Scarica una pagina e restituisce il suo oggetto BeautifulSoup."""
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_volume_elements(soup):
    """Restituisce gli elementi HTML che rappresentano i volumi."""
    return soup.find_all("div", class_="volume-element")


def get_volume_count(opera_url):
    """Restituisce il numero totale di volumi dell'opera."""
    with requests.Session() as session:
        soup = fetch_soup(opera_url, session)
        return len(get_volume_elements(soup))


def get_opera_name(soup):
    """Estrae il nome dell'opera dalla pagina già scaricata."""
    title = soup.find("h1", class_="name")

    if title is None:
        raise ValueError("Impossibile trovare il nome dell'opera.")

    name = title.get_text(strip=True)

    # Evita caratteri non validi nei nomi di file e cartelle.
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")

    if not name:
        raise ValueError("Il nome dell'opera non è valido.")

    return name


def get_chapter_url_list_from_soup(soup, volume_number):
    """Estrae gli URL dei capitoli di un volume numerato da 1."""
    volumes = get_volume_elements(soup)
    volume_count = len(volumes)

    if not 1 <= volume_number <= volume_count:
        raise ValueError(
            f"Volume non valido: scegli un numero tra 1 e {volume_count}."
        )

    # Il sito mostra prima il volume più recente.
    volume = volumes[volume_count - volume_number]

    chapter_urls = []

    for chapter in volume.find_all("div", class_="chapter"):
        link = chapter.find("a", class_="chap")

        if link and link.get("href"):
            chapter_urls.append(urljoin(soup.base_url or "", link["href"]))

    # Mantiene il comportamento del programma originale.
    chapter_urls.reverse()

    return chapter_urls


def get_chapter_url_list(opera_url, volume_number):
    """Restituisce gli URL dei capitoli di un volume."""
    with requests.Session() as session:
        soup = fetch_soup(opera_url, session)
        return get_chapter_url_list_from_soup(soup, volume_number)


def get_chapter_number(opera_url, volume_number):
    """Restituisce il numero di capitoli presenti in un volume."""
    return len(get_chapter_url_list(opera_url, volume_number))


def get_chapter_page_count(chapter_url, session):
    """Conta le pagine indicate nel selettore HTML del capitolo."""
    soup = fetch_soup(chapter_url, session)
    page_select = soup.find("select", class_="page")

    if page_select is None:
        raise ValueError(f"Selettore delle pagine non trovato: {chapter_url}")

    return len(page_select.find_all("option"))


def get_chapter_image_urls(chapter_url, page_count, session):
    """Estrae gli URL delle immagini di tutte le pagine del capitolo."""
    image_urls = []

    for page_number in range(1, page_count + 1):
        page_url = urljoin(chapter_url.rstrip("/") + "/", str(page_number))
        soup = fetch_soup(page_url, session)

        page_container = soup.find("div", id="page")
        image = (
            page_container.find("img", class_="img-fluid")
            if page_container
            else None
        )

        if image is None or not image.get("src"):
            raise ValueError(f"Immagine non trovata nella pagina: {page_url}")

        image_urls.append(urljoin(page_url, image["src"]))

    return image_urls


def download_image(image_url, destination, session):
    """Scarica un'immagine e la salva in formato JPEG."""
    response = session.get(image_url, timeout=TIMEOUT)
    response.raise_for_status()

    # Conversione esplicita: il file JPEG rimane valido anche se
    # il server restituisce un'immagine in un altro formato.
    with Image.open(BytesIO(response.content)) as image:
        image.convert("RGB").save(destination, format="JPEG", quality=95)


def create_pdf(opera_name, volume_number, output_dir):
    """Crea il PDF del volume, ordinando capitoli e pagine numericamente."""
    volume_dir = output_dir / opera_name / f"volume-{volume_number}"

    if not volume_dir.is_dir():
        print(f"Cartella del volume non trovata: {volume_dir}")
        return None

    chapter_dirs = sorted(
        (
            path for path in volume_dir.iterdir()
            if path.is_dir() and path.name.startswith("capitolo-")
        ),
        key=lambda path: int(path.name.split("-")[-1]),
    )

    image_paths = []

    for chapter_dir in chapter_dirs:
        pages = sorted(
            (
                path for path in chapter_dir.iterdir()
                if path.is_file() and path.suffix.lower() == ".jpg"
            ),
            key=lambda path: int(path.stem),
        )
        image_paths.extend(pages)

    if not image_paths:
        print("Nessuna immagine trovata: PDF non creato.")
        return None

    pdf_path = output_dir / opera_name / f"volume-{volume_number}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Usa un context manager per chiudere correttamente la prima immagine.
    with Image.open(image_paths[0]) as first_image:
        first_image.convert("RGB").save(
            pdf_path,
            "PDF",
            save_all=True,
            append_images=[
                Image.open(path).convert("RGB")
                for path in image_paths[1:]
            ],
        )

    print(f"PDF creato: {pdf_path}")
    return pdf_path


def _download_volume(
    opera_url, opera_name, soup, volume_number, session, output_dir
):
    """Scarica un volume e genera il relativo PDF."""
    chapter_urls = get_chapter_url_list_from_soup(soup, volume_number)

    if not chapter_urls:
        print(f"Nessun capitolo trovato per il volume {volume_number}.")
        return

    volume_dir = output_dir / opera_name / f"volume-{volume_number}"

    try:
        for chapter_number, chapter_url in enumerate(chapter_urls, start=1):
            print(f"Volume {volume_number}: capitolo {chapter_number}")

            page_count = get_chapter_page_count(chapter_url, session)
            image_urls = get_chapter_image_urls(
                chapter_url, page_count, session
            )

            chapter_dir = volume_dir / f"capitolo-{chapter_number}"
            chapter_dir.mkdir(parents=True, exist_ok=True)

            for page_number, image_url in enumerate(image_urls, start=1):
                destination = chapter_dir / f"{page_number}.jpg"
                download_image(image_url, destination, session)
                print(f"  Pagina {page_number}/{page_count} scaricata")

        pdf_path = create_pdf(opera_name, volume_number, output_dir)

        # Elimina le immagini temporanee soltanto se il PDF è stato creato.
        if pdf_path is not None and pdf_path.is_file():
            shutil.rmtree(volume_dir, ignore_errors=True)

    except Exception:
        # Conserva le immagini già scaricate per consentire il recupero.
        print(
            f"Errore durante il download del volume {volume_number}. "
            f"I file temporanei, se presenti, sono conservati."
        )
        raise


def download_volume(opera_url, volume_number, output_dir):
    """Scarica un singolo volume e crea il PDF."""
    with requests.Session() as session:
        soup = fetch_soup(opera_url, session)
        opera_name = get_opera_name(soup)

        _download_volume(
            opera_url, opera_name, soup, volume_number, session, output_dir
        )


def download_all_volumes(opera_url, output_dir):
    """Scarica tutti i volumi dell'opera."""
    with requests.Session() as session:
        soup = fetch_soup(opera_url, session)
        opera_name = get_opera_name(soup)
        volume_count = len(get_volume_elements(soup))

        if volume_count == 0:
            raise ValueError("Nessun volume trovato per questa opera.")

        for volume_number in range(1, volume_count + 1):
            print(f"\nScaricamento volume {volume_number}/{volume_count}")
            _download_volume(
                opera_url, opera_name, soup, volume_number,
                session, output_dir
            )


def main():
    parser = argparse.ArgumentParser(
        description="Scarica i volumi di un'opera e li converte in PDF."
    )

    parser.add_argument(
        "opera_url",
        help="URL della pagina dell'opera"
    )

    parser.add_argument(
        "volume",
        nargs="?",
        type=int,
        help="Numero del volume da scaricare; se omesso, scarica tutti i volumi",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Cartella in cui salvare il manga (predefinita: directory corrente)",
    )

    args = parser.parse_args()
    output_dir = args.output_dir.expanduser()

    try:
        if args.volume is None:
            download_all_volumes(args.opera_url, output_dir)
        elif args.volume < 1:
            parser.error("Il numero del volume deve essere almeno 1.")
        else:
            download_volume(args.opera_url, args.volume, output_dir)

    except (requests.RequestException, ValueError) as error:
        parser.exit(1, f"Errore: {error}\n")


if __name__ == "__main__":
    main()