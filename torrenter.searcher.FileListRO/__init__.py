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

import xbmc, os


ROOT_PATH = os.path.dirname(__file__)
addon_id = ROOT_PATH.replace('\\','/').rstrip('/').split('/')[-1]
searcher_name = addon_id.replace('torrenter.searcher.','')

exec_str = 'XBMC.ActivateWindow(%s)' % \
           ('%s?action=%s&external=%s&from_searcher=True') % \
           ('Videos,plugin://plugin.video.torrenter/', 'search', searcher_name)
xbmc.executebuiltin(exec_str)