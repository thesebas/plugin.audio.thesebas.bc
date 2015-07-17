__author__ = 'thesebas'

from bs4 import BeautifulSoup
import urllib2
from resources.router import expander
import re
import json

collection_url_tpl = expander("https://bandcamp.com/{username}?mvp=p")
wishlist_url_tpl = expander("https://bandcamp.com/{username}/wishlist?mvp=p")
albumcover_url_tpl = expander('https://f1.bcbits.com/img/a{albumartid}_9.jpg')
search_url_tpl = expander('https://bandcamp.com/search{?q}')


class Band(object):
    def __init__(self):
        pass


class Album(object):
    def __init__(self, **kwargs):
        self.cover = kwargs.get("cover", '')
        self.title = kwargs.get("title", '')
        self.url = kwargs.get("url", '')
        self.artist = kwargs.get("artist", '')

    def __str__(self):
        return "<Album artist=%s, title=%s, cover=%s, url=%s>" % (self.artist, self.title, self.cover, self.url)

    def __repr__(self):
        return 'Album(artist="%s", title="%s", cover="%s", url="%s")' % (self.artist, self.title, self.cover, self.url)

    @staticmethod
    def unserialize(data):
        if type(data) == Album:
            return data
        else:
            return Album(**data)


class Track(object):
    def __init__(self, album, **kwargs):
        self.title = kwargs.get("title", '')
        self.artist = kwargs.get("artist", '')
        self.track_url = kwargs.get("track_url", '')
        self.stream_url = kwargs.get("stream_url", '')
        self.album = album


def li_to_album(li):
    cover = li.find('img', class_='collection-item-art')["src"]
    info = li.find('div', class_='collection-item-details-container')
    title = info.find('div', class_='collection-item-title').string
    artist = info.find('div', class_='collection-item-artist').string
    url = li.find('a', class_='item-link')['href']
    artist = artist[3:]
    # print li.prettify('utf-8')
    return Album(title=title, artist=artist, cover=cover, url=url)


def tralbumdata_to_trac(data):
    if data["file"] is None:  # not playable files
        return None

    return Track(None, title=data["title"], artist="", track_url="", stream_url=data["file"]["mp3-128"])


def itemdetail_to_album(detail):
    return Album(url=detail["item_url"], artist=detail["band_name"], title=detail["item_title"],
                 cover=albumcover_url_tpl({"albumartid": detail["item_art_id"]}))


def li_to_searchresult(li):
    if "band" in li["class"]:
        return Band()
    elif "album" in li["class"]:
        url = li.find('a', class_='artcont')["href"]
        title = li.find('div', class_='result-info').find('div', class_='heading').a.string.strip()
        cover = li.find('div', class_='art').img['src']
        return Album(url=url, title=title, cover=cover)
    elif "track" in li["class"]:
        return Track(None)

    return None


def get_wishlist(user):
    url = wishlist_url_tpl({"username": user})
    res = urllib2.urlopen(url)
    body = res.read()
    m = re.search("^\s+item_details: (.*),$", body, re.M)
    if m:
        data = json.loads(m.group(1))
        return [itemdetail_to_album(detail) for id, detail in data.iteritems()]
    return []


def get_collection(user):
    url = collection_url_tpl({"username": user})
    res = urllib2.urlopen(url)
    body = res.read()
    soup = BeautifulSoup(body, 'html.parser')

    return [li_to_album(li) for li in soup.find_all('li', class_='collection-item-container')]


def get_album_tracks(url):
    res = urllib2.urlopen(url)
    body = res.read()
    m = re.search("trackinfo : (.*),", body, re.M)
    print m
    if m:
        data = json.loads(m.group(1))
        print data
        return [track for track in [tralbumdata_to_trac(track) for track in data] if track is not None]

    return []


def get_search_results(query):
    print "searching for '%s'" % (query,)
    res = urllib2.urlopen(search_url_tpl(dict(q=query)))
    body = res.read()

    soup = BeautifulSoup(body, 'html.parser')
    return [item for item in [li_to_searchresult(li) for li in
                              soup.find('ul', class_='result-items').find_all('li', class_='searchresult')] if item]
