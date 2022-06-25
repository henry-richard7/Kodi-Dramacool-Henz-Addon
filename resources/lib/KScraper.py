from bs4 import BeautifulSoup
import requests
import re

BASE_URL = "https://asianembed.io/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.0.43 Safari/537.36"
}


def recently_added(page_number: int = 1) -> list:
    """
    Returns a list of recently added shows.
    """

    result = []
    next_page_number = page_number + 1
    page = requests.get(f"{BASE_URL}/?page={page_number}", headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    shows = soup.find("ul", class_="listing items")

    for show in shows.find_all("li"):
        result.append(
            {
                "title": show.select_one("div[class='name']").get_text().strip(),
                "image": show.find("img").get("src"),
                "href": f'{BASE_URL}{show.find("a").get("href")}',
            }
        )
    return {"dramas": result, "next_page": next_page_number}


def search(query: str) -> list:
    """
    Returns a list of shows matching the query.
    """

    result = []

    page = requests.get(f"{BASE_URL}/search.html?keyword={query}", headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    shows = soup.find("ul", class_="listing items")

    for show in shows.find_all("li"):
        result.append(
            {
                "title": show.select_one("div[class='name']").get_text().strip(),
                "image": show.find("img").get("src"),
                "href": f'{BASE_URL}{show.find("a").get("href")}',
            }
        )
    return result


def episodes(url: str) -> list:
    """
    Returns a list of episodes for a show.
    """

    result = []

    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    episodes = soup.find("ul", class_="listing items lists")

    for episode in episodes.find_all("li"):
        result.append(
            {
                "title": episode.select_one("div[class='name']").get_text().strip(),
                "image": episode.find("img").get("src"),
                "href": f'{BASE_URL}{episode.find("a").get("href")}',
            }
        )
    return result


def get_video(url: str) -> str:
    """
    Returns the video URL for an episode.
    """

    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    video = soup.find("div", class_="play-video")

    first_iframe = f'https:{video.find("iframe").get("src")}'
    second_iframe = requests.get(first_iframe, headers=HEADERS)
    soup = BeautifulSoup(second_iframe.content, "html.parser")

    sbplay_url = (
        soup.find("ul", class_="list-server-items")
        .find("li", attrs={"data-provider": "streamsb"})
        .get("data-video")
    )

    id_ = re.search(r"\/e\/(.*)\?c", sbplay_url).group(1)
    id_ = bytearray(id_, "utf-8")

    master_url = f"https://watchsb.com/sources43/6d6144797752744a454267617c7c{id_.hex()}7c7c4e61755a56456f34385243727c7c73747265616d7362/6b4a33767968506e4e71374f7c7c343837323439333133333462353935333633373836643638376337633462333634663539343137373761333635313533333835333763376333393636363133393635366136323733343435323332376137633763373337343732363536313664373336327c7c504d754478413835306633797c7c73747265616d7362"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37",
        "Accept-Language": "en-US,en;q=0.9",
        "watchsb": "streamsb",
    }

    last_link = requests.get(master_url, headers=headers).json()["stream_data"]["file"]
    return last_link
