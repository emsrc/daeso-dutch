#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Graph align client

A simple client to a graph align server which reads two sentences from
standard input - one sentence per line - and writes server output to standard
output.
"""

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = '0.9'


# intentionally no dependencies on daeso-framework or daeso-dutch libraries, 
# only standard Python

import sys
import socket
import pprint

from optparse import OptionParser
from xmlrpclib import ServerProxy, Fault


DEFAULT_HOST = "localhost:5508"


parser = OptionParser()

parser.add_option(
    "-H", "--host", 
    dest="host",
    metavar="HOST:PORT",
    default=DEFAULT_HOST,
    help="name (or IP address) of host and port "
    "(default is '%s')" % DEFAULT_HOST)

parser.add_option(
    "-i", "--input-encoding", 
    default="utf8", 
    metavar="utf8|latin1|ascii|...",
    help="character encoding of input (default is utf8)")

parser.add_option(
    "-o", "--output-encoding", 
    default="utf8", 
    metavar="utf8|latin1|ascii|...",
    help="character encoding of output (default is utf8)")

parser.add_option(
    "-r", "--raw", 
    dest="raw",
    action="store_true",
    help="raw output as a Python dict")


(options, args) = parser.parse_args()



def _read(prompt):
    # decodes an input string from specified input encoding to unicode,
    # (which Python's XML-RPC knows how to handle/transport)
    inp = raw_input(prompt)
    return inp.decode(options.input_encoding)

def _write(out):
    # converts a string in the dict returned by the "align" method on the
    # server proxy object, which can be either a plain ascii string or a
    # unicode string, to the specified output encoding
    print out.encode(options.output_encoding)

    

server_proxy = ServerProxy("http://" + options.host, encoding="utf-8")

try:
    assert server_proxy.echo("test") == "test"
except Exception, inst:
    if isinstance(inst, socket.error):
        print >>sys.stderr, "ERROR: cannot connect to graph align server" 
    raise inst


while True:
    try:
        source_sent = _read("Source sentence? : ")
        target_sent = _read("Target sentence? : ")
    except (KeyboardInterrupt, EOFError):
        exit(0)

    try:
        result = server_proxy.align(source_sent, target_sent)
    except Fault, inst:
        print >>sys.stderr, inst
        continue
    
    if options.raw:
        pprint.pprint(result)
    else:
        _write( "Source parse:\n" +
                result["source_parse"] +
                "Target parse:\n" +
                result["target_parse"] )
        
        print "Parse alignment:"
        for triple in result["parse_align"]:
            _write( "%d %s %d" % tuple(triple) )
            
        print "\nPhrase alignment:"
        for triple in result["phrase_align"]:
            _write( "%s <==%s==> %s" % tuple(triple) )
            
        print "\n--"
        
        
        