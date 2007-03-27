<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdfe="http://redfoot.net/3.0/rdf#"
   xmlns:code="http://redfoot.net/3.0/code#"
   xmlns:server="http://redfoot.net/3.0/server#"
>

  <rdfe:RDFXMLDocument rdf:about="">
  </rdfe:RDFXMLDocument>

  <rdfe:Namespace rdf:about="#">
    <rdfs:label>Kid</rdfs:label>
    <rdfs:comment>The Redfoot kid namespace.</rdfs:comment>
  </rdfe:Namespace>

  <rdf:Property rdf:ID="template">
    <rdfs:label>content</rdfs:label>
    <rdfs:comment></rdfs:comment>
    <rdfs:domain rdf:resource="#Entry"/>
    <rdfs:range rdf:resource="http://www.w3.org/2000/01/rdf-schema#Literal"/>
  </rdf:Property>

  <rdfs:Class rdf:ID="Template">
    <rdfs:label>Kid Template</rdfs:label>
    <rdfs:comment></rdfs:comment>
    <rdfs:subClassOf rdf:resource="http://redfoot.net/3.0/rdf#Resource"/>
    <server:display rdf:resource="">
      <code:Code rdf:ID="kid_display">
        <rdfs:label>kid display</rdfs:label>
        <code:python rdf:datatype="http://redfoot.net/3.0/redfoot#Python">
<![CDATA[

_logger = redfoot.getLogger(__uri__)

from kid import XML
from StringIO import StringIO

def kid_display(page_part_uri, **args):
    """ 
    Due to the way kid works we can not serialize a template within a
    template directly to the output stream. Instead we have to return
    it as an element stream to the template it appears within. Hence
    the create_display level of complexity.

    See Also: http://www.kid-templating.org/trac/ticket/29
    """
    _logger.info("kid_display(%s)" % page_part_uri)
    if page_part_uri is not None:
        sio = StringIO()
        disp = lookup(SERVER.display, uri=page_part_uri)
        #if disp is None:
            #_logger.warning("%s had no SERVER.display" % page_part_uri)
        _w = response.write
        response.write = sio.write
        _logger.info("found: %s" % disp)
        context = dict(globals())
        context.update(args)
        redfoot.execute(disp, context, page_part_uri=page_part_uri, fragment=True, output="xml")
        response.write = _w
        return XML(sio.getvalue())
    else:
        return XML("")

_logger.info("kid_direct_display(%s)" % page_part_uri)
if page_part_uri:
    value = redfoot.value(page_part_uri, KID.template)
    if value:
        mod = kid_module.get_kid_template(page_part_uri, value)
        global display
        display = kid_display
        t = mod.Template(**globals())        
        try:
            t.write(response, encoding="utf-8", fragment=fragment, output=output)
        except Exception, e:
            _logger.exception("While handling request for '%s' and trying to display %s (%s) the following exception occurred:\n" % (request.uri, redfoot.label(page_part_uri), page_part_uri))

]]>
        </code:python>
      </code:Code>
    </server:display>
  </rdfs:Class>

  <rdfs:Class rdf:ID="PageHandler">
    <rdfs:label>Kid Page Handler</rdfs:label>
    <rdfs:comment></rdfs:comment>
    <rdfs:subClassOf rdf:resource="#Template"/>
  </rdfs:Class>

  <rdfs:Class rdf:ID="PagePartHandler">
    <rdfs:label>Kid Page Part Handler</rdfs:label>
    <rdfs:comment></rdfs:comment>
    <rdfs:subClassOf rdf:resource="#Template"/>
  </rdfs:Class>

  <code:Module rdf:ID="module">
    <rdfs:label>kid glue</rdfs:label>      
    <rdfs:comment></rdfs:comment>    
    <code:python rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
<![CDATA[

REQUIRED = "0.9.3" # TODO: bump to 0.9.5? ... as that's all I've tested so far.
def version_tuple(s):
    return tuple([int(x) for x in s[0:5].split(".")])    
try:
    import kid
except ImportError, e:
    raise ImportError("kid is not installed. Please install kid-%s ( http://kid-templating.org/ )" % REQUIRED)

assert version_tuple(kid.__version__) >= version_tuple(REQUIRED), "Please install kid version %s or higher. Found kid version: %s" % (REQUIRED, kid.__version__)


import sys, new, time
from StringIO import StringIO
from kid.compiler import compile

 
def load_template(file, name='', cache=True, encoding=None, ns={},
                  entity_map=None, exec_module=None):
    
    name = name.encode()
    mod_name = "%s" % name.replace(".", "_") # TODO: 
    mod = new.module(mod_name)
    mod.__file__ = name
    mod.__ctime__ = time.time()
    mod.__dict__.update(ns)
    sys.modules[mod_name] = mod
    code = compile(file, filename=name, encoding=encoding)
    exec code in mod.__dict__
    return mod

def Template(file=None, source=None, name=None, encoding=None, **kw):
    mod = load_template(file, name=name, encoding=encoding)
    return mod.Template(**kw)


from itertools import chain

class CleanupElementStream(kid.ElementStream):
    def __init__(self, element_stream, callback):
        kid.ElementStream.__init__(self, element_stream)
        self.__callback = callback

    def __pop(self):
        self.__callback()
        if False:
            yield None

    def __iter__(self):
        return chain(kid.ElementStream.__iter__(self), self.__pop())


_kid_cache = {}

def get_kid_template(uri, value):
    mod = _kid_cache.get(value)
    if mod is None:
        sio = StringIO(value.encode("utf-8"))
        mod = load_template(sio, name=unicode(uri), encoding="utf-8", ns={"__uri__":uri})
        _kid_cache[value] = mod
    return mod


if __name__=="__main__":
    value = u"""
<html xmlns:kid="http://purl.org/kid/ns#">
<?python 
print foo
assert False
?>
</html>
"""
    encoding="utf-8"
    fragment = False
    output = "html"

    context = {}
    context["foo"] = "bar"

    t = Template(StringIO(value.encode(encoding)), name=unicode("..."), encoding=encoding, **context)
    t.write(sys.stdout, encoding=encoding, fragment=fragment, output=output)

]]>
    </code:python>
  </code:Module>

</rdf:RDF>  
