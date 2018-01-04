# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', ''))

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
            listitem = xbmcgui.ListItem(label=item_data["LanguageName"],
                                        label2=item_data["SubFileName"],
                                        iconImage=item_data["SubRating"],
                                        thumbnailImage=item_data["ISO639"]
                                        )

            listitem.setProperty("sync", ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"])
            listitem.setProperty("hearing_imp", ("false", "true")[int(item_data["SubHearingImpaired"]) != 0])
            url = "plugin://%s/?action=download&link=%s&filename=%s&format=%s&traducator=%s" % (__scriptid__,
                                                                                                item_data["ZipDownloadLink"],
                                                                                                item_data["SubFileName"],
                                                                                                item_data["referer"],
                                                                                                item_data["Traducator"]
                                                                                                )
            #f = open( '/storage/.kodi/temp/files2.py', 'w' )
            #f.write( 'url = ' + repr(url) + '\n' )
            #f.close()
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)


def Download(link, url, referer, trdtr):
    subtitle_list = []
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
    log(__name__, "Download Using HTTP")
    s = requests.Session()
    ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    headers = {'User-Agent': ua}
    referer = 'http://www.titrari.ro/index.php?page=cautare&z1=0&z2=' + referer + '&z3=1&z4=1'
    s.headers.update({'referer': referer})
    link = 'http://www.titrari.ro/get.php?id=' + link
    file = s.get(link, headers=headers)
    contentType = file.headers['Content-Disposition'].split(';')
    Type = 'rar' if contentType[1][-5:] == '.rar"' else 'zip'
    fname = "%s.%s" % (os.path.join(__temp__, "subtitle"), Type)
    with open(fname, 'wb') as f: f.write(file.content)
    extractPath = os.path.join(__temp__, "Extracted")
    xbmc.executebuiltin("XBMC.Extract(%s, %s)" % (fname, extractPath))
    xbmc.sleep(1000)
    for root, dirs, files in os.walk(extractPath):
        for file in files:
            dirfile = os.path.join(root, file)
            dirfile_with_path_name = normalizeString(os.path.relpath(dirfile, extractPath))
            dirname, basename = os.path.split(dirfile_with_path_name)
            dirname = re.sub(r"[/\\]{1,10}", "-", dirname)
            dirfile_with_path_name = "(%s) %s" % (dirname, basename) if len(dirname) else basename
            #new_dirfile = os.path.join(extractPath, safeFilename(dirfile_with_path_name))
            if (os.path.splitext(file)[1] in exts):
                #extension = file[file.rfind('.') + 1:]
                subtitle_list.append(dirfile)
                #index += 1 
    selected = []
    #f = open( '/storage/.kodi/temp/files2.py', 'w' )
    #f.write( 'url = ' + repr(contentType) + '\n' )
    #f.close()
    if xbmcvfs.exists(subtitle_list[0]):
        subtitle_list_s = natcasesort(subtitle_list)
        dialog = xbmcgui.Dialog()
        sel = dialog.select("%s\n%s" % ('Traducator: ', trdtr),
                            [os.path.basename(x) for x in subtitle_list_s])
        if sel >= 0:
            selected.append(subtitle_list_s[sel])
            return selected
	else:
            return None
    else:
        return None
  
def safeFilename(filename):
    keepcharacters = (' ', '.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

def natcasesort(arr):
    if isinstance(arr, list):
        arr = sorted(arr, key=lambda x:str(x).lower())
    elif isinstance(arr, dict):
        arr = sorted(arr.iteritems(), key=lambda x:str(x[0]).lower())
    return arr

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
    subs = Download(params["link"], params["link"], params["format"], params["traducator"])
    if subs is not None:
        for sub in subs:
            listitem = xbmcgui.ListItem(label=sub)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
