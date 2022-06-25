from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold
import requests
import xbmcgui
import re
import urllib
import inputstreamhelper
from bs4 import BeautifulSoup
from resources.lib import KScraper as ks


@Route.register
def root(plugin, content_type="segment"):
    yield Listitem.search(search_drama)

    item = Listitem()
    item.label = "Watch Asian Drama"
    item.set_callback(list_drama, page_no=1)

    yield item


@Route.register
def list_drama(plugin, page_no):
    dramas = ks.recently_added(page_no)
    for drama in dramas["dramas"]:
        item = Listitem()
        item.label = drama["title"]
        item.art["thumb"] = drama["image"]
        item.art["fanart"] = drama["image"]
        item.info["plot"] = f'Watch {drama["title"]}'
        item.set_callback(
            get_episodes,
            drama_url=drama["href"],
            img_url=drama["image"],
        )

        yield item
    yield Listitem.next_page(page_no=dramas["next_page"], callback=list_drama)


@Route.register
def get_episodes(plugin, drama_url, img_url):

    episodes = ks.episodes(drama_url)

    for episode in episodes:
        item = Listitem()
        item.art["thumb"] = img_url
        item.art["fanart"] = img_url
        item.label = episode["title"]
        item.set_callback(
            play_video,
            video_url=episode["href"],
            v_title=episode["title"],
        )
        yield item


@Route.register
def search_drama(plugin, search_query):
    search_results = ks.search(search_query)

    for search_result in search_results:
        item = Listitem()
        item.label = search_result["title"]
        item.art["thumb"] = search_result["image"]
        item.art["fanart"] = search_result["image"]
        item.info["plot"] = f"Watch {search_result['title']}"
        item.set_callback(
            get_episodes,
            drama_url=search_result["href"],
            img_url=search_result["image"],
        )

        yield item


@Resolver.register
def play_video(plugin, video_url, v_title):
    vid_url = f"{ks.get_video(video_url)}|user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37&Accept-Language=en-US,en;q=0.9&watchsb=streamsb".strip()
    return Listitem().from_dict(
        **{
            "label": v_title,
            "callback": vid_url,
            "properties": {
                "inputstream.adaptive.manifest_type": "hls",
                "inputstream": "inputstream.adaptive",
            },
        }
    )
