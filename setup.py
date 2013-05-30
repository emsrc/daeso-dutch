#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by Erwin Marsi and TST-Centrale
#
# This file is part of the DAESO Framework.
#
# The DAESO Framework is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The DAESO Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
distutils setup script for distributing the DAESO Framework
"""

# TODO:
# - docs, data and test are not installed when using bdist_wininst...

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


from distutils.core import setup
from glob import glob
from os import walk, remove
from os.path import join, exists
from shutil import rmtree

if exists('MANIFEST'): remove('MANIFEST')
if exists("build"): rmtree("build")

name = "daeso-dutch"
version = "0.9.0"

description = """DAESO Dutch is a language-specific extension to the generic
DAESO Framework."""

long_description = """DAESO Dutch is a language-specific extension to the
generic DAESO Framework. It supports working with Dutch parallel treebanks
parsed with Alpino parser. It also contains support for running graph
alignment experiments on the DAESO corpus, and for building automatic graph
aligners. """


packages = [ root[4:] 
             for (root, dirs, files) in walk("lib") 
             if not ".svn" in root ]
             

def get_data_files(data_dir_prefix, dir):
    # data_files specifies a sequence of (directory, files) pairs 
    # Each (directory, files) pair in the sequence specifies the installation directory 
    # and the files to install there.
    data_files = []

    for base, subdirs, files in walk(dir):
        install_dir = join(data_dir_prefix, base)
        files = [ join(base, f) for f in files
                  if not f.endswith(".pyc") and not f.endswith("~") ]
        
        data_files.append((install_dir, files))

        if '.svn' in subdirs:
            subdirs.remove('.svn')  # ignore svn directories
                
    return data_files


# data files are installed under sys.prefix/share/pycornetto-%(version)
data_dir = join("share", "%s-%s" % (name, version))
data_files = [(data_dir, ['CHANGES', 'COPYING', 'INSTALL', 'README'])]
data_files += get_data_files(data_dir, "doc")
data_files += get_data_files(data_dir, "config/ga0")

sdist_options = dict( 
    formats=["zip","gztar","bztar"])

setup(
    name = name,
    version = version,
    description = description,
    long_description = long_description, 
    license = "GNU Public License v3",
    author = "Erwin Marsi",
    author_email = "e.marsi@gmail.com",
    url = "http://daeso.uvt.nl/daeso-dutch",
    # download_url = """,
    # formats = ["zip","gztar","bztar"],
    requires = ["daeso","cornetto","tt"],
    provides = ["daeso_nl (%s)" % version],
    package_dir = {"": "lib"},
    packages = packages,
    scripts = glob(join("bin","*.py")),
    data_files =  data_files,
    platforms = "POSIX, Mac OS X, MS Windows",
    keywords = [
        "graph alignment", 
        "tree alignment", 
        "parallel treebank",
        "parallel graphbank", 
        "parallel text", 
        "comparable text" ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
        "Natural Language :: English"
    ],
    options =               dict(sdist=sdist_options)
)
