import sys, logging, traceback

logger = logging.getLogger("redfoot")

def show_install_message(msg): # TODO:
    logger.critical(msg)
    logger.critical("""Try the --install-rdflib option or""")
    logger.critical("""See http://rdflib.net/ for information on downloading and installing rdflib.""")
    sys.exit(-1)

try:
    import rdflib
except ImportError, e:
    show_install_message("rdflib not found: %s" % e)
else:
    version = tuple([int(x) for x in rdflib.__version__.split(".", 2)])    
    REQUIRED = (2, 3, 1)
    if version < REQUIRED:
        show_install_message("rdflib %s or greater required. Found rdflib version %s" % ("%s.%s.%s" % REQUIRED, rdflib.__version__))        

from rdflib import RDF, RDFS, URIRef, BNode, Namespace
from rdflib.Graph import Graph, ConjunctiveGraph

REDFOOT = Namespace("http://redfoot.net/2005/redfoot#")
REDFOOT.Globals = REDFOOT["Globals"]
REDFOOT.Defaults = REDFOOT["Defaults"]
REDFOOT.program = REDFOOT["program"]


class BootLoader(ConjunctiveGraph):
    """
    Responsible for loading and running the program specified by a
    URIRef. If no program is specified a default is obtained from
    REDFOOT.
    """

    def __init__(self, store=None):
        super(BootLoader, self).__init__(store=store or "Sleepycat")
        self.__config = None

    def __set_program(self, program):
        self.remove((REDFOOT.Globals, REDFOOT.program, None))
        if program:
            self.config.add((REDFOOT.Globals, REDFOOT.program, program))
        self.commit()

    def __get_program(self):
        program = self.value(REDFOOT.Globals, REDFOOT.program)
        if not program:
            if self.update or not (REDFOOT, None, None) in self:
                logger.info("loading: %s" % REDFOOT)
                self.load(REDFOOT)
                self.commit()
            program = self.value(REDFOOT.Defaults, REDFOOT.program)
            assert program, "No default program found"            
        return program
    program = property(__get_program, __set_program, doc="python program redfoot.py will load and execute")

    def __get_config(self):
        config = self.__config
        if config is None:
           config =  self.__config = Graph(store=self.store, identifier=BNode("_config"))
        return config
    config = property(__get_config, doc="context for storing configuration data")

    def open(self, path):
        super(BootLoader, self).open(path, create=True)

    def main(self, options, args):
        self.update = update = options.update
        if options.clear_default:
            self.program = None                 
        program = None
        if options.program:
            program = URIRef(self.absolutize(options.program, defrag=0))
        program = program or self.program
        if options.set_default:
            self.program = program
        if update or not (program, RDF.value, None) in self:
            logger.info("loading: %s" % program)
            self.load(program)
            self.commit()
    
        logger.info("running: %s ( %s )" % (self.label(program, ''), program))

        value = self.value(program, RDF.value)
        assert value, "No RDF.value found for: %s" % program
        assert value.datatype==REDFOOT.Python, "%s RDF.value is not of datatype REDFOOT.Python. This version of redfoot only supports REDFOOT.Python code values" % program
    
        program_options = options.program_options
        if program_options:
            args = [program_options,] + args
        try:
            c = compile(value+"\n", program, "exec")
            exec c in dict({"redfoot_loader": self, "args": args, "redfoot_program": program})
        except Exception, e:
            tb = sys.exc_traceback
            tb = tb.tb_next
            logger.error(traceback.print_exception(sys.exc_type, sys.exc_value, tb))
