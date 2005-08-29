import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

from urlparse import urlparse
from rdflib.util import uniq
from rdflib import URIRef, Literal, RDF, RDFS

#NibClassBuilder.extractClasses("editor")


# class defined in editor.nib
class EditView(NibClassBuilder.AutoBaseClass):
    # the actual base class is NSView

    def newItem_(self, sender):
        print "new resource"

    def keyDown_(self, theEvent):
	keyChar = theEvent.characters().characterAtIndex_(0)
	if (keyChar == NSEnterCharacter) or (keyChar == NSCarriageReturnCharacter):
	    self.editorController.editTriple()
	elif (keyChar == NSDeleteCharacter):
	    print "EditView: delete"
	else:
	    super(EditView, self).keyDown_(theEvent)

# class defined in editor.nib
class EditorController(NibClassBuilder.AutoBaseClass, NSComboBoxDataSource, NSOutlineViewDataSource):
    # The actual base class is NSWindowController

    def init(self, redfoot):
        super(EditorController, self).init()
	self.redfoot = redfoot
	self.resources = []
        return self

    def print_(self, sender):
        print "PRINT"

    def newContext_(self, sender):
	print "new context:", sender

    def setContext(self, context):
	# currently ContextContoller calls us
	self.context = context
	resources = uniq(self.redfoot.get_context(context).subjects(None, None))
	resources.sort()
	self.resources = resources 
	self.resourcesTable.reloadData()
	self.resourcesTable.deselectAll_(self)
	self.resourcesTable.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(0), False)

    def editTriple(self):
	subject, predicate, object = self.resourceController.currentTriple()
	self.editTripleController.setTriple((subject, predicate, object), self.context)

    # NSTableDataSource 

    def numberOfRowsInTableView_(self, tableView):
	return len(self.resources)
	
    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
	id = tableColumn.identifier()
	uri = self.resources[row]
	if id=="uri":
	    base =self.context
	    base = base.split("#", 1)[0]
            uri = URIRef(uri.replace(base, "", 1)) # relativize
	    return uri
	elif id=="label":
	    return self.redfoot.label(uri, "")
	elif id=="comment":
	    return self.redfoot.comment(uri, "")
	else:
	    return ""
	
    # NSTableView delegate methos

    def tableViewSelectionDidChange_(self, notification):
	selectedRow = notification.object().selectedRow()
	if selectedRow==-1:
	    resource = None
	else:
	    resource = self.resources[selectedRow]
	self.resource = resource
	self.resourceController.setResource(resource)


class ResourceController(NibClassBuilder.AutoBaseClass):
    def init(self):
        super(ResourceController, self).init()
	self.predicate_objects = []
	self.subject = None
        return self
    
    def currentTriple(self):
	subject = self.subject
	row = self.resourceTable.selectedRow()
	predicate, object = self.predicate_objects[row]
	return subject, predicate, object

    def _getRedfoot(self):
        return self.editorController.redfoot
    redfoot = property(_getRedfoot)

    def setResource(self, resource):
	self.subject = resource
	if resource is None:
	    predicate_objects = []
	else:
	    predicate_objects = list(self.redfoot.predicate_objects(resource))
	    predicate_objects.sort()
	self.predicate_objects = predicate_objects
        self.resourceTable.reloadData()

    # NSTableDataSource 
    def numberOfRowsInTableView_(self, tableView):
        return len(self.predicate_objects)
        
    def tableView_shouldEditTableColumn_row_(self, tableView, tableColumn, row):
        return False

    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
        id = tableColumn.identifier()
        predicate, object = self.predicate_objects[row]
        if id=="predicate":
            return self.redfoot.label(predicate, predicate)
        elif id=="object":
	    if isinstance(object, Literal):
		return object
	    else:
		return self.redfoot.label(object, object)
        else:
            return ""
        
    # NSTableView delegate methos
    def tableViewSelectionDidChange_(self, notification):
        pass
    

class EditTripleController(NibClassBuilder.AutoBaseClass):
    def init(self):
        super(EditTripleController, self).init()
	self.subject = None
	self.values = {}
        return self
    
    def _getRedfoot(self):
        return self.editorController.redfoot
    redfoot = property(_getRedfoot)

    def setTriple(self, (subject, predicate, object), context):
	self.triple = (subject, predicate, object)
	self.context = context
	self.subject.setObjectValue_(subject)
	self.predicate.setObjectValue_(predicate)
	if isinstance(object, Literal):
	    storage = self.object.textStorage()
	    range = NSMakeRange(0, storage.length())
	    self.object.setSelectedRange_(range)
	    self.object.insertText_(object)
	    self.objectScrollView.setHidden_(False)
	    self.objectChoicesScrollView.setHidden_(True)
	else:
	    self._setPossibleValues()
	    self.objectScrollView.setHidden_(True)
	    self.objectChoicesScrollView.setHidden_(False)
	self.editTripleWindow.makeKeyAndOrderFront_(self)

    def textDidChange_(self, notification):
	subject, predicate, object = self.triple
	if isinstance(object, Literal):
	    self.redfoot.remove((subject, predicate, object))
	    new_value = Literal(self.object.textStorage().string())
	    triple = (subject, predicate, new_value)
	    self.redfoot.add(triple, self.context)
	    self.triple = triple
	else:
	    print "TODO: raise an exception"


    def keyDown_(self, theEvent):
	keyChar = theEvent.characters().characterAtIndex_(0)
	print "KEYDOWN.EditTriple '%s' '%s' '%s' " % (theEvent, theEvent.characters(), keyChar)
	if (keyChar == NSEnterCharacter) or (keyChar == NSCarriageReturnCharacter):
	    print "????????????"
	else:
	    super(EditView, self).keyDown_(theEvent)

    def _setPossibleValues(self):
	subject, predicate, object = self.triple
	redfoot = self.redfoot
	values = set()
	#value_list = []
	for range in redfoot.objects(predicate, RDFS.range):
	    for type in redfoot.transitive_subjects(RDFS.subClassOf, range):
		for value in redfoot.subjects(RDF.type, type):
		    values.add(value)
	values.add(object) 
		    #label = first(redfoot.objects(value, RDFS.label)) or value
		    #values[value] = label
		    #value_list.append((label, value))
	#value_list.sort()
	ordered_values = list(values)
	ordered_values.sort()
	self.values = ordered_values
        self.objectChoices.reloadData()
	row = self.values.index(object)
	index_set = NSIndexSet.indexSetWithIndex_(row)
	self.objectChoices.selectRowIndexes_byExtendingSelection_(index_set, False)
	self.objectChoices.scrollRowToVisible_(row)

    # NSTableDataSource 

    def numberOfRowsInTableView_(self, tableView):
	return len(self.values)
	
    def tableView_objectValueForTableColumn_row_(self, tableView, tableColumn, row):
	#id = tableColumn.identifier()
	uri = self.values[row]
	return uri
	
    # NSTableView delegate methos

    def tableViewSelectionDidChange_(self, notification):
	selectedRow = notification.object().selectedRow()
	if selectedRow==-1:
	    resource = None
	else:
	    resource = self.values[selectedRow]
	subject, predicate, object = self.triple
	if not isinstance(object, Literal):
	    self.redfoot.remove((subject, predicate, object))
	    new_value = resource
	    triple = (subject, predicate, new_value)
	    self.redfoot.add(triple, self.context)
	    self.triple = triple
	


