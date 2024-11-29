import requests
import threading
import subprocess
import json
from tqdm import tqdm
from sys import exit
from menu import menu
from pathlib import Path
from collections import defaultdict

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


    query = "includeFuturePublishAt=0&includeExternalUrl=0&includeEmptyPages=0&limit=500&translatedLanguage[]=en&translatedLanguage[]=pt-br"
    chapters = requests.get(f"{base_url}/manga/{title_ids[titles.index(selected_title)]}/feed?{query}")
    #print(chapters.text)
    chapters = chapters.json()["data"]
    
    chapter_sources = defaultdict(list)
    for chap in chapters:
        chapter_sources[chap["attributes"]["chapter"]].append(chap)

    chapters_num = [f"{chap:.0f}" if chap == int(chap) else f"{chap:.1f}" for chap in sorted(list(map(float, chapter_sources.keys())))]
    selected_chapter = menu(chapters_num)

    chapter_translates = [chap["attributes"]["translatedLanguage"] + " " + str(i + 1) for i, chap in enumerate(chapter_sources[selected_chapter])]
    chapter_ids = [chap["id"] for chap in chapter_sources[selected_chapter]]
    selected_opt = menu(chapter_translates)

    pages = requests.get(f"{base_url}/at-home/server/{chapter_ids[chapter_translates.index(selected_opt)]}").json()
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


