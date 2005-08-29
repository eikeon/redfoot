#!/usr/bin/env python
"""
redfoot.py is a command line interface to redfoot.

For help on redfoot see:

   redfoot.py --help
"""

import sys, logging, traceback
from optparse import OptionParser
from redfootlib import __version__
from redfootlib.install_rdflib import install_rdflib


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(message)s')

logging.info("redfoot version: %s" % __version__)

usage = "usage: %prog [options] [args]"
parser = OptionParser(usage=usage)
# where to doc what program_uri "program url"    
parser.allow_interspersed_args = False
parser.add_option("--install-rdflib", dest="install_rdflib", action="store_true", help="download and install latest stable rdflib or version specified by URL")
parser.add_option("--update", action="store_true", dest="update", help="update program")    
parser.add_option("--quiet", action="store_true", dest="quiet", help="")    
parser.add_option("--program", dest="program", help="name of program program to load and run")
parser.add_option("--program-args", dest="program_args", help="arguments for program program")
parser.add_option("--set-default", action="store_true", dest="set_default", help="sets the current program as the default")
parser.add_option("--clear-default", action="store_true", dest="clear_default", help="clears the current default program")
parser.add_option("--backend", dest="backend", help="name of rdflib Graph backend to use")
parser.add_option("--path", dest="path", help="path to database")

parser.set_defaults(path="__rfdb__", program = None, update=False, quiet=False, backend=None, install_rdflib=False, set_default=False, clear_default=False)


def main(command=None):
    if command is None:
	options, args = parser.parse_args()	
    else:
	args = command.split()
	options, args = parser.parse_args(args)
    if options.install_rdflib:
	install_rdflib(args)
    else:
	from redfootlib.BootLoader import BootLoader
	loader = BootLoader(backend=options.backend)
	try:
	    loader.open(options.path)
	    loader.main(options, args)
	finally:
	    loader.close()
	return loader

if __name__=="__main__":
    main()
