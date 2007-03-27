<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rdf:RDF [
  <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#">
  <!ENTITY rdfe "http://redfoot.net/3.0/rdf#">
  <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
  <!ENTITY code "http://redfoot.net/3.0/code#">
  <!ENTITY command "http://redfoot.net/3.0/command#">
]>
<rdf:RDF
   xmlns:rdf="&rdf;"
   xmlns:rdfs="&rdfs;"
   xmlns:rdfe="&rdfe;"
   xmlns:code="&code;"
   xmlns:command="&command;"
   xmlns:kernel="http://redfoot.net/3.0/kernel#"
>

  <rdfe:Namespace rdf:about="#">
    <rdfs:label>Redfoot Command</rdfs:label>
    <rdfs:comment>The Redfoot Command Namespace.</rdfs:comment>
  </rdfe:Namespace>

  <rdfs:Class rdf:ID="Command">
    <rdfs:label>Command</rdfs:label>
    <rdfs:comment>...</rdfs:comment>
    <rdfs:subClassOf rdf:resource="&code;Code"/>
  </rdfs:Class>

</rdf:RDF>
