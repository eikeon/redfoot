import logging, sys, os

from subprocess import Popen
from tarfile import TarFile
from urllib2 import urlopen, Request
from StringIO import StringIO

from redfootlib import __version__

_logger = logging.getLogger("redfoot.install_rdflib")

def install_rdflib(args=[]):
    if len(args)==0:
	url = "http://rdflib.net/rdflib-stable.tgz"
    elif len(args)==1:
	url = args[0]
	if url=="latest" or url=="dev":
	    url = "http://rdflib.net/rdflib.tgz"
    else:
	_logger.critical("usage: <URL_to_rdflib_version> # defaults to latest stable version")
	return

    _logger.info("downloading rdflib")

    headers = {'User-agent': 'redfootlib (%s)' % __version__}
    f = urlopen(Request(url, None, headers))
    sio = StringIO(f.read())
    sio.seek(0)
    tar = TarFile.gzopen("rdflib.tgz", fileobj=sio)

    _logger.info("extracting rdflib")
    for member in tar:
	if member.name.endswith("setup.py"):
	    setup = member.name
	tar.extract(member)

    log_file = file("redfoot-install-rdflib-log", "w")

    dir, file_name = os.path.split(setup)
    os.chdir(dir)

    _logger.info("installing rdflib")
    _logger.info("writing redoot-install-rdflib-log")

    try:
        p = Popen([sys.executable, "setup.py", "install"], stdout=log_file, stderr=log_file)
        p.wait()
    except Exception, e:
        _logger.error("Could not install rdflib: %s" % e)
        sys.exit(-1)
    log_file.close()

    if "rdflib" in sys.modules:
	del sys.modules["rdflib"]
    try:
	import rdflib
	_logger.info("rdflib %s installed" % rdflib.__version__)
    except ImportError, e:
	_logger.info("rdflib not installed: %s" % e)    

