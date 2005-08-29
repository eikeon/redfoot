#
#  redfoot.py
#  redfoot
#

from PyObjCTools import NibClassBuilder, AppHelper
from Foundation import NSBundle


info = NSBundle.mainBundle().infoDictionary()[u'PyObjCXcode']

for nibFile in info[u'NIBFiles']:
    print NibClassBuilder.extractClasses(nibFile)

for pythonModule in info[u'Modules']:
    __import__(pythonModule)


from Foundation import *
from AppKit import *

import redfootAppDelegate # so that it gets included in the .app

if __name__ == '__main__':
    AppHelper.runEventLoop()
