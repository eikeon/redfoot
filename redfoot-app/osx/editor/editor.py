import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

NibClassBuilder.extractClasses("editor")

from EditorController import EditorController
from ContextsController import ContextsController


if __name__ == "__main__":
    print "We already have one running"
    #AppHelper.runEventLoop()
