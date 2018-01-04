# -*- coding: utf-8 -*- 

import cookielib
import re
import struct
import unicodedata
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcvfs

__addon__      = xbmcaddon.Addon()
__version__    = __addon__.getAddonInfo('version') # Module version
__scriptname__ = "XBMC Subtitles"

BASE_URL = "http://subtitrari.regielive.ro/cauta.html?s="

class OSDBServer:
    def __init__(self, * args, ** kwargs):
        self.server = BASE_URL
        self.osdb_token  = '1'

    def searchsubtitles(self, item):
        if len(item['tvshow']) > 0:
            OS_search_string = item['tvshow'].replace(" ", "+")      
        else:
            if str(item['year']) == "":
                item['title'], item['year'] = xbmc.getCleanMovieTitle(item['title'])
    
            OS_search_string = item['title'].replace(" ", "+")
            
        if item['mansearch']:
            s_string = urllib.unquote(item['mansearchstr'])
            OS_search_string = s_string.replace(" ", "+")
        #log( __name__ , "Search String [ %s ]" % (OS_search_string,))
        link1 = self.server + OS_search_string
        link = get_search(link1)
        first_search = re.compile('class="post_title">.+?<a href="(.+?)"', re.IGNORECASE | re.DOTALL).findall(link)
        if item['season']:
            season = item['season']
            episode = item['episode']
            rename_tvshow_link = first_search[0] + 'sezonul-' + item['season'] + '/' + 'episodul-' + item['episode'] + '/'
            search = re.compile('<div class="col-md-12 nume.+?>(.+?)<.+?<ul class="rating_list_subtitrare.+?( |title="Nota (.+?) d).+?<div class="col-md-3 descarca.+?<a href="(.+?)"', re.IGNORECASE | re.DOTALL).findall(get_search(rename_tvshow_link))
        else:
            season = '0'
            episode = '0'
            search = re.compile('<div class="col-md-12 nume.+?>(.+?)<.+?<ul class="rating_list_subtitrare.+?( |title="Nota (.+?) d).+?<div class="col-md-3 descarca.+?<a href="(.+?)"', re.IGNORECASE | re.DOTALL).findall(get_search(first_search[0]))
        #f = open( '/storage/.kodi/temp/files3.py', 'w' )
        #f.write( 'url = ' + repr(rename_tvshow_link) + '\n' )
        #f.close()
        clean_search = []
        if len(search) > 0:
            for item_search in search:
                s_title = re.sub('\s+', '', item_search[0])
                if item_search[2] is not None:
                    rating = item_search[2]
                else:
                    rating = '0'
                clean_search.append({'SeriesSeason': season, 'SeriesEpisode': episode, 'LanguageName': 'Romanian', 'episode': '0', 'SubFileName': s_title + '.srt', 'SubRating': rating, 'ZipDownloadLink': item_search[3], 'ISO639': 'ro', 'SubFormat': 'srt', 'MatchedBy': 'fulltext', 'SubHearingImpaired': '0'})
	  
        #search = self.server.SearchSubtitles( OS_search_string )
            if clean_search:
                return clean_search 
        else:
            return None
     
def get_search(url):
    ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    req = urllib2.Request(url)
    req.add_header('User-Agent', ua)
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False

def get_zip(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    #log( __name__ ,"Getting url: %s with referer %s" % (url, referer))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'),
        ('Host', 'regielive.ro'),
        ('Referer', 'subtirari.regielive.ro/vice-23811/')]
    content = None
    try:
        response = opener.open(url)
        content = response.read()
        response.close()
    except:
        log(__name__, "Failed to get url:%s" % (url))
    #log( __name__ ,"Got content from url: %s" % (url))
    return content
      
def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module, msg,)).encode('utf-8'), level=xbmc.LOGDEBUG) 

def hashFile(file_path, rar):
    if rar:
        return OpensubtitlesHashRar(file_path)
      
    log(__name__, "Hash Standard file")  
    longlongformat = 'q'  # long long
    bytesize = struct.calcsize(longlongformat)
    f = xbmcvfs.File(file_path)
    
    filesize = f.size()
    hash = filesize
    
    if filesize < 65536 * 2:
        return "SizeError"
    
    buffer = f.read(65536)
    f.seek(max(0, filesize-65536), 0)
    buffer += f.read(65536)
    f.close()
    for x in range((65536 / bytesize) * 2):
        size = x * bytesize
        (l_value,) = struct.unpack(longlongformat, buffer[size:size + bytesize])
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF
    
    returnHash = "%016x" % hash
    return filesize, returnHash


def OpensubtitlesHashRar(firsrarfile):
    log(__name__, "Hash Rar file")
    f = xbmcvfs.File(firsrarfile)
    a = f.read(4)
    if a != 'Rar!':
        raise Exception('ERROR: This is not rar file.')
    seek = 0
    for i in range(4):
        f.seek(max(0, seek), 0)
        a = f.read(100)        
        type, flag, size = struct.unpack('<BHH', a[2:2 + 5]) 
        if 0x74 == type:
            if 0x30 != struct.unpack('<B', a[25:25 + 1])[0]:
                raise Exception('Bad compression method! Work only for "store".')            
            s_partiizebodystart = seek + size
            s_partiizebody, s_unpacksize = struct.unpack('<II', a[7:7 + 2 * 4])
            if (flag & 0x0100):
                s_unpacksize = (struct.unpack('<I', a[36:36 + 4])[0] << 32) + s_unpacksize
                log(__name__, 'Hash untested for files biger that 2gb. May work or may generate bad hash.')
            lastrarfile = getlastsplit(firsrarfile, (s_unpacksize-1) / s_partiizebody)
            hash = addfilehash(firsrarfile, s_unpacksize, s_partiizebodystart)
            hash = addfilehash(lastrarfile, hash, (s_unpacksize % s_partiizebody) + s_partiizebodystart-65536)
            f.close()
            return (s_unpacksize, "%016x" % hash)
        seek += size
    raise Exception('ERROR: Not Body part in rar file.')

def getlastsplit(firsrarfile, x):
    if firsrarfile[-3:] == '001':
        return firsrarfile[:-3] + ('%03d' % (x + 1))
    if firsrarfile[-11:-6] == '.part':
        return firsrarfile[0:-6] + ('%02d' % (x + 1)) + firsrarfile[-4:]
    if firsrarfile[-10:-5] == '.part':
        return firsrarfile[0:-5] + ('%1d' % (x + 1)) + firsrarfile[-4:]
    return firsrarfile[0:-2] + ('%02d' % (x-1))

def addfilehash(name, hash, seek):
    f = xbmcvfs.File(name)
    f.seek(max(0, seek), 0)
    for i in range(8192):
        hash += struct.unpack('<q', f.read(8))[0]
        hash = hash & 0xffffffffffffffff
    f.close()    
    return hash

def normalizeString(str):
    return unicodedata.normalize(
                                 'NFKD', unicode(unicode(str, 'utf-8'))
                                 ).encode('ascii', 'ignore')
