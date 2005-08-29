"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app


plist = dict(
   NSPrincipalClass='editor',
   CFBundleDevelopmentRegion="English",
   CFBundleExecutable="editor",
   CFBundleIdentifier="net.redfoot",
   CFBundlePackageType="BNDL",
   CFBundleVersion="1.0",
   NSHumanReadableCopyright="Copyright Daniel Krech 2005"
)

setup(
    plugin=['editor.py'],
    data_files=['English.lproj'],
    options=dict(py2app=dict(
        extension='.bundle',
        plist=plist,
    )),
)
