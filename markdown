<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
   xmlns:rdfe="http://redfoot.net/3.0/rdf#"
   xmlns:code="http://redfoot.net/3.0/code#"
>

  <rdfe:RDFXMLDocument rdf:about="">
  </rdfe:RDFXMLDocument>
  
  <code:Module rdf:ID="module">
    <rdfs:label>module for transforming markdown format</rdfs:label>      
    <code:python rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
<![CDATA[

#!/usr/bin/env python

# Python-Markdown
#
# Started by Manfred Stienstra (manfred.stienstra [at] dwerg.net,
# http://www.dwerg.net/projects/markdown/).  Extended and maintained
# by Yuri Takhteyev (yuri [at] freewisdom.org, http://www.freewisdom.org)
#
# Project website: http://www.freewisdom.org/projects/python-markdown
#
# License: GPL 2 (http://www.gnu.org/copyleft/gpl.html)
#
# Version: 0.4

import re
import sys
import os
import xml.dom.minidom

HTML_PLACEHOLDER = "HTML_BLOCK_GOES_HERE_21738940712938470198_ALKJDL"

def print_error(string):
    """
    Print an error string to stderr
    """
    #sys.stderr.write(string.toString()+'\n')
    sys.stderr.write(string +'\n')


debug_file = None

def debug(data, prefix) :
    return
    global debug_file
    if debug_file is None:
        debug_file = open("md.log", "w")
    debug_file.write( "---------- %s ------------------\n" % prefix )
    if type(data) == type('asdfa') :
        debug_file.write(data + "\n")

    elif type(data) == type([]) :
        for x in data :
            debug_file.write(x + "\n")


class Markdown:
    """Markdown formatter.

    This the class for creating a html document from Markdown text
    """

    regExp = {
        'reference-def' : re.compile(r'^(  )?\[([^\]]*)\]:\s*([^ ]*)(.*)'),
        'header':         re.compile(r'^(#*)([^#]*)(#*)$'),
        'backtick':       re.compile(r'^([^\`]*)\`([^\`]*)\`(.*)$'),
        'escape':         re.compile(r'^([^\\]*)\\(.)(.*)$'),
        'emphasis':       re.compile(r'^([^\*]*)\*([^\*]*)\*(.*)$|^([^\_]*)\_([^\_]*)\_(.*)$'),
        'link':           re.compile(r'^([^\[]*)\[([^\]]*)\]\s*\(([^\)]*)\)(.*)$'),
        'reference-use' : re.compile(r'^([^\[]*)\[([^\]]*)\]\s*\[([^\]]*)\](.*)$'),
        'strong':       re.compile(r'^([^\*]*)\*\*(.*)\*\*([^\*]*)$|^([^\_]*)\_\_(.*)\_\_([^\_]*)$'),
        'containsline': re.compile(r'^([-]*)$|^([=]*)$', re.M),
        'ol':    re.compile(r'^[\d]*\.\s+(.*)$'),
        'ul':    re.compile(r'^[*+-]\s+(.*)$'),
        'isline':       re.compile(r'^(\**)$|^([-]*)$'),
        'tabbed':       re.compile(r'^((\t)|(    ))(.*)$'),
        'quoted' : re.compile(r'^> ?(.*)$'),
        'empty' : re.compile(r'^\s*$')
    }
    
    def __init__(self, text):
        """
           Create a new Markdown instance.
        
           @param text: The text in Markdown format.
        """

        self.references={}
        self.text = self._preprocess(text)
        self.rawHtmlBlocks=[]
        

    def _transform(self):
        """
           Transforms the Markdown text into a XHTML body document

           @returns: An xml.dom.minidom.Document
        """
        doc = xml.dom.minidom.Document()
        #body = doc.createElementNS("http://www.w3.org/1999/xhtml", "body")
        body = doc.createElement("span")
        body.appendChild(doc.createTextNode('\n'))
        body.setAttribute('class', 'markdown')
        doc.appendChild(body)
        self.doc = doc
        self._processSection(body, self.text.split('\n'))
        body.appendChild(doc.createTextNode('\n'))    
        return doc

    def _preprocess(self, text):
        """
           Preprocess the source text.  In particular, this includes
           normalizing new lines and building a set of reference
           definitions.

           @param text: The text in Markdown format.
           @returns: Normalized text without reference definitions.
        """
        # Remove whitespace.
        text = text.strip()
        # Zap carriage returns.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Extract references
        # E.g., [id]: http://example.com/  "Optional Title Here"

        text_no_ref = "";#\n"
        for line in text.split("\n") :
            m = self.regExp['reference-def'].match(line)
            if m:
                self.references[m.group(2)] = (m.group(3), m.group(4).strip())
            else :
                text_no_ref += line
                text_no_ref += "\n"

        return text_no_ref #+ "\n"



    def _processSection(self, parent_elem, lines, inList = 0) :

        """
           Process a section of a source document, looking for high
           level structural elements like lists, block quotes, code
           segments, html blocks, etc.  Some those then get stripped
           of their high level markup (e.g. get unindented) and the
           lower-level markup is processed recursively.

           @param parent_elem: DOM element to which the content will be added
           @param lines: a list of lines
           @param inList: a level
           @returns: None
        """
        
        debug (lines, "Section: %d" % inList)
        if not lines :
            return

        # Deal with HR lines (needs to be done before processing lists)
        
        if self._isLine(lines[0]) :  
            parent_elem.appendChild(self.doc.createElement('hr'))
            self._processSection(parent_elem, lines[1:], inList)
            return

        # Check if this section starts with a list, a blockquote or
        # a code block

        processFn = { 'ul' :     self._processUList,
                      'ol' :     self._processOList,
                      'quoted' : self._processQuote,
                      'tabbed' : self._processCodeBlock }
        
        for regexp in ['ul', 'ol', 'quoted', 'tabbed'] :
            m = self.regExp[regexp].match(lines[0])
            if m :
                processFn[regexp](parent_elem, lines, inList)
                return

        # We are not looking at one of the high-level structures like
        # lists or blockquotes.  So, it's just a regular paragraph
        # (though perhaps nested inside a list or something else).
        # However, we are not in the list, we just need to look for a
        # blank line.  If we _are_ inside a list, however, we need to
        # consider that a sublist does not need to be separated by a
        # blank line.  Rather, the following markup is legal:
        #
        # * The top level list item
        #
        #     Another paragraph of the list.  This is where we are now.
        #     * Underneath we might have a sublist.
        #
        
        if inList :

            start, theRest = self._linesUntil(lines, (lambda line:
                             self.regExp['ul'].match(line)
                             or self.regExp['ol'].match(line)
                                              or not line.strip()))

            self._processSection(parent_elem, start, inList - 1)
            self._processSection(parent_elem, theRest, inList - 1)
                    
        else : # Ok, we it's just a simple block

            paragraph, theRest = self._linesUntil(lines, lambda line:
                                                 not line.strip())
            debug(paragraph, "Para: ")
            parent_elem.appendChild(self._handleSimpleBlock(self.doc,
                                                      "\n".join(paragraph)))
            if theRest :
                theRest = theRest[1:]  # skip the first (blank) line
            debug(theRest[:1], "%%")
            self._processSection(parent_elem, theRest, inList)
            




    def _processUList(self, parent_elem, lines, inList) :
        self._processList(parent_elem, lines, inList,
                         listexpr='ul', tag = 'ul')

    def _processOList(self, parent_elem, lines, inList) :
        self._processList(parent_elem, lines, inList,
                         listexpr='ol', tag = 'ol')


    def _processList(self, parent_elem, lines, inList, listexpr, tag) :
        """
           Given a list of document lines starting with a list item,
           finds the end of the list, breaks it up, and recursively
           processes each list item and the remainder of the text file.

           @param parent_elem: DOM element to which the content will be added
           @param lines: a list of lines
           @param inList: a level
           @returns: None
        """

        ul = self.doc.createElement(tag)  # ul might actually be '<ol>'
        parent_elem.appendChild(ul)

        # Make a list of list items
        items = [] 
        item = -1

        i = 0  # a counter to keep track of where we are

        for line in lines :

            if not line.strip() :
                # If we see a blank line, this _might_ be the end of the list
                i += 1

                # Find the next non-blank line
                for j in range(i, len(lines)) :
                    if lines[j].strip() :
                        next = lines[j]
                        break
                else :
                    # There is no more text => end of the list
                    break
                
                # Check if the next non-blank line is still a part of the list
                if ( self.regExp[listexpr].match(next) or
                     self.regExp['tabbed'].match(next) ):
                    items[item].append(line)
                    continue
                else :
                    break # found end of the list

            # Now we need to detect list items (at the current level)
            # while also detabing child elements if necessary

            for expr in [listexpr, 'tabbed']:

                m = self.regExp[expr].match(line)
                if m :
                    if expr == listexpr :  # We are looking at a new item
                        if m.group(1) : 
                            items.append([m.group(1)])
                            item += 1
                        else :
                            debug(item, "Item: ")
                    elif expr == 'tabbed' :  # This line needs to be detabbed
                        #print m.groups()
                        items[item].append(m.group(4)) #after the 'tab'

                    i += 1
                    break
            else :
                items[item].append(line)  # Just regular continuation 
        else :
            i += 1

        # Add the dom elements
        for item in items :
            li = self.doc.createElement("li")
            ul.appendChild(li)
            debug(item, "LI:")
            self._processSection(li, item, inList + 1)

        # Process the remaining part of the section
        self._processSection(parent_elem, lines[i:], inList)
        

    def _linesUntil(self, lines, condition) :
        """ A utility function to break a list of lines upon the
            first line that satisfied a condition.  The condition
            argument should be a predicate function.
            """
        
        i = -1
        for line in lines :
            i += 1
            if condition(line) : break
        else :
            i += 1
        return lines[:i], lines[i:]

    def _processQuote(self, parent_elem, lines, inList) :
        """
           Given a list of document lines starting with a quote finds
           the end of the quote, unindents it and recursively
           processes the body of the quote and the remainder of the
           text file.

           @param parent_elem: DOM element to which the content will be added
           @param lines: a list of lines
           @param inList: a level
           @returns: None
        """

        dequoted = []
        i = 0
        for line in lines :
            m = self.regExp['quoted'].match(line)
            if m :
                dequoted.append(m.group(1))
                i += 1
            else :
                break
        else :
            i += 1

        blockquote = self.doc.createElement('blockquote')
        parent_elem.appendChild(blockquote)

        self._processSection(blockquote, dequoted, inList)
        self._processSection(parent_elem, lines[i:], inList)
        

    def _processCodeBlock(self, parent_elem, lines, inList) :
        """
           Given a list of document lines starting with a code block
           finds the end of the block, puts it into the dom verbatim
           wrapped in ("<pre><code>") and recursively processes the 
           the remainder of the text file.

           @param parent_elem: DOM element to which the content will be added
           @param lines: a list of lines
           @param inList: a level
           @returns: None
        """
        
        detabbed = []
        i = 0
        for line in lines :
            m = self.regExp['tabbed'].match(line)
            if m :
                detabbed.append(m.group(4))
                i += 1
            else :
                break
        else :
            i += 1

        pre =     self.doc.createElement('pre')
        code = self.doc.createElement('code')
        parent_elem.appendChild(pre)
        pre.appendChild(code)
        pre.appendChild(self.doc.createTextNode("\n".join(detabbed)))

        self._processSection(parent_elem, lines[i:], inList)
                

    def _handleInline(self, doc, line):
        """
        Transform a Markdown line with inline elements to an XHTML part

        @param item: A block of Markdown text
        @return: A list of xml.dom.minidom elements
        """
        if not(line):
            return [doc.createTextNode(' '),]
        # two spaces at the end of the line denote a <br/>
        if line.endswith('  '):
            l = self._handleInline(doc, line.rstrip())
            l.append(doc.createElement('br'))
            return l

        m = self.regExp['link'].match(line)
        if m is not None:
            ll = self._handleInline(doc, m.group(1))
            lr = self._handleInline(doc, m.group(4))
            a = doc.createElement('a')
            a.appendChild(doc.createTextNode(m.group(2)))
            a.setAttribute('href', m.group(3))
            #ll.append(doc.createTextNode(" "))
            ll.append(a)
            #ll.append(doc.createTextNode(" "))
            ll.extend(lr)
            return ll

        m = self.regExp['reference-use'].match(line)
        if m is not None:
            ll = self._handleInline(doc, m.group(1))
            lr = self._handleInline(doc, m.group(4))
            a = doc.createElement('a')
            a.appendChild(doc.createTextNode(m.group(2)))

            href, title = self.references.get(m.group(3), ('undefined', '') )
            a.setAttribute('href', href)

            if title :
                a.setAttribute('title', title)
                                              
            #ll.append(doc.createTextNode(" "))
            ll.append(a)
            #ll.append(doc.createTextNode(" "))
            ll.extend(lr)
            return ll

        for type in ['escape', 'strong', 'emphasis', 'backtick']:
            m = self.regExp[type].match(line)
            if m is not None:
                if type == 'emphasis':
                    el = doc.createElement('em')
                elif type == 'strong':
                    el = doc.createElement('strong')
                elif type == 'backtick' :
                    el = doc.createElement('code')
                if m.group(2) is not None:
                    ll = self._handleInline(doc, m.group(1))
                    lr = self._handleInline(doc, m.group(3))
                    txtEl = doc.createTextNode(m.group(2))
                elif m.group(5) is not None:
                    ll = self._handleInline(doc, m.group(4))
                    lr = self._handleInline(doc, m.group(6))
                    txtEl = doc.createTextNode(m.group(5))
                if type in ['escape'] :
                    ll.append(txtEl)
                else :
                    el.appendChild(txtEl)
                    ll.append(el)
                    
                ll.extend(lr)
                return ll

                
        else:
            return [doc.createTextNode(line),]

 
    def _handleHeader(self, doc, text):
        """
        Transform a Markdown header to an XHTML part

        @param block: A block of Markdown text        
        @return: An xml.dom.minidom element
        """
        m = self.regExp['header'].match(text)
        if m is None:
            return doc.createTextNode('')

        # we only allow h1 - h6
        if len(m.group(1)) > 6:
            el = doc.createTextNode(text)
            return el
        else:
            el = doc.createElement("h%s" % len(m.group(1)))
            txtEl = doc.createTextNode(m.group(2).strip())
            el.appendChild(txtEl)
            return el

    def _handleParagraph(self, doc, block, noinline=False):
        """
        Transform a Markdown paragraph to an XHTML part

        @param block: A block of Markdown text 
        @param noinline: Whether to live inline elements alone or not
        @return: An xml.dom.minidom element
        """
        el = doc.createElement('p')

        if noinline:
            el.appendChild(doc.createTextNode(block))
        else :
            for item in self._handleInline(doc, block.replace("\n", " ")) :
                el.appendChild(item)

        return el


    def _handleSimpleBlock(self, doc, block, noinline=False):
        """
        
           Transform a _simple_ block of Markdown to an XHTML part.  A
           simple block is a block that does not contain any
           structural elements that can be nested.
           
           @param block: A block of Markdown text with non-nesting elements
           @param noinline: Whether to live inline elements alone or not
           @return: A list of xml.dom.minidom elements
        """
        
        # we don't care about a bunch of newlines
        if not(block):
            return doc.createTextNode('')

        # header
        if block.startswith('#'):
            return self._handleHeader(doc, block)
        
        elif block.startswith("<") : # very permisive test for HTML
            self.rawHtmlBlocks.append(block)
            el = doc.createTextNode("\n" + HTML_PLACEHOLDER + "\n")
            return el
        
        # everything else
        else:
            # header
            lineMatch = self.regExp['containsline'].search(block)
            if lineMatch and (lineMatch.group(1) or lineMatch.group(2)):
                lines = block.split('\n')
                try:
                    if lines[1].startswith('='):
                        return self._handleHeader(doc, '#'+lines[0])
                    elif lines[1].startswith('-'):
                        return self._handleHeader(doc, '##'+lines[0])
                except IndexError, e:
                    print_error('Error: Found a strange header block')
                    print_error(block)
                    raise e
                print_error('Error: Isline was true, while there was no line')
                print_error(block)
                return doc.createTextNode('\n')    
            # this is a block with no inline elements
            elif noinline:
                return doc.createTextNode(block)
            # this is a paragraph
            else:
                return self._handleParagraph(doc, block, noinline)


    def _isLine(self, block) :

        """
            Determines if a block should be replaced with an <HR>
        """

        text = block.replace(' ', '')
        match = self.regExp['isline'].match(text)
        if match and (match.group(1) or match.group(2)) and len(text) > 2:
            return 1
        else:
            return 0


    def __str__(self):
        """
        Return the document in XHTML format.

        @returns: A serialized XHTML body.
        """
        doc = self._transform()
        xml = doc.toxml()

        buffer = ""
        self.rawHtmlBlocks.reverse()

        for line in xml.split("\n")[2:-1] :
            if line == HTML_PLACEHOLDER :
                buffer += self.rawHtmlBlocks.pop()
                buffer += "\n"
            else :
                buffer += line
                buffer += "\n"

        return buffer
    
    toString = __str__


def markdown(text):
    return Markdown(text).toString() 

if __name__ == '__main__':
    print Markdown(file(sys.argv[1]).read())

]]>
    </code:python>
  </code:Module>

</rdf:RDF>  
