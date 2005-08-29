import logging, sys, os

from subprocess import Popen
from tarfile import TarFile
from urllib2 import urlopen, Request
from StringIO import StringIO

from redfootlib import __version__


def install_rdflib(args):
    if len(args)==0:
	url = "http://rdflib.net/rdflib-stable.tgz"
    elif len(args)==1:
	url = args[0]
	if url=="latest" or url=="dev":
	    url = "http://rdflib.net/rdflib.tgz"
    else:
	logging.critical("usage: <URL_to_rdflib_version> # defaults to latest stable version")
	return

    logging.info("downloading rdflib")

    headers = {'User-agent': 'redfootlib (%s)' % __version__}
    f = urlopen(Request(url, None, headers))
    sio = StringIO(f.read())
    sio.seek(0)
    tar = TarFile.gzopen("rdflib.tgz", fileobj=sio)

    logging.info("extracting rdflib")
    for member in tar:
	if member.name.endswith("setup.py"):
	    setup = member.name
	tar.extract(member)
    dir, file = os.path.split(setup)
    os.chdir(dir)

    logging.info("installing rdflib")
    p = Popen([sys.executable, "setup.py", "install"])
    p.wait()
    if "rdflib" in sys.modules:
	del sys.modules["rdflib"]
    try:
	import rdflib
	logging.info("rdflib %s installed" % rdflib.__version__)
    except ImportError, e:
	logging.info("rdflib not installed: %s" % e)    

