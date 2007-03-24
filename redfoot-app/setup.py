from ez_setup import use_setuptools
use_setuptools()

import sys, warnings
from setuptools import setup, find_packages

from redfootlib import __version__
VERSION = __version__

if sys.version<"2.5":
    warnings.warn("Redfoot is not being tested on Python < 2.5")

setup(
    name = 'redfoot',
    version = VERSION,
    description = "A hypercode program loader and runner",
    author = "Daniel Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://redfoot.net/",
    test_suite = 'nose.collector', # test_suite = 'setuptools.tests',

    license = "BSD",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Natural Language :: English",
                   "Topic :: Software Development :: Libraries :: Application Frameworks",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
    long_description = \
    """A hypercode program loader and runner.

    If you have recently reported a bug marked as fixed, or have a craving for
    the very latest, you may want the development version instead:
    http://svn.redfoot.net/trunk/redfoot-app#egg=redfoot-dev
    """,
    keywords = "hypercode RDF framework",
    download_url = "http://redfoot.net/redfoot-%s.tar.gz" % VERSION,

    packages = ["redfootlib"],

    entry_points = {
        'console_scripts': [
            'redfoot = redfootlib.main:main',
        ]
    },

    install_requires = ["rdflib>=2.4.0.dev-r1005,==dev", "zope.interface>=3.3.0", "kid>=0.9.5"],

    )


