import sys, types, logging

_logger = logging.getLogger(__name__)

from rdflib import RDF, URIRef, Namespace
from rdflib.Graph import Graph, ConjunctiveGraph

BOOT = Namespace("http://redfoot.net/3.0/boot#")
CODE = Namespace("http://redfoot.net/3.0/code#")


class NoProgramException(Exception):
    pass


class BootLoader(ConjunctiveGraph):
    """
    Responsible for loading and running the program specified by a
    URIRef. If no program is specified a default is obtained from
    BOOT.
    """

    def __init__(self, store=None):
        super(BootLoader, self).__init__(store=store or "Sleepycat")
        self.__config = None
        self.__crypto = None

    def __set_program(self, program):
        self.remove((BOOT.Globals, BOOT.program, None))
        if program:
            program = self.absolutize(program, defrag=0)
            self.config.add((BOOT.Globals, BOOT.program, program))
        self.commit()

    def __get_program(self):
        program = self.value(BOOT.Globals, BOOT.program)
        if not program:
            _logger.info("No program found in BOOT.Globals")
            if not (BOOT, None, None) in self:
                _logger.info("loading: %s" % BOOT)
                self.load(BOOT)
                self.commit()
            program = self.value(BOOT.Defaults, BOOT.program)
            if program:
                _logger.info("Found program: %s" % program)
            else:
                _logger.info("No program found in BOOT.Defaults")
                raise NoProgramException()
        return program
    program = property(__get_program, __set_program, doc="python program redfoot.py will load and execute")

    def __get_config(self):
        if self.__config is None:
            uri = URIRef("_config", base=BOOT)
            self.__config = Graph(store=self.store, identifier=uri)
        return self.__config
    config = property(__get_config, doc="context for storing configuration data")

    def open(self, path):
        _logger.debug("opening with store=%s and configuration=%s" % (self.store, path))
        super(BootLoader, self).open(path, create=True)

    def close(self):
        _logger.debug("closing store.")
        super(BootLoader, self).close()

    def check(self, uri):
        if (uri, None, None) not in self:
            try:
                self.parse(uri)
            except Exception, e:
                _logger.warning("couldn't parse %s: %s" % (uri, e))

    def execute(self, uri, context=None, **keyword_args):
        if uri is not None:
            uri = self.absolutize(uri, defrag=0)
            self.check(uri)
            _logger.info("execute: %s" % self.label(uri))
            _logger.debug("  uri: %s" % uri)
            value = self.value(uri, CODE.python)
            if value:
                value = value.replace("\r\n", "\n")        
                value = value.replace("\r", "\n")        
                value += "\n"
            else:
                raise ValueError("No CODE.python found for: %s" % uri)
            context = context or {"redfoot_loader": self, "__uri__": uri}
            for k, v in keyword_args.items():
                context[k] = v
            c = compile(value, uri, "exec")
            exec c in context
            return context
        else:
            raise Exception("Couldn't execute %s (nothing known about resource)" % uri)

    def module(self, uri):
        self.check(uri)
        module_name = uri       
        _logger.debug("creating module: %s" % uri)
        safe_module_name = "__uri___%s" % hash(uri)
        module = types.ModuleType(safe_module_name)
        module.__name__ = module_name 
        module.__file__ = uri
        module.__ispkg__ = 0
        sys.modules[module_name] = module
        module.__dict__.update({"redfoot_loader": self, "__uri__": uri})
        self.execute(uri, context=module.__dict__)

        return module

    def _get_crypto(self):
        if self.__crypto is None:
            _logger.warning("No Crypto Support... flying in the clear!")
            class Crypto(object):
                def encrypt(self, value):
                    return value
                def decrypt(self, value):
                    return value
            self.__crypto = Crypto()
        return self.__crypto

    def _set_crypto(self, crypto):
        if self.__crypto is None:
            self.__crypto = crypto
        else:
            raise Exception("Crypto already set") # TODO: what's the right exception

    crypto = property(_get_crypto, _set_crypto, doc="object with crypto methods")
  
