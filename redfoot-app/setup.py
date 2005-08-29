from distutils.core import setup

setup(
    name = 'redfoot',
    version = "2.0.0",
    description = "A hypercode program loader and runner",
    author = "Daniel Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://redfoot.net/",

    license = "http://redfoot.net/2005/08/20/redfoot-2.0.0/LICENSE",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python"],
    long_description = "A hypercode program loader and runner.",

    packages = ["redfootlib"],
    scripts = ["bin/redfoot"],
    )


