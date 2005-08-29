#
#  redfootAppDelegate.py
#  redfoot
#

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

import os

REDFOOT_DIR = os.path.expanduser('~/Library/redfoot')
if not os.path.isdir(REDFOOT_DIR):
    os.mkdir(REDFOOT_DIR)
os.chdir(REDFOOT_DIR)

from threading import Thread
from time import sleep

NibClassBuilder.extractClasses("MainMenu")

from redfootlib.main import parser
from redfootlib.BootLoader import BootLoader

import sys, logging
from cStringIO import StringIO

stdout = StringIO()
handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter('%(levelname)s %(message)s', None)) 
logging.getLogger().addHandler(handler)

sys.stdout = stdout
sys.stderr = stdout


class OutputThread(Thread):

    def __init__(self, controller):
        Thread.__init__(self)
        self.controller = controller

    def run(self):
        while True:
	    lock = NSLock.alloc().init()
	    if lock.tryLock():
		pool = NSAutoreleasePool.alloc().init()
		controller = self.controller
		output = controller.output
		s = output.getvalue()
		output.truncate(0)
		console = controller.console
		if s and console:
		    storage = console.textStorage()
		    range = NSMakeRange(storage.length(), storage.length())
		    console.setSelectedRange_(range)
		    console.insertText_(s)
                lock.unlock()
		sleep(.1)
	    del pool

class CommandThread(Thread):

    def __init__(self, controller, cmd):
        Thread.__init__(self)
        self.controller = controller
	self.cmd = cmd

    def run(self):
	pool = NSAutoreleasePool.alloc().init()

        options, args = parser.parse_args(args=self.cmd.split())
        self.controller.loader.main(options, args)

	del pool


# class defined in MainMenu.nib
class RedfootController(NibClassBuilder.AutoBaseClass):
    # the actual base class is NSObject
    # The following outlets are added to the class:
    # command
    # console

    def init(self):
        super(RedfootController, self).init()

        self.output = stdout
        worker = OutputThread(self)
        worker.start()

	self.loader = BootLoader()    
        options, args = parser.parse_args(args="".split())
	self.loader.open(options.path)
	self.loader.main(options, args)
	self.redfoot = self.loader.redfoot
        self.redfoot.controller = self	
        return self

    def applicationWillTerminate_(self, aNotification):
	logging.info("closing store")
	self.redfoot.close()

    def runCommand_(self, sender):
        cmd = sender.stringValue()
        if not sender.objectValues().containsObject_(cmd):
	    sender.addItemWithObjectValue_(cmd)
        self.output.write("\nCommand: %s\n" % cmd)
        t = CommandThread(self, cmd)
        t.start()
        
    def tabView_shouldSelectTabViewItem_(self, tabView, tabViewItem):
	print tabView, tabViewItem, tabViewItem.view()
	return True
	
    def tabView_willSelectTabViewItem_(self, tabView, tabViewItem):
	pass #print tabViewItem.view().label.stringValue()

    def tabView_didSelectTabViewItem_(self, tabView, tabViewItem):
	pass
	
    def tabViewDidChangeNumberOfTabViewItems_(self, tabView):
	pass

