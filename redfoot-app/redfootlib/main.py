#!/usr/bin/env python
"""
redfoot.py is a command line interface to redfoot.

For help on redfoot see:

   redfoot.py --help
"""

import optparse, logging

parser = optparse.OptionParser(usage="usage: %prog [options] [args]")

parser.allow_interspersed_args = False

parser.add_option("--install-rdflib", dest="install_rdflib", action="store_true", help="download and install latest stable rdflib or version specified by URL")
parser.add_option("--update", action="store_true", dest="update", help="update program")    
parser.add_option("--quiet", action="store_true", dest="quiet", help="")    
parser.add_option("--program", dest="program", help="URIRef of program to load and run")
parser.add_option("--program-args", dest="program_args", help="arguments for program program")
parser.add_option("--set-default", action="store_true", dest="set_default", help="sets the current program as the default")
parser.add_option("--clear-default", action="store_true", dest="clear_default", help="clears the current default program")
parser.add_option("--store", dest="store", help="name of rdflib store to use")
parser.add_option("--path", dest="path", help="path to database")
parser.add_option("--daemon", dest="daemon", action="store_true", help="run as a daemon")
parser.add_option("--log-level", action="store", type="int", dest="log_level", help="logger level")
parser.add_option("--name", action="store", type="string", dest="name", help="name to use as base for log and PID files")

parser.set_defaults(path="__rfdb__", program = None, update=False, quiet=False, store=None, install_rdflib=False, set_default=False, clear_default=False, daemon=False, log_level=logging.DEBUG, name="redfoot")


def main(command=None):
    if command is None:
        options, args = parser.parse_args() 
    else:
        args = command.split()
        options, args = parser.parse_args(args)

    _logger = logging.getLogger("redfoot")
    _logger.setLevel(options.log_level)
    _formatter = logging.Formatter('%(message)s')
    _handler = logging.StreamHandler()
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)

    if options.daemon:
        _logger.debug("daemonizing")
        from redfootlib.daemonize import daemonize
        from redfootlib import pid
        pid_file = "%s.pid" % options.name
        pid.check_file(pid_file)
        daemonize()
        pid.add_file(pid_file)
        _logger.removeHandler(_handler)

    from logging.handlers import RotatingFileHandler
    _handler = RotatingFileHandler("%s.log" % options.name, maxBytes=1024*1024, backupCount=5)
    _formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(pathname)s %(lineno)d\n%(message)s')
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)

    if options.install_rdflib:
        from redfootlib.install_rdflib import install_rdflib
        install_rdflib(args)
    else:
        from redfootlib import __version__
        _logger.info("redfoot version: %s" % __version__)
        from redfootlib.BootLoader import BootLoader
        loader = BootLoader(store=options.store)
        _logger.info("opening with store=%s and configuration=%s" % (options.store, options.path))
        loader.open(options.path)
        try:
            loader.main(options, args)
        finally:
            loader.close()
        if options.daemon:
            pid.remove_file(pid_file)

if __name__=="__main__":
    main()
