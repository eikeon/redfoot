#!/usr/bin/env python

"""
redfoot --help
"""

import sys
# try: except: finally: in this script below require 2.5
# and I've only been testing on Python 2.5
assert sys.version_info >= (2,5,0), "redfoot requires Python 2.5 or higher"

import optparse, logging

from redfootlib import BootLoader, __version__


def main():
    parser = optparse.OptionParser(usage="""\
    usage: %prog [loader <loader_option>] [program <program_options> <program_args>]

    example: %prog loader --help
    example: %prog loader --log-level=debug program --help""")

    parser.allow_interspersed_args = False

    loader_parser = optparse.OptionParser(usage="""usage: %prog loader <loader_options>""")

    loader_parser.add_option("--program", dest="program", help="URIRef of program to load and run.")
    loader_parser.add_option("--set-default", action="store_true", dest="set_default", help="sets the current program as the default. Use with the --program option.")
    loader_parser.add_option("--clear-program", action="store_true", dest="clear_default", help="clears the default program.")
    loader_parser.add_option("--update", action="store_true", dest="update", help="Update cached version of program.")
    loader_parser.add_option("--verbose", action="store_true", dest="verbose", help="verbose logging format")
    loader_parser.add_option("--log-level", action="append", dest="log_levels", help="LOGLEVEL is specified by Logger_Name:Logger_Level where Logger_Name is optional and defaults to root logger. For example, --logger warning --logger hypercode.xmpp:debug")
    loader_parser.add_option("--version", "-V", action="store_true", dest="version", help="Shows version of redfoot command line program and exits.")
    loader_parser.add_option("--store", dest="store", help="Name of rdflib store to use (name registered with rdflib's plugin module).")
    loader_parser.add_option("--path", dest="path", help="Path to database (defaults to %default).") # TODO: add alias called configuration... as that's what it's called now
    loader_parser.add_option("--daemon", dest="daemon", action="store_true", help="Run as a daemon.")
    loader_parser.add_option("--name", action="store", type="string", dest="name", help="name to use as base for log and PID files (when running with --daemon). Defaults to %default.")
    loader_parser.add_option("--generate-key", action="store_true", dest="generate_key", help="generate a public/private key pair for Redfoot.")
    loader_parser.add_option("--passphrase", action="store_true", dest="passphrase", help="passphrase for Redfoot's public/private key.")

    loader_parser.set_defaults(program=None, set_default=False, clear_default=False,
                               update=False, verbose=False, log_levels=["INFO"], version=False, 
                               store=None, path="redfoot_boot", 
                               daemon=False, name="redfoot",
                               generate_key=False, passphrase="")

    loader_parser.allow_interspersed_args = False


    options, args = parser.parse_args()

    if len(args)>0:
        command = args[0] 
        if command=="loader":
            options, args = loader_parser.parse_args(args[1:])
            if len(args)>0:
                if args[0]=="program":
                    args = args[1:]
        elif command=="program":
            args = args[1:]
            options, _ = loader_parser.parse_args([])
        else:
            options, _ = loader_parser.parse_args([])
    else:
        options, _ = loader_parser.parse_args([])

    if options.version:
        print __version__
        from sys import exit
        exit(0)

    _logger = logging.getLogger("redfoot")
    _root_logger = logging.getLogger()
    _root_handler = logging.StreamHandler()
    if options.verbose:
        _root_handler.setFormatter(logging.Formatter('[%(levelname)s %(name)s] \n(%(pathname)s:%(lineno)d)\n%(message)s')) 
    else:
        _root_handler.setFormatter(logging.Formatter('[%(levelname)s %(name)s] %(message)s')) 

    _root_logger.addHandler(_root_handler)

    def level_from_string(s):
        try:
           log_level = int(s)
        except ValueError, ve:
            levels = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10, "NOTSET": 0}
            log_level = s.upper()
            log_level = levels.get(log_level) or logging.INFO
        return log_level

    for logger in options.log_levels:
        if ":" in logger:
            _name, _level = logger.rsplit(":", 1)
        else:
            _name, _level = None, logger
        logging.getLogger(_name).setLevel(level_from_string(_level))

    loader = BootLoader.BootLoader(store=options.store)

    from getpass import getpass
    if options.generate_key:
        from redfootlib.crypto import generate_key, use_key
        passphrase = getpass(prompt="passphrase:")
        generate_key(passphrase)
        passphrase = getpass(prompt="verify passphrase:")
        loader.crypto = use_key(passphrase)
    if options.passphrase:
        from redfootlib.crypto import use_key
        try:
            passphrase = getpass(prompt="passphrase:")
        except KeyboardInterrupt, ki:
            passphrase = ''    
        c = loader.crypto = use_key(passphrase)
        #e = c.encrypt("testing")
        #_logger.info("e: %s" % e)
        #_logger.info("??: %s" % c.decrypt(e))

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
    _formatter = logging.Formatter("""\
    [%(asctime)s %(levelname)s %(name)s]
      (%(pathname)s:%(lineno)d)
    %(message)s
    """)
    _handler.setFormatter(_formatter)
    _root_logger.addHandler(_handler)

    _error_handler = RotatingFileHandler("%s-error.log" % options.name, maxBytes=1024*1024, backupCount=5)
    _error_handler.setFormatter(_formatter)
    _error_handler.setLevel(logging.ERROR)
    _root_logger.addHandler(_error_handler)

    _warning_handler = RotatingFileHandler("%s-warning.log" % options.name, maxBytes=1024*1024, backupCount=5)
    _warning_handler.setFormatter(_formatter)
    _warning_handler.setLevel(logging.WARNING)
    _root_logger.addHandler(_warning_handler)

    _logger.info("version: %s" % __version__)



    loader.open(options.path)

    try:
        if options.clear_default:
            loader.program = None 
        program = None
        if options.program:
            program = options.program
            if options.set_default:
                loader.program = program
        else:
            program = loader.program
        if options.update:
            _logger.info("updating program: %s" % program)
            loader.load(program)
            loader.program 
            loader.commit()
        _logger.info("running: %s" % loader.label(program, default=program))
        _logger.debug("  uri: %s" % program)
        loader.execute(program or loader.program, args=args)
    except BootLoader.NoProgramException, e:
        _logger.warning("No program specified. Specify one with redfoot loader --program")
    except KeyboardInterrupt, ki:
        _logger.info("%s, Bye" % ki)
    except Exception, e:
        _logger.exception(e)
    finally:
        loader.close()
        if options.daemon:
            pid.remove_file(pid_file)

if __name__=="__main__":
    main()
