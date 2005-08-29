#!/usr/local/bin/python
#/usr/bin/env python
#
# ------------------------------------------------
#
#   CHANGE ABOVE OR EDIT THE "Shell Script Files"
#   PHASE TO START THE THIS SCRIPT WITH ANOTHER
#   PYTHON INTERPRETER.
#
# ------------------------------------------------
# 

"""
Distutils script for building redfoot.

Development:
    xcodebuild -buildstyle Development

Deployment:
    xcodebuild -buildstyle Deployment

These will place the executable in
the "build" dir by default.

Alternatively, you can use py2app directly.
    
Development:
    python setup.py py2app --alias
    
Deployment:
    python setup.py py2app
    
These will place the executable in
the "dist" dir by default.

"""

from distutils.core import setup
import py2app
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyObjCTools import XcodeSupport

xcode = XcodeSupport.xcodeFromEnvironment(
    'redfoot.xcode',
    os.environ,
)

sys.argv = xcode.py2app_argv(sys.argv)
setup_options = xcode.py2app_setup_options('app')

#
# mangle any distutils options you need here
# in the setup_options dict
#
setup_options["scripts"] = ["redfoot"]

STD_PACKAGES = ["bsddb","compiler","curses","distutils","email","encodings","hotshot","idlelib","logging","xml"]
STD_INCLUDES = ["BaseHTTPServer","Bastion","CGIHTTPServer","ConfigParser","Cookie","DocXMLRPCServer","HTMLParser","MimeWriter","Queue","SimpleHTTPServer","SimpleXMLRPCServer","SocketServer","StringIO","UserDict","UserList","UserString","_LWPCookieJar","_MozillaCookieJar","__future__","_strptime","_threading_local","aifc","asynchat","asyncore","atexit","audiodev","base64","bdb","binhex","bisect","calendar","cgi","cgitb","chunk","cmd","code","codecs","codeop","colorsys","commands","compileall","cookielib","copy","copy_reg","csv","dbhash","decimal","difflib","dircache","dis","doctest","dummy_thread","dummy_threading","filecmp","fileinput","fnmatch","formatter","fpformat","ftplib","getopt","getpass","gettext","glob","gopherlib","gzip","heapq","hmac","htmlentitydefs","htmllib","httplib","ihooks","imaplib","imghdr","imputil","inspect","keyword","linecache","locale","macpath","macurl2path","mailbox","mailcap","markupbase","mhlib","mimetools","mimetypes","mimify","modulefinder","multifile","mutex","netrc","new","nntplib","ntpath","nturl2path","opcode","optparse","os","os2emxpath","pdb","pickle","pickletools","pipes","pkgutil","platform","popen2","poplib","posixfile","posixpath","pprint","profile","pstats","pty","py_compile","pyclbr","pydoc","quopri","random","re","reconvert","regex_syntax","regsub","repr","rexec","rfc822","rlcompleter","robotparser","sched","sets","sgmllib","shelve","shlex","shutil","site","smtpd","smtplib","sndhdr","socket","sre","sre_compile","sre_constants","sre_parse","stat","statcache","statvfs","string","stringold","stringprep","subprocess","sunau","sunaudio","symbol","symtable","tabnanny","tarfile","telnetlib","tempfile","textwrap","this","threading","timeit","toaiff","token","tokenize","trace","traceback","tty","types","tzparse","unittest","urllib","urllib2","urlparse","user","uu","warnings","wave","weakref","webbrowser","whichdb","whrandom","xdrlib","xmllib","xmlrpclib","zipfile"]
STD_FRAMEWORKS = ["ColorPicker","MacOS","Nav","OSATerminology","_AE","_AH","_App","_CF","_CG","_CarbonEvt","_Cm","_Ctl","_Dlg","_Drag","_Evt","_File","_Fm","_Folder","_Help","_IBCarbon","_Icn","_Launch","_List","_Menu","_Mlte","_OSA","_Qd","_Qdoffs","_Qt","_Res","_Scrap","_Snd","_TE","_Win","_bisect","_bsddb","_codecs_cn","_codecs_hk","_codecs_iso2022","_codecs_jp","_codecs_kr","_codecs_tw","_csv","_curses","_curses_panel","_heapq","_hotshot","_locale","_multibytecodec","_random","_socket","_ssl","_testcapi","_tkinter","_weakref","array","audioop","autoGIL","binascii","bsddb185","bz2","cPickle","cStringIO","cmath","collections","crypt","datetime","dbm","fcntl","gestalt","grp","icglue","imageop","itertools","math","md5","mmap","nis","operator","parser","pwd","pyexpat","readline","regex","resource","rgbimg","select","sha","strop","struct","syslog","termios","time","timing","unicodedata","waste","zlib"]

setup_options["options"] = dict(
    py2app=dict(
        iconfile='redfoot.icns',
	packages = ["redfootlib", "rdflib","twisted","kid"] + STD_PACKAGES,
	includes = ["redfootAppDelegate",] + STD_INCLUDES,
	frameworks = STD_FRAMEWORKS,
))

setup(**setup_options)


