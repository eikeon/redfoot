import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

from urlparse import urlparse
from rdflib.util import uniq
from rdflib import URIRef, Literal, RDF, RDFS

#NibClassBuilder.extractClasses("editor")


class Context(NSObject):
    def init(self, context):
	super(Context, self).init()
	self.context = context
	return self

    def numberOfChildren(self):
	return -1

    def childAtIndex(self, n):
	return None

    def fullPath(self):
	return u"fullpath"

    def relativePath(self, tableColumn):
	id = tableColumn.identifier()
	if id=="context":
	    scheme, netloc, url, params, query, fragment = urlparse(self.context)
	    return url
	else:
	    return u"-"
    

class ContextGroup(NSObject):
    def init(self, context, children):
	super(ContextGroup, self).init()
	self.context = context
	children.sort()
	self.children = children
	self.children.sort()
	return self

    def numberOfChildren(self):
	return len(self.children)

    def childAtIndex(self, n):
	return Context.allocWithZone_(self.zone()).init(self.children[n])

    def fullPath(self):
	return u"fullpath"

    def relativePath(self, tableColumn):
	id = tableColumn.identifier()
	if id=="context":
	    return self.context
	else:
	    return u"-"


class Empty(NSObject):
    def init(self):
	super(Empty, self).init()
	return self

    def numberOfChildren(self):
	return 0

    def childAtIndex(self, n):
	return None

    def relativePath(self, tableColumn):
	return None

	
class Root(NSObject):
    def init(self, contexts):
	super(Root, self).init()
	groups = {}
	for context in contexts:
	    scheme, netloc, url, params, query, fragment = urlparse(context)
	    try:
		s = groups[netloc]
	    except:
		s = groups[netloc] = set()
	    s.add(context)

	children = []
	hosts = groups.keys()
	hosts.sort()
	for key in hosts:		
	    c = ContextGroup.allocWithZone_(self.zone()).init(key, list(groups[key]))
	    children.append(c)

	self.children = children
	return self

    def numberOfChildren(self):
	return len(self.children)

    def childAtIndex(self, n):
	return self.children[n]

    def relativePath(self, tableColumn):
	id = tableColumn.identifier()
	if id=="context":
	    return u"root"
	else:
	    return u"-"

class ContextsView(NibClassBuilder.AutoBaseClass, NSMenuValidation):
    # the actual base class is NSView

    #def newContext_(self, sender):
    #	print "new context:", sender

    def validateMenuItem_(self, menuItem):
	return True

    #def becomeFirstResponder(self):
    #	return True

    def newItem_(self, sender):
        print "new context"

    def newContext_(self, sender):
	print "new context:", sender

    def delete_(self, sender):
	print "DELETE"

    def keyDown_(self, theEvent):
	keyChar = theEvent.characters().characterAtIndex_(0)
	if (keyChar == NSDeleteCharacter):
	    self.contextsController.deleteContext()
        elif theEvent.characters()==u"u":
	    menu = NSApp().mainMenu()
	    print menu
	    menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("editor", None, "")
	    menu.insertItem_atIndex_(menuItem, 1)
            menu.setSubmenu_forItem_(self.delegate().editorMenu, menuItem)
	    menuItem.setTitle_("editor")
	    menu.update()
            editor = self.contextsController.updateContexts()
	else:
	    super(ContextsView, self).keyDown_(theEvent)


# class defined in editor.nib
class ContextsController(NibClassBuilder.AutoBaseClass, NSComboBoxDataSource, NSOutlineViewDataSource, NSMenuValidation):
    # The actual base class is NSWindowController

    def init(self):
        super(ContextsController, self).init()
	self.root = None
        return self

    def delete_(self, sender):
	print "DELETE"

    def validateMenuItem_(self, menuItem):
	return True

    def newContext_(self, sender):
	print "new context:", sender

    def awakeFromNib(self):
	self.updateContexts()

    def _getRedfoot(self):
	if self.editorController is None:
	    return None
        return self.editorController.redfoot
    redfoot = property(_getRedfoot)

    def updateContexts(self):
	self.root = None
	self.contextsOutline.reloadData()            

    def deleteContext(self):
	selectedRow = self.contextsOutline.selectedRow()
	print "selectedRow:", selectedRow
	if selectedRow >= 0:
	    item = self.contextsOutline.itemAtRow_(selectedRow)
	    context = item.context
	    print "context:", context
	    self.redfoot.remove_context(context)
	    self.updateContexts()

    def getRoot(self):
	if self.root is None:
	    if self.redfoot is None:
		self.root = Empty.allocWithZone_(self.zone()).init()
	    else:
		contexts = list(self.redfoot.contexts())
		self.root = Root.allocWithZone_(self.zone()).init(contexts)
	return self.root

    # NSOutlineViewDataSourc

    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
	if item is None:
	    item = self.getRoot()
	return item.numberOfChildren()

    def outlineView_isItemExpandable_(self, outlineView, item):
	if item is None:
	    return True
	else:
	    return (item.numberOfChildren() != -1)

    def outlineView_child_ofItem_(self, outlineView, index, item):
	if item is None:
	    item = self.getRoot()
	return item.childAtIndex(index)

    def outlineView_objectValueForTableColumn_byItem_(self, outlineView, tableColumn, item):
	if item is None:
	    return "/"
	else:
	    return item.relativePath(tableColumn)

    # NSOutlineView delegate methods

    def outlineViewSelectionDidChange_(self, notification):
	#id item = [[notification object] itemAtRow:[[notification object] selectedRow]];
	selectedRow = notification.object().selectedRow()
 	item = notification.object().itemAtRow_(selectedRow)
	context = item.context
	self.editorController.setContext(context)
