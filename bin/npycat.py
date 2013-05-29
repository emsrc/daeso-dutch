#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cat a numpy binary file 

intended for record arrays
"""

# TODO:
# - options for char encoding
# - option for delilimiter
# - options to supress header



__author__ = 'Erwin Marsi <e.marsi@gmail.com>'

__version__ = "0.1"


import numpy
from daeso.thirdparty.argparse import ArgumentParser, RawDescriptionHelpFormatter


delimiter="\t"
kind2format = {"i": "%d", "f": "%f"}


def npycat(fn):
    array = numpy.load(fn)
    
    types = []
    format = []
    
    for i in range(len(array.dtype)):
        types.append(array.dtype[i].str)
        kind = array.dtype[i].kind
        format.append(kind2format.get(kind, "%s"))
    
    format = delimiter.join(format) 

    print "# " + delimiter.join((str(i+1) for i in range(len(array.dtype))))
    print "# " + delimiter.join(array.dtype.names)
    print "# " + delimiter.join(types)    
    
    for rec in array:
        print format % tuple(rec)

        
        
parser = ArgumentParser(description=__doc__,
                        version="%(prog)s version " + __version__,
                        formatter_class=RawDescriptionHelpFormatter)

parser.add_argument("file", 
                    nargs="+",
                    help=( "numpy binary file (.npy)"))


args = parser.parse_args()

for fn in args.file:
    npycat(fn)
