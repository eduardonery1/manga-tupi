import requests
import threading
import subprocess
import json
from tqdm import tqdm
from sys import exit
from menu import menu
from pathlib import Path


def run(dir_path):
    subprocess.run(["feh", dir_path, "-R 1", "--fullscreen", "--scale-down"])

if __name__=="__main__":

    base_url = "https://api.mangadex.org"

    r = requests.get(
        f"{base_url}/manga",
        params={"title": input("Pesquise mangá: ")}
    )
    with open("query.json", "w") as f:
        json.dump(r.json(), f)

    titles = [manga["attributes"]["title"]["en"] if "pt-br" not in manga["attributes"]["altTitles"] else manga["attributes"]["altTitles"]["pt-br"] for manga in r.json()["data"]]
    title_ids = [manga["id"] for manga in r.json()["data"]] 
    selected_title = menu(titles)
    if selected_title == "EXIT":
        exit()

    chapters = requests.get(
        f"{base_url}/manga/{title_ids[titles.index(selected_title)]}/feed?includeFuturePublishAt=0&includeExternalUrl=0&includeEmptyPages=0&limit=500&translatedLanguage[]=en&translatedLanguage[]=pt-br"
    )
    #print(chapters.text)
    chapters = chapters.json()["data"]
    chapters = [chaps for chaps in filter(lambda chap: chap["attributes"]["translatedLanguage"] == "pt-br" or chap["attributes"]["translatedLanguage"] == "en", chapters)]
    chapters.sort(key = lambda chap: float(chap["attributes"]["chapter"]))
    chapters_num = [chap["attributes"]["chapter"] + " - " + chap["attributes"]["translatedLanguage"] for chap in chapters]
    chapter_ids = [chap["id"] for chap in chapters]
    selected_chapter = menu(chapters_num)
    if selected_chapter == "EXIT":
        exit()

    pages = requests.get(
        f"{base_url}/at-home/server/{chapter_ids[chapters_num.index(selected_chapter)]}"
    ).json()
    dir_path = Path(f"{selected_title}/{selected_chapter}")
    dir_path.mkdir(parents=True, exist_ok=True)
    first = True
    thread = threading.Thread(target=run, args=(dir_path,))
    #print(pages)
    print("Baixando páginas enquanto vc vê o mangá, pode ser que precise esperar um pouco...")
    for i in tqdm(range(len(pages["chapter"]["data"]))):
        url = pages["baseUrl"] + "/data/" + pages["chapter"]["hash"] + "/" + pages["chapter"]["data"][i]
        img_data = requests.get(url).content
        img_path = str(dir_path) + f"/{i}.png"
        with open(img_path, "wb") as img:
            img.write(img_data)
        if first:
            thread.start()
            first = False
    thread.join()


