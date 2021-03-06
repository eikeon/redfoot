<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdfe="http://redfoot.net/3.0/rdf#"
   xmlns:code="http://redfoot.net/3.0/code#"
   xmlns:boot="http://redfoot.net/3.0/boot#"
   xmlns:kernel="http://redfoot.net/3.0/kernel#"
>
 
  <rdfe:RDFXMLDocument rdf:about="">
  </rdfe:RDFXMLDocument>
  
  <rdfe:Namespace rdf:about="#">
    <rdfs:label>Redfoot Boot</rdfs:label>
    <rdfs:comment></rdfs:comment>
  </rdfe:Namespace>

  <boot:Resource rdf:ID="Globals">
    <rdfs:label>Boot Globals</rdfs:label>
    <rdfs:comment>Where the BootLoader looks for which boot program to run if one was not specified.</rdfs:comment>
  </boot:Resource>

  <boot:Resource rdf:ID="Defaults">
    <rdfs:label>Boot Defaults</rdfs:label>
    <rdfs:comment>Where the BootLoader looks for which boot program to run if not found in Globals.</rdfs:comment>
    <boot:program rdf:resource="http://svn.redfoot.net/trunk/boot#loader"/>
  </boot:Resource>

  <code:Code rdf:ID="loader">
    <rdfs:label>Redfoot Loader</rdfs:label>
    <rdfs:comment>

Redfoot an application for managing and running hypercode. And includes hypercode for building websites.

For help on Redfoot see:

   redfoot.py help

    </rdfs:comment> 
    <code:python rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
<![CDATA[

from rdflib import URIRef

import logging

_logger = logging.getLogger(redfoot_loader.label(__uri__))

from optparse import OptionParser
parser = OptionParser("usage: %prog program <program_options>")
parser.add_option("--path", dest="path", help="path to database") 
parser.add_option("--program", dest="program", help="URIRef of program for kernel to load and run. Defaults to command_runner")
parser.add_option("--rebuild-from-journal", action="store_true", dest="rebuild_from_journal", help="rebuild the store from the journal file")    
parser.add_option("--update", action="store_true", dest="update", help="update cached version of program")    
parser.set_defaults(path="redfoot_db", program = None, update=False, 
                    program="http://redfoot.net/3.0/kernel#runner")

parser.allow_interspersed_args = False

(options, args) = parser.parse_args(args)

KERNEL = URIRef("http://redfoot.net/3.0/kernel#module")
redfoot_loader.load(URIRef("kernel#module", base=__uri__), publicID=KERNEL)

Kernel = redfoot_loader.module(KERNEL).Kernel

redfoot = Kernel("Sleepycat")

physical = URIRef(__uri__.split("/boot#loader")[0])
redfoot.map(URIRef("http://redfoot.net/3.0"), physical)

redfoot.open(options.path, rebuild=options.rebuild_from_journal)
try:
    program = URIRef(options.program)
    # NOTE: Just for reference we load __uri__
    #program = URIRef(program, base=__uri__)
    if options.update:
        redfoot.load(KERNEL)
        redfoot.load(program)
        redfoot.load(__uri__)
    else:
        redfoot.check(KERNEL)
        redfoot.check(program)
        redfoot.check(__uri__)
    _logger.info("running: %s" % redfoot.label(program))
    _logger.debug("  uri: %s" % program)
    redfoot.execute(program, args=args)
except Exception, e:
    _logger.exception(e)
finally:
    redfoot.close(commit_pending_transaction=True)

]]>
    </code:python>
  </code:Code>

</rdf:RDF>  
