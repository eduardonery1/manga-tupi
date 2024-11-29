import requests
import threading
import subprocess
import json
from tqdm import tqdm
from sys import exit
from menu import menu
from pathlib import Path
from collections import defaultdict


base_url = "https://api.mangadex.org"

def run(dir_path):
    subprocess.run(["feh", dir_path, "-R 1", "--fullscreen", "--scale-down"])





if __name__=="__main__":
    res = requests.get(
                f"{base_url}/manga",
                params={"title": input("Pesquise mangá: ")}).json()["data"]

    titles = [  manga["attributes"]["title"]["en"] 
                if "pt-br" not in manga["attributes"]["altTitles"] 
                else manga["attributes"]["altTitles"]["pt-br"] 
                for manga in res]

    title_ids = [manga["id"] for manga in res] 
    selected_title = menu(titles)

    offset = 0
    get = lambda query: requests.get(f"{base_url}/manga/{title_ids[titles.index(selected_title)]}/feed?{query}").json()["data"]
    current, chapters = [], []
    while not current or len(current) == 500: 
        query = "&".join(["limit=500",
                      "translatedLanguage[]=pt-br",
                      "translatedLanguage[]=en",
                      "order[chapter]=asc",
                      "includeEmptyPages=0",
                      "includeFuturePublishAt=0",
                      f"offset={offset}"])
        current = get(query)
        chapters.extend(current)
        offset += 500
    
    chapter_sources = defaultdict(list)
    for chap in chapters:
        if chap["attributes"]["chapter"] is None:
            continue
        chapter_sources[chap["attributes"]["chapter"]].append(chap)
    chapters_num = [f"{chap:.0f}" if chap == int(chap) else f"{chap:.1f}" for chap in sorted(list(map(float, chapter_sources.keys())))]
    
    def chapter_selection(selected_chapter = None):
        global chapters_num, chapter_sources
        if not selected_chapter:
            selected_chapter = menu(chapters_num)
        else:
            try:
                selected_chapter = chapters_num[chapters_num.index(selected_chapter) + 1]
            except:
                raise Exception("Sem mais capítulos.")
            
        def select_language():
            nonlocal selected_chapter
            chapter_translates = [chap["attributes"]["translatedLanguage"] + " " + str(i + 1) for i, chap in enumerate(chapter_sources[selected_chapter])]
            chapter_ids = [chap["id"] for chap in chapter_sources[selected_chapter]]
            selected_opt = menu(chapter_translates)

            pages = requests.get(f"{base_url}/at-home/server/{chapter_ids[chapter_translates.index(selected_opt)]}").json()
            dir_path = Path(f"{selected_title}/{selected_chapter}")
            dir_path.mkdir(parents=True, exist_ok=True)
            first = True
            thread = threading.Thread(target=run, args=(dir_path,))

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
        select_language()

        return selected_chapter
        
    prev = chapter_selection()
    while True:
        opt = menu(["Próximo"])
        if opt == "Próximo":
            prev = chapter_selection(prev)
        else:
            break

    


