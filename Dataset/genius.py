"""
Scrape song annotations from Genius.com
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Literal, Dict, List


HTML_MAPPING = {
    "annotation_property": "og:description",
    "lyrics_class": "Lyrics__Container-sc-1ynbvzw-1 kUgSbL",
    "song_list_class": "chart_row-content",
    "song_name_class": "chart_row-content-title"
}



class GeniusApi:

    html_mapping = HTML_MAPPING

    def __init__(self):
        pass


    def scrape(self, url, mode: Literal["artist", "album", "song", "annotation"]):
        
        """
        Scrape the given url page. The page should be artist, album, song, or annotation page from Genius.com.
        """

        if mode == "artist":
            pass
        elif mode == "album":
            return self._parse_album_page(url)
        elif mode == "song":
            return self._parse_song_page(url)
        elif mode == "annotation":
            return self._parse_annotation_page(url)
        
    
    def _parse_annotation_page(self, url):

        """
        Parse the genius annotation from the annotation page.
        """

        response = requests.get(url)
        if not response.status_code < 400:
            raise Exception(f"Failed to fetch annotation page: {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.head.find("meta", property=self.html_mapping["annotation_property"])
        if not soup:
            print(f"no annotation found")
            return ""

        return soup.get("content")
    

    def _parse_song_page(self, url: str) -> List[Dict[str, str]]:

        """
        parse the song page to get the lyrics and corresponding annotation.

        output schema: List of
        {
            "lyrics": str,
            "annotation": str,
            "source": str
        }
        """

        response = requests.get(url)
        if not response.status_code < 400:
            raise Exception(f"Failed to fetch song page: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")        
        soup = soup.find("div", class_=self.html_mapping["lyrics_class"])
        if (not soup) or (not soup.find_all("a", href=True)):
            print(f"no lyrics or annotation found")
            return []

        link_to_lyrics = {}
        for annotation_link, annotated_lyrics in ((a.get("href"), a.get_text(" ")) for a in soup.find_all("a", href=True)):
            if annotation_link.startswith("/"):
                annotation_link = f"https://genius.com{annotation_link}"
            
            if annotation_link in link_to_lyrics:
                # treat duplicated annotation.
                if annotated_lyrics.strip() in link_to_lyrics[annotation_link]:
                    continue
                else:
                    link_to_lyrics[annotation_link] += f"\n{annotated_lyrics.strip()}"
            else:
                link_to_lyrics[annotation_link] = annotated_lyrics.strip()
        
        output = []
        for link, lyrics in link_to_lyrics.items():
            output.append({
                "lyrics": lyrics,
                "annotation": self._parse_annotation_page(link),
                "source": link
            })
            print(f"parsed {len(output)}/{len(link_to_lyrics)} annotations")

        return output
    

    def _parse_album_page(self, url: str) -> List[Dict]:
        
        """
        Parse the album page.
        output schema: 
        List of
        {
            "name": song name,
            "content": list of dictionary of (lyrics, annotation, annotation source url),
            "lyrics_source": lyrics source url
        }
        """

        response = requests.get(url)
        if not response.status_code < 400:
            raise Exception(f"Failed to fetch song page: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        song_list_soup = soup.find_all("div", class_=self.html_mapping["song_list_class"])

        output = []
        for song_soup in song_list_soup:
            song_title = song_soup.find("h3", class_="chart_row-content-title")
            song_link = song_soup.find("a")["href"]

            print(f"parsing {song_title.contents[0].strip()}")
            song_content = self._parse_song_page(song_link)
            print(f"parsed {len(song_content)} annotations\n")

            output.append({"name": song_title.contents[0].strip(), "content": song_content, "lyrics_source": song_link})
        
        return output






def main():

    write_path = "data/Frank Ocean/channel ORANGE.json"

    genius = GeniusApi()
    parsed_material = genius.scrape("https://genius.com/albums/Frank-ocean/Channel-orange", "album")

    with open(write_path, "w", encoding="utf-8") as f:
        json.dump(parsed_material, f, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    main()

