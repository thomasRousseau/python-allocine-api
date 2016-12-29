import hashlib
from base64 import b64encode
try: # python3
	from urllib.parse import urlencode
except: #python2
	from urllib import urlencode
import requests
import time
import json
from pprint import pprint # for a more readable json output

ALLOCINE_BASE_URL = "http://api.allocine.fr/rest/v3/"
ALLOCINE_PARTNER_KEY = '100043982026'
ALLOCINE_SECRET_KEY = '29d185d98c984a359e6e6f26a0474269'
ANDROID_USER_AGENT = 'Dalvik/1.6.0 (Linux; U; Android 4.2.2; Nexus 4 Build/JDQ39E)'


def do_request(method, params):
    sed = time.strftime("%Y%m%d")
    sha1 = hashlib.sha1()
    PARAMETER_STRING = "partner=" + ALLOCINE_PARTNER_KEY + "&" + "&".join([k + "=" + params[k] for k in params.keys()]) + "&sed=" + sed
    SIG_STRING = bytes(ALLOCINE_SECRET_KEY + PARAMETER_STRING, 'utf-8')
    sha1.update(SIG_STRING)
    SIG_SHA1 = sha1.digest()
    SIG_B64 = b64encode(SIG_SHA1).decode('utf-8')
    sig = urlencode({SIG_B64: ''})[:-1]
    URL = ALLOCINE_BASE_URL + method + "?" + PARAMETER_STRING + "&sig=" + sig
    headers = {'User-Agent': ANDROID_USER_AGENT}
    results = requests.get(URL, headers=headers).text
    try:
        return json.loads(results)
    except Exception as e:
        return results


# search :
#   q : string to search
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   filter (optionnal) : filter depending on the result type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   count (optionnal) : number of results to return (should be an integer)
#   page (optionnal) : number of the results page to return (default is 10 results by page)
def search(string, format="json", filter=None, count=None, page=None):
    data = {'q': str(string), 'format': str(format)}
    if filter is not None:
        data["filter"] = filter.replace(",", "%2C")
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = str(page)
    return do_request("search", data)


# movie : information about a movie
#   code : film id (should be an integer)
#   profile (optionnal) : level of information returned ("small", "medium", or "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2")
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   filter (optionnal) : filter depending on the result type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def movie(code, profile=None, mediafmt=None, format="json", filter=None, striptags=None):
    data = {'code': str(code), 'format': format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    data['format'] = format
    if filter is not None:
        data["filter"] = filter
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("movie", data)


# reviewlist : critic (public or press) about a movie
#   type : type ("movie")
#   code : film id (should be an integer)
#   filter : critic type ("public", "desk-press")
#   count (optionnal) : number of critic to return (should be an integer)
#   page (optionnal) : page number to return (10 results by page by default)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def reviewlist(code, filter="public%2Cdesk-press", count=None, page=None, format="json"):
    data = {'code': str(code), "filter": filter, "format": format}
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = str(page)
    return do_request("reviewlist", data)


# showtimelist : theater schedule
#   zip : postal code of the city
#   lat : latitude coordinate of the theater
#   long : longitude coordinate of the theater
#   radius : radius around the location (between 1 and 500 km)
#   theaters : theaters code list (separated by a comma)
#   location : string identifying the theater
#   movie (optionnal) : film id (should be an integer, if not set, returns all movies)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   date (optionnal) : date, in the YYYY-MM-DD format (if not set, set to today)
def showtimelist(zip=None, lat=None, long=None, radius=None, theaters=None, location=None, movie=None, format="json", date=None):
    data = {"format": format}
    if zip is not None:
        data["zip"] = str(zip)
    if lat is not None:
        data["lat"] = str(lat)
    if long is not None:
        data["long"] = str(long)
    if radius is not None:
        data["radius"] = str(radius)
    if theaters is not None:
        data["theaters"] = theaters.replace(",", "%2C")
    if location is not None:
        data["location"] = location
    if movie is not None:
        data["movie"] = str(movie)
    if date is not None:
        data["date"] = date
    return do_request("showtimelist", data)


# media : information about a media
#   code : media id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def media(code, profile=None, mediafmt=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    return do_request("media", data)


# person : information about a person
#   code : person id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   filter (optionnal) : filter results by type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def person(code, profile=None, mediafmt=None, filter=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if filter is not None:
        data["filter"] = filter
    return do_request("person", data)


# filmography : person filmography
#   code : person id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   filter (optionnal) : filter the results by type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def filmography(code, profile=None, filter=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if filter is not None:
        data["filter"] = filter
    return do_request("filmography", data)


# movielist : movie list in theater
#   code : person id (should be an integer)
#   count (optionnal) : number of results to return (should be an integer)
#   page (optionnal) : number of the results page to return (default is 10 results by page)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   filter (optionnal) : filter results by type ("nowshowing", "comingsoon", separated by a comma)
#   order (optionnal) : order to sort the results ("datedesc", "dateasc", "theatercount", "toprank")
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def movielist(code, count=None, page=None, profile=None, filter=None, order=None, format="json"):
    data = {"code": str(code), "format": format}
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = page
    if profile is not None:
        data["profile"] = profile
    if filter is not None:
        data["filter"] = filter
    if order is not None:
        data["order"] = order
    return do_request("movielist", data)


# theaterlist : theater list
#   zip : postal code of the city
#   lat : latitude coordinate of the theater
#   long : longitude coordinate of the theater
#   radius : radius around the location (between 1 and 500 km)
#   theater : theater code (should be an integer)
#   location : string identifying the theater
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def theaterlist(zip=None, lat=None, long=None, radius=None, theater=None, location=None, format="json"):
    data = {"format": format}
    if zip is not None:
        data["zip"] = str(zip)
    if lat is not None:
        data["lat"] = str(lat)
    if long is not None:
        data["long"] = str(long)
    if radius is not None:
        data["radius"] = str(radius)
    if theater is not None:
        data["theater"] = theater
    if location is not None:
        data["location"] = location
    return do_request("theaterlist", data)


# tvseries : information about a TV serie
#   code : serie id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def tvseries(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("tvseries", data)


# season : information about a TV serie season
#   code : season id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def season(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("season", data)


# episode : information about an episode
#   code : season id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def episode(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("episode", data)
