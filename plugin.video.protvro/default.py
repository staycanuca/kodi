import urllib
import urllib2
import re
import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import os
import sys


website = 'http://protvplus.ro'


settings = xbmcaddon.Addon( id = 'plugin.video.protvro' )

search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )
movies_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies.png' )
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )


def ROOT():
    addDir('Seriale','http://protvplus.ro/',23,movies_thumb,'seriale')
    addDir('Emisiuni','http://protvplus.ro/',23,movies_thumb,'emisiuni')
    addDir('Stirile ProTV','http://protvplus.ro/',23,movies_thumb,'stiri')
    addDir('Cauta','http://protvplus.ro/',3,search_thumb)

def CAUTA(url, autoSearch = None):
    keyboard = xbmc.Keyboard( '' )
    keyboard.doModal()
    if ( keyboard.isConfirmed() == False ):
        return
    search_string = keyboard.getText()
    if len( search_string ) == 0:
        return
        
    if autoSearch is None:
      autoSearch = ""
    
    parse_menu( get_search_url(search_string), 'emlink' )
    
def SXVIDEO_GENERIC_PLAY(sxurl):
  link = get_search(website+sxurl)
  match=re.compile('<meta property="og:title" content="(.+?)".+?clipSource =.+?"(.+?)"', re.IGNORECASE|re.MULTILINE|re.DOTALL).findall(link)
  if len(match) > 0:
    print match
    iconimage="DefaultVideo.png"
    item = xbmcgui.ListItem(match[0][0], iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    xbmc.Player().play(match[0][1], item)

    
def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False
    
def get_search_url(keyword, offset = None):
    #http://protvplus.ro/hledat?q=las&searchsend=Search
    url = 'http://protvplus.ro/hledat?q=' + urllib.quote_plus(keyword) + '&searchsend=Search'
    return url

def get_search(url):
    
    params = {}
    req = urllib2.Request(url, urllib.urlencode(params))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def sxaddLink(name,url,iconimage,movie_name,mode=4,descript=None):
        ok=True
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.addContextMenuItems([('Watched/Unwatched', 'Action(ToggleWatched)')])
        if descript != None:
	  liz.setInfo( type="Video", infoLabels={ "Title": movie_name,"Plot": descript } )
	else:
	  liz.setInfo( type="Video", infoLabels={ "Title": movie_name } )
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addNext(name,page,mode,iconimage, meniu = None):
    u=sys.argv[0]+"?url="+urllib.quote_plus(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    if meniu != None:
	  u += "&meniu="+urllib.quote_plus(meniu)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir(name,url,mode,iconimage,meniu = None,descript=None):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        if meniu != None:
	  u += "&meniu="+urllib.quote_plus(meniu)
	if descript != None:
	  u += "&descriere="+urllib.quote_plus(descript)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if descript != None:
	  liz.setInfo( type="Video", infoLabels={ "Title": name,"Plot": descript  } )
	else:
	  liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
      
def parse_menu(url,meniu):
    if url == None:
      url = 'http://protvplus.ro/'
    if meniu=='emisiuni' or meniu=='seriale' or meniu=='stiri':
      url = url+meniu+'/'
      link = get_search(url)
      match=re.compile('<li><a href="(.+?)".+?class="title_new">(.+?)<.+?label" >(.+?)<', re.IGNORECASE|re.MULTILINE).findall(link)
    elif meniu=='emlink':
      link = get_search(url)
      match=re.compile('<a href="(.+?)">\n\s*<span.+?\n\s*<img src=\'(.+?)\'\s*.+?\n\s*.+?\n\s*.+?\n.+?\n.+?<a href.+?>(.+?)</a>', re.IGNORECASE|re.MULTILINE).findall(link)
    if len(match) > 0:
      print match
      if meniu=='emisiuni' or meniu=='seriale' or meniu=='stiri':
	for link, nume, nrep in match:
	  image = "DefaultVideo.png"
	  url = website + link
	  addDir(nume,url,23,image,'emlink')
      elif meniu=='emlink':
	for linkem, image, name in match:
	  sxaddLink(name,linkem,image,name,10)
	  
	  
    match=re.compile('<a href="(.+?)" class="page">', re.IGNORECASE).findall(link)
    if len(match) > 0:
      page_num=re.compile('\?page=(\d+)', re.IGNORECASE).findall(url)
      if page_num:
	pagen = int(page_num[0]) + 1
	nexturl = re.sub('\?page=(\d+)', '?page=' + str(pagen), url)
      else:
	nexturl = url.rstrip('/') + '?page=2'
      #f = open( '/storage/.kodi/temp/files.py', 'w' )
      #f.write( 'match = ' + repr(nexturl) + '\n' )
      #f.close()  
      addNext('Next', nexturl, 23, next_thumb, 'emlink')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')             
params=get_params()
url=None
mode=None
meniu=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        meniu=urllib.unquote_plus(params["meniu"])
except:
        pass


#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        ROOT()
        
elif mode==3:
        CAUTA(url)
        
elif mode==23:
        parse_menu(url,meniu)

elif mode==10:
        SXVIDEO_GENERIC_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
