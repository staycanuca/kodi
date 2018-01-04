import HTMLParser
import cookielib
import json
import os
import re
import sys
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


website = 'http://www.digi24.ro'

settings = xbmcaddon.Addon(id='plugin.video.digi24')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')


def ROOT():
    addDir('Video', 'http://www.digi24.ro/video', 23, movies_thumb, 'emisiuni_link')
    addDir('Emisiuni', 'http://www.digi24.ro/emisiuni', 23, movies_thumb, 'emisiuni')
    addDir('Emisiuni exclusiv online', 'http://www.digi24.ro/video/emisiuni/exclusiv-online', 23, movies_thumb, 'emisiuni_link')
    addDir('24 Minute', 'http://www.digi24.ro/video/emisiuni/exclusiv-online/24-minute', 23, movies_thumb, 'emisiuni_link')
    addDir('Live Digi24', 'http://www.digi24.ro/live/digi24', 23, movies_thumb, 'live')
    addDir('Live Digi24 Brasov', 'http://www.digi24.ro/live/digi24-brasov', 23, movies_thumb, 'live')
    addDir('Live Digi24 Constanta', 'http://www.digi24.ro/live/digi24-constanta', 23, movies_thumb, 'live')
    addDir('Live Digi24 Craiova', 'http://www.digi24.ro/live/digi24-craiova', 23, movies_thumb, 'live')
    addDir('Live Digi24 Iasi', 'http://www.digi24.ro/live/digi24-iasi', 23, movies_thumb, 'live')
    addDir('Live Digi24 Oradea', 'http://www.digi24.ro/live/digi24-oradea', 23, movies_thumb, 'live')
    addDir('Live Digi24 Timisoara', 'http://www.digi24.ro/live/digi24-timisoara', 23, movies_thumb, 'live')
    addDir('Live Digi24 Galati', 'http://www.digi24.ro/live/digi24-galati', 23, movies_thumb, 'live')
    addDir('Live Digi24 Cluj-Napoca', 'http://www.digi24.ro/live/digi24-cluj-napoca', 23, movies_thumb, 'live')
    
    addDir('Cauta', 'http://www.digi24.ro/cautare?q=', 3, search_thumb) #http://www.digi24.ro/live/digi24-constanta


def CAUTA(url, autoSearch=None):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() is False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    if autoSearch is None:
        autoSearch = ""
    parse_menu(get_search_url(search_string), 'search', urllib.quote_plus(search_string))


