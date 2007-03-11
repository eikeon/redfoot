from ez_setup import use_setuptools
use_setuptools()

#from distutils.core import setup
from setuptools import setup, find_packages


setup(
    name = 'redfoot',
    version = "2.1.1",
    description = "A hypercode program loader and runner",
    author = "Daniel Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://redfoot.net/",

    license = "http://redfoot.net/2006/10/15/redfoot-2.1.0/LICENSE",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python"],
    long_description = "A hypercode program loader and runner.",

    packages = ["redfootlib"],
    #scripts = ["bin/redfoot"],

    entry_points = {
        'console_scripts': [
            'redfoot = redfootlib.main:main',
        ]
    },

    install_requires = ["rdflib", "zope.interface>=3.3.0", "kid>=0.9.5"],

    )


