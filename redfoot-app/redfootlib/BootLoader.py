import sys, logging, traceback

def show_install_message(msg): # TODO:
    logging.critical(msg)
    logging.critical("""Try the --install-rdflib option or""")
    logging.critical("""See http://rdflib.net/ for information on downloading and installing rdflib.""")
    sys.exit(-1)

try:
    import rdflib
except:
    show_install_message("rdflib not found")
else:
    version = tuple([int(x) for x in rdflib.__version__.split(".", 2)])    
    REQUIRED = (2, 1, 0)
    if version < REQUIRED:
	show_install_message("rdflib %s or greater required. Found rdflib version %s" % ("%s.%s.%s" % REQUIRED, rdflib.__version__))        

logging.info("rdflib version: %s" % rdflib.__version__)

from rdflib import RDF, RDFS, Graph, URIRef, BNode, Namespace

REDFOOT = Namespace("http://redfoot.net/2005/redfoot#")
REDFOOT.Globals = REDFOOT["Globals"]
REDFOOT.Defaults = REDFOOT["Defaults"]
REDFOOT.program = REDFOOT["program"]



class BootLoader(Graph):

    def __init__(self, backend=None):
	super(BootLoader, self).__init__(backend=backend or "Sleepycat")
	self.__log = None        
	self.__config = None

    def __get_log(self):
	if self.__log is None:
	    self.__log = logging
	return self.__log
    log = property(__get_log, doc="log facility")

    def __set_program(self, program):
	self.config.remove((REDFOOT.Globals, REDFOOT.program, None))
	if program:
	    self.config.add((REDFOOT.Globals, REDFOOT.program, program))

    def __get_program(self):
	program = self.value(REDFOOT.Globals, REDFOOT.program)
	if not program:
	    program = self.value(REDFOOT.Defaults, REDFOOT.program)
	    assert program, "No default program found"            
	return program
    program = property(__get_program, __set_program, doc="python program redfoot.py will load and execute")

    def __get_config(self):
	config = self.__config
	if config is None:
	   config =  self.__config = self.get_context(BNode("_config"))
	return config
    config = property(__get_config, doc="context for storing configuration data")

    def open(self, path):
	super(BootLoader, self).open(path)

    def main(self, options, args):
	if options.quiet:
	    logging.getLogger().setLevel(logging.WARNING)

	update = options.update
	if options.clear_default:
	    self.program = None                 
	if update or not (REDFOOT, None, None) in self:
	    self.log.info("loading: %s" % REDFOOT)
	    self.load(REDFOOT)
	program = None
	if options.program:
	    if ":" in options.program and "://" not in options.program:
		prefix, name = options.program.split(":", 1)
		if prefix=="":
		    program = URIRef(REDFOOT + options.program[1:])
		else:
		    namespace = dict(self.namespaces()).get(prefix, None)
		    if namespace is None:
			self.log.warning("no known namespace for '%s'.")
			namespace = REDFOOT
		    program = URIRef(namespace + name)
	    else:
		program = URIRef(self.absolutize(options.program, defrag=0))
	program = program or self.program
	if options.set_default:
	    self.program = program
	if update or not (program, RDF.value, None) in self:
	    self.log.info("loading: %s" % program)
	    self.load(program)

        self.log.info("running: %s ( %s )" % (self.label(program, ''), program))

        # assert program is of type REDFOOT.Program ?
        value = self.value(program, RDF.value)
	assert value, "No RDF.value found for: %s" % program
        assert value.datatype==REDFOOT.Python, "%s RDF.value is not of datatype REDFOOT.Python. This version of redfoot only supports REDFOOT.Python code values" % program

	program_args = options.program_args
	if program_args:
	    args = [program_args,] + args
	try:
	    c = compile(value+"\n", program, "exec")
	    exec c in dict({"redfoot_loader": self, "args": args, "redfoot_program": program})
	except Exception, e:
	    self.log.error("\nWhile trying to exec %s the following exception occurred:\n" % program)
	    self.log.error(traceback.print_exc())


