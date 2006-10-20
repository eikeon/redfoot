#!/usr/bin/env python
"""
redfoot.py is a command line interface to redfoot.

For help on redfoot see:

   redfoot.py --help
"""

import optparse, logging

parser = optparse.OptionParser(usage="""usage: %prog [<%prog_options>] [program [<program_options>]][<program_args>]
example: %prog --update program --help""")

parser.allow_interspersed_args = False

parser.add_option("--program", dest="program", help="URIRef of program to load and run. Defaults to program specified in http://redfoot.net/2005/redfoot#Defaults")
parser.add_option("--set-default", action="store_true", dest="set_default", help="sets the current program as the default. Use with --program when also wanting to make the program the future default program.")
parser.add_option("--clear-default", action="store_true", dest="clear_default", help="clears the current default program")
parser.add_option("--update", action="store_true", dest="update", help="update cached version of program")    
parser.add_option("--verbose", "-v", action="store_true", dest="verbose", help="verbose logging of messages")    
parser.add_option("--log-level", action="store", type="int", dest="log_level", help="numeric logger level (see Python's logging module for numeric values of the standard logging levels)")
parser.add_option("--version", action="store_true", dest="version", help="Shows version of redfoot command line program and exits")    
parser.add_option("--store", dest="store", help="name of rdflib store to use (name registered with rdflib's plugin module)")
parser.add_option("--path", dest="path", help="path to database (defaults to __rfboot__)") # TODO: add alias called configuration... as that's what it's called now
parser.add_option("--daemon", dest="daemon", action="store_true", help="run as a daemon")
parser.add_option("--name", action="store", type="string", dest="name", help="name to use as base for log and PID files (when running with --daemon)")
parser.add_option("--install-rdflib", dest="install_rdflib", action="store_true", help="download and install latest stable rdflib or version specified by URL or dev (for latest development version)")

parser.set_defaults(path="__rfboot__", program = None, update=False, verbose=False, version=False, store=None, install_rdflib=False, set_default=False, clear_default=False, daemon=False, log_level=logging.WARNING, name="redfoot")


def main(command=None):
    if command is None:
        options, args = parser.parse_args() 
    else:
        args = command.split()
        options, args = parser.parse_args(args)

    _logger = logging.getLogger("redfoot")

    _root_logger = logging.getLogger()
    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = options.log_level
    _root_logger.setLevel(log_level)
    _root_formatter = logging.Formatter('[%(name)s] %(message)s')
    _root_handler = logging.StreamHandler()
    _root_handler.setLevel(log_level)
    _root_handler.setFormatter(_root_formatter)
    _root_logger.addHandler(_root_handler)

    if options.version:
        from redfootlib import __version__
        print __version__
        from sys import exit
        exit(0)

    if options.daemon:
        _logger.debug("daemonizing")
        from redfootlib.daemonize import daemonize
        from redfootlib import pid
        pid_file = "%s.pid" % options.name
        pid.check_file(pid_file)
        daemonize()
        pid.add_file(pid_file)
        _root_logger.removeHandler(_root_handler)

    from logging.handlers import RotatingFileHandler
    _handler = RotatingFileHandler("%s.log" % options.name, maxBytes=1024*1024, backupCount=5)
    _formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s %(pathname)s %(lineno)d] %(message)s')
    _handler.setFormatter(_formatter)
    _root_logger.addHandler(_handler)

    if options.install_rdflib:
        from redfootlib.install_rdflib import install_rdflib
        install_rdflib(args)
    else:
        from redfootlib import __version__
        _logger.info("version: %s" % __version__)
        from redfootlib.BootLoader import BootLoader
        loader = BootLoader(store=options.store)
        _logger.info("opening with store=%s and configuration=%s" % (options.store, options.path))
        loader.open(options.path)
        try:
            if len(args)>0 and args[0]=="program":
                args = args[1:]
            loader.main(options, args)
        finally:
            _logger.info("closing store=%s with configuration=%s" % (options.store, options.path))
            loader.close()
        if options.daemon:
            pid.remove_file(pid_file)

if __name__=="__main__":
    main()
