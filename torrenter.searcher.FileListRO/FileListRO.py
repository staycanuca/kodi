# -*- coding: utf-8 -*-
'''
    Torrenter v2 plugin for XBMC/Kodi
    Copyright (C) 2012-2015 Vadim Skorba v1 - DiMartino v2
    http://forum.kodi.tv/showthread.php?tid=214366

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import SearcherABC
import os
import re
import socket
import sys
import urllib
import xbmcaddon


class FileListRO(SearcherABC.SearcherABC):

    __torrenter_settings__ = xbmcaddon.Addon(id='plugin.video.torrenter')
    #__torrenter_language__ = __settings__.getLocalizedString
    #__torrenter_root__ = __torrenter_settings__.getAddonInfo('path')

    ROOT_PATH = os.path.dirname(__file__)
    addon_id = ROOT_PATH.replace('\\', '/').rstrip('/').split('/')[-1]
    __settings__ = xbmcaddon.Addon(id=addon_id)
    __addonpath__ = __settings__.getAddonInfo('path')
    __version__ = __settings__.getAddonInfo('version')
    __plugin__ = __settings__.getAddonInfo('name') + " v." + __version__

    username = __settings__.getSetting("username")
    password = __settings__.getSetting("password")
    baseurl = 'filelist.ro'

    '''
    Setting the timeout
    '''
    torrenter_timeout_multi = int(sys.modules["__main__"].__settings__.getSetting("timeout"))
    timeout_multi = int(__settings__.getSetting("timeout"))

    '''
    Weight of source with this searcher provided. Will be multiplied on default weight.
    '''
    sourceWeight = 1

    '''
    Full path to image will shown as source image at result listing
    '''
    searchIcon = os.path.join(__addonpath__, 'icon.png')

    '''
    Flag indicates is this source - magnet links source or not.
    '''

    @property
    def isMagnetLinkSource(self):
        return False

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        int(leechers),# Leechers count
        str(size),# Full torrent's content size (e.g. 3.04 GB)
        str(title),# Title (will be shown)
        str(link),# Link to the torrent/magnet
        str(image),# Path to image shown at the list
    ))
    '''

    headers = [('Origin', 'http://' + baseurl),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
        ('Referer', 'http://' + baseurl + '/'), ('X-Requested-With', 'XMLHttpRequest')]

    def __init__(self):
        self.logout()

        if self.timeout_multi == 0:
            socket.setdefaulttimeout(10 + (10 * self.torrenter_timeout_multi))
        else:
            socket.setdefaulttimeout(10 + (10 * (self.timeout_multi-1)))

        if self.__settings__.getSetting("usemirror") == 'true':
            self.baseurl = self.__settings__.getSetting("baseurl")

        #self.debug = self.log

    def logout(self):
        old_username = self.__settings__.getSetting("old_username")
        if old_username in [None, ''] or old_username != self.username:
            self.__settings__.setSetting("old_username", self.username)
            self.clear_cookie(self.baseurl)
        self.login()

    def search(self, keyword):
        filesList = []
        url = 'http://%s/browse.php?search=%s' % (self.baseurl, urllib.quote_plus(keyword))
        if self.__settings__.getSetting('sortby') == '0' or \
	    self.__settings__.getSetting('sortby') == xbmcaddon.Addon().getLocalizedString(30031):
            url += '&cat=0&searchin=0&sort=5' 
	elif self.__settings__.getSetting('sortby') == xbmcaddon.Addon().getLocalizedString(30032):
            url += '&cat=0&searchin=0&sort=2'
	elif self.__settings__.getSetting('sortby') == xbmcaddon.Addon().getLocalizedString(30033):
            url += '&cat=0&searchin=0&sort=0'
        response = self.makeRequest(url, headers=self.headers)
        if None != response and 0 < len(response):
            self.debug(response)
            regex = '''<div class=\\'torrentrow\\'>(.+?)</div></div>'''
            regex_tr = '''title=\\'(.+?)\\'.+?<a href="(.+?)".+?<font class=\\'small\\'>(\d+\.\d+)<.+?#\d+>(\d+)<.+?(<b>|;\\'>)(\d+)<'''
            for tr in re.compile(regex, re.DOTALL).findall(response):
	        if re.compile('<title> FileList :: Login </title>').search(response):
                    xbmc.executebuiltin((u'Notification(%s,%s)' % ('FileList.ro', 'lipsa username si parola din setari')))
                result = re.compile(regex_tr, re.DOTALL).findall(tr)
                self.debug(tr + ' -> ' + str(result))
                if result:
                    (title, link, size, seeds, nothing, leechers) = result[0]
                    title = self.clear_title(title)
                    link = 'http://%s/%s' % (self.baseurl, link)
                    filesList.append((
                                     int(int(self.sourceWeight) * int(seeds)),
                                     int(seeds), int(leechers), size,
                                     title,
                                     self.__class__.__name__ + '::' + link,
                                     self.searchIcon,
                                     ))
        #f = open( '/storage/.kodi/temp/files12.py', 'w' )
        #f.write( 'url = ' + repr(response) + '\n' )
        #f.close()
        return filesList

    def clear_title(self, s):
        return self.stripHtml(self.unescape(s)).replace('   ', ' ').replace('  ', ' ').strip()

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            self.debug(response)
            if re.compile('<input type=\'password\'').search(response) or \
                re.compile('<title> FileList :: Login </title>').search(response):
                self.log('FileListRO Not logged!')
                self.login()
                return False
        return True

    def getTorrentFile(self, url):
        content = self.makeRequest(url, headers=self.headers)
        if not self.check_login(content):
            content = self.makeRequest(url, headers=self.headers)
        if re.search("<html", content):
            msg = re.search('User sau parola gresite', content)
            if msg:
                self.showMessage('FileListRO Login Error', 'Incorrent pair login/password')
            xbmc.sleep(4000)
            self.debug('getTorrentFile: ' + content)
            sys.exit(1)
        return self.saveTorrentFile(url, content)

    def login(self):
        data = {
            'password': self.password,
            'username': self.username
        }
        x = self.makeRequest(
                             'http://%s/takelogin.php' % (self.baseurl), data=data, headers=self.headers)
        if re.search('{"status":"OK"', x):
            self.log('LOGGED FileListRO')
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            if cookie.name == 'fl' and cookie.domain == self.baseurl:
                return 'fl=' + cookie.value
        return False
