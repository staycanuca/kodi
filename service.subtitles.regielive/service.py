# -*- coding: utf-8 -*-

from cStringIO import StringIO
import os
import re
import shutil
import sys
import urllib
import uuid
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from zipfile import ZipFile



__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', '')).decode("utf-8")

if xbmcvfs.exists(__temp__):
    shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

sys.path.append (__resource__)

from OSUtilities import OSDBServer, log, normalizeString
import requests

def Search(item):
    search_data = []
    try:
        search_data = OSDBServer().searchsubtitles(item)
    except:
        log(__name__, "failed to connect to service for subtitle search")
        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32001))).encode('utf-8'))
        return
    if search_data != None:
        for item_data in search_data:
            #f = open( '/storage/.kodi/temp/files2.py', 'w' )
            #f.write( 'url = ' + repr(item_data['SeriesSeason']) + '\n' )
            #f.close()
            if ((item['season'] == item_data['SeriesSeason'] and
                item['episode'] == item_data['SeriesEpisode']) or
                (item['season'] == "" and item['episode'] == "") ## for file search, season and episode == ""
                ):
                listitem = xbmcgui.ListItem(label=item_data["LanguageName"],
                                            label2=item_data["SubFileName"],
                                            iconImage=item_data["SubRating"],
                                            thumbnailImage=item_data["ISO639"]
                                            )

                listitem.setProperty("sync", ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"])
                listitem.setProperty("hearing_imp", ("false", "true")[int(item_data["SubHearingImpaired"]) != 0])
                url = "plugin://%s/?action=download&link=%s&filename=%s&format=%s" % (__scriptid__,
                                                                                      item_data["ZipDownloadLink"],
                                                                                      item_data["SubFileName"],
                                                                                      item_data["SubFormat"]
                                                                                      )

                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)


def Download(link, url, format, stack=False):
    url = re.sub('download', 'descarca', url)
    url = re.sub('html', 'zip', url)
    subtitle_list = []
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
    log(__name__, "Download Using HTTP")
    s = requests.Session()
    ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    headers = {'User-Agent': ua}
    if ((__addon__.getSetting("OSuser") and
        __addon__.getSetting("OSpass"))):
        payload = {'l_username':__addon__.getSetting("OSuser"), 'l_password':__addon__.getSetting("OSpass")}
        s.post('http://www.regielive.ro/membri/login.html', data=payload, headers=headers)
    else:
        s.post('http://www.regielive.ro', headers=headers)
    f = s.get(url, headers=headers)
    try:
        archive = ZipFile(StringIO(f.content), 'r')
    except:
        return subtitle_list
    files = archive.namelist()
    files.sort()
    index = 1
    for file in files:
        contents = archive.read(file)
        if (os.path.splitext(file)[1] in exts):
            extension = file[file.rfind('.') + 1:]
            if len(files) == 1:
                dest = os.path.join(__temp__, "%s.%s" % (str(uuid.uuid4()), extension))
            else:
                dest = os.path.join(__temp__, "%s.%d.%s" % (str(uuid.uuid4()), index, extension))
            f = open(dest, 'wb')
            f.write(contents)
            f.close()
            subtitle_list.append(dest)
            index += 1
    if xbmcvfs.exists(subtitle_list[0]):
        return subtitle_list

def get_params(string=""):
    param = []
    if string == "":
        paramstring = sys.argv[2]
    else:
        paramstring = string
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
    log(__name__, "action '%s' called" % params['action'])
    item = {}
    item['temp']               = False
    item['rar']                = False
    item['mansearch']          = False
    item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
    item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
    item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
    item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
    item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
    item['file_original_path'] = xbmc.Player().getPlayingFile().decode('utf-8')                 # Full path of a playing file
    item['3let_language']      = [] #['scc','eng']

    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        if lang == "Portuguese (Brazil)":
            lan = "pob"
        elif lang == "Greek":
            lan = "ell"
        else:
            lan = xbmc.convertLanguage(lang, xbmc.ISO_639_2)

        item['3let_language'].append(lan)

    if item['title'] == "":
        log(__name__, "VideoPlayer.OriginalTitle not found")
        item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

    if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
        item['season'] = "0"                                                          #
        item['episode'] = item['episode'][-1:]

    if (item['file_original_path'].find("http") > -1):
        item['temp'] = True

    elif (item['file_original_path'].find("rar://") > -1):
        item['rar']  = True
        item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

    elif (item['file_original_path'].find("stack://") > -1):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    Search(item)

elif params['action'] == 'download':
    subs = Download(params["link"], params["link"], params["format"])
    #f = open( '/storage/.kodi/temp/files2.py', 'w' )
    #f.write( 'url = ' + repr(subs) + '\n' )
    #f.close()
    for sub in subs:
        listitem = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