def SXVIDEO_GENERIC_PLAY(sxurl):
    f = HTMLParser.HTMLParser()
    sxurl = f.unescape(sxurl)
    link = get_search(sxurl)
    match = re.compile('(itemprop="headline">(.+?)<|<h1 class="h3">(.+?)<).+?source":"(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    # match2=re.compile('<meta property="og:title" content="(.+?)".+?\n\s*.+?content="(.+?)"', re.IGNORECASE|re.MULTILINE|re.DOTALL).findall(link)
    if len(match) > 0:
        # if len(match2) > 0:
        # var player_config.+?\n\s*.+?\n\s*"url": "(.+?)",(\n\s*.+?){15}url": "(.+?)",\n\s*.+?netConnectionUrl": \'(.+?)\'
        path = str(match[0][3])
        path = re.sub('\\\\', '', path)
        if match[0][1]:
            title = match[0][1]
	else:
            title = match[0][2]
        #iconimage = "DefaultVideo.png"
        #f = open('/storage/.kodi/temp/files.py', 'w')
        #f.write('match = ' + repr(path) + '\n')
        #f.close()
        item = xbmcgui.ListItem(path=path)
        item.setInfo('video', {'Title': title, 'Plot': title})
        xbmc.Player().play(path, item)


def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False


def get_search_url(keyword, offset=None):
    url = 'http://www.digi24.ro/cautare?q=' + urllib.quote_plus(keyword)
    return url


def get_search(url):
    f = HTMLParser.HTMLParser()
    url = f.unescape(url)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'),
        ('Content-type', 'application/x-www-form-urlencoded'),
        ]
    try:
        response = opener.open(url)
        link = response.read()
        return link
    except:
        return False


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def sxaddLink(name, url, iconimage, movie_name, mode=4, descript=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if descript is not None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu is not None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDir(name, url, mode, iconimage, meniu=None, descript=None):
    # f = HTMLParser.HTMLParser()
    # linkem = f.unescape(url)
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if meniu is not None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descript is not None:
        u += "&descriere=" + urllib.quote_plus(descript)
        ok = True
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
        if meniu == 'live':
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	else:
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        # link = get_search(url)
    return ok


def parse_menu(url, meniu, searchterm=None):
    if url is None:
        url = 'http://www.digi24.ro'
    if meniu == 'video':
        link = get_search(url)
        match = re.compile('<figure class="card-img.+?<a href="(.+?)">.+? dat.+?"(.+?)".+?card-title">(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        for legatura, imagine, nume in match:
            linkem = website + legatura
            nume = re.sub(' +', ' ', nume)
            descriere = nume
            sxaddLink(nume, linkem, imagine, nume, 10, descriere)
    elif meniu == 'emisiuni':
        match = []
        link = get_search(url)
        regex = '''<article class="card col-xs-3">(.+?)</article>'''
        regex_art = '''<figure class="card-img.+?<a href="(.+?)".+? dat.+?"(.+?)".+?title=".+?">(.+?)<'''
        # match=re.compile('<figure class="card-img.+?<a href="(.+?)">.+? dat.+?"(.+?)".+?card-title">(.+?)<', re.IGNORECASE|re.MULTILINE|re.DOTALL).findall(link)
        for art in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            result = re.compile(regex_art, re.DOTALL).findall(art)
            if result:
                (legatura, image, nume) = result[0]
                match.append((legatura,
                             image,
                             nume,
                             ))
        for legatura, imagine, nume in match:
            linkem = website + legatura
            nume = re.sub(' +', ' ', nume)
            descriere = nume
            addDir(nume, linkem, 23, imagine, 'emisiuni_link')
    elif meniu == 'emisiuni_link':
        match = []
        link = get_search(url)
        regex = '''<article class="card col.+?">(.+?)</article>'''
        regex_art = '''<figure class="card-img.+?<a href="(.+?)".+?title="(.+?)".+?<img src="(.+?)"'''
        # match=re.compile('<figure class="card-img.+?<a href="(.+?)">.+? dat.+?"(.+?)".+?card-title">(.+?)<', re.IGNORECASE|re.MULTILINE|re.DOTALL).findall(link)
        for art in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            result = re.compile(regex_art, re.DOTALL).findall(art)
            if result:
                (legatura, nume, imagine) = result[0]
                match.append((legatura,
                             imagine,
                             nume,
                             ))
        for legatura, imagine, nume in match:
            linkem = website + legatura
            nume = re.sub(' +', ' ', nume)
            descriere = nume
            sxaddLink(nume, linkem, imagine, nume, 10, descriere)
        match = re.compile('\?p=', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            page_num = re.compile('\?p=(.+?)', re.IGNORECASE).findall(str(url))
            if len(page_num) > 0:
                pagen = int(page_num[0]) + 1
                nexturl = re.sub('\?p=(\d+)', '?p=' + str(pagen), url)
            else:
                nexturl = url + '?p=2'
            #f = open( '/storage/.kodi/temp/files.py', 'w' )
            #f.write( 'match = ' + repr(str(nexturl)) + '\n' )
            #f.close()
            addNext('Next', nexturl, 23, next_thumb, 'emisiuni_link')
    elif meniu == 'search':
        link = get_search(url)
        match = re.compile('<article class="card"> <figure class="card-img-top"> <div class="img-responsive img-responsive-16by9"> <a href="(.+?)".+?img src="(.+?)".+?title="title">(.+?)<.+?<p class="card-text">(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            print match
        for legatura, imagine, nume, descriere in match:
            linkem = website + legatura
            sxaddLink(nume, linkem, imagine, nume, 10, descriere)
        match = re.compile('\&p=', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            page_num = re.compile('\&p=(.+?)', re.IGNORECASE).findall(str(url))
            if len(page_num) > 0:
                pagen = int(page_num[0]) + 1
                nexturl = re.sub('\&p=(\d+)', '&p=' + str(pagen), url)
            else:
                nexturl = url + '&p=2'
            addNext('Next', nexturl, 23, next_thumb, 'search')
    elif meniu == 'live':
        link = get_search(url)
        match = re.compile('"scope":"(.+?)"').findall(link)
        if len(match) > 0:
            print match
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'),
            ('Host', 's2.220.t1.ro'),
            ('Referer', url)]
        make_key = opener.open('http://balancer.digi24.ro/streamer/make_key.php')
        link = 'http://balancer.digi24.ro/streamer.php?&scope=' + match[0] + '&key=' + str(make_key.read()) + '&outputFormat=json&type=hls&quality=hq'
        file = opener.open(link).read()
        infos = json.loads(file)
        result = infos['file']
        imagine = "DefaultFolder.png"
        item = xbmcgui.ListItem(path=result)
        item.setInfo('video', {'Title': match[0]})
        xbmc.Player().play(result, item)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


params = get_params()
url = None
mode = None
meniu = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    meniu = urllib.unquote_plus(params["meniu"])
except:
    pass


# print "Mode: "+str(mode)
# print "URL: "+str(url)
# print "Name: "+str(name)

if mode is None or url is None or len(url) < 1:
    ROOT()
elif mode == 3:
    CAUTA(url)
elif mode == 23:
    parse_menu(url, meniu)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
