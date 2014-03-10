#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Alpino client

A simple client to Alpino server which reads input from standard input - one
sentence per line - and writes parses in XML format to standard output.
"""

# TODO:
# - handle encoding errors
# - reset cache


__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = '0.9'

import sys
import socket

from xmlrpclib import ServerProxy, Fault
from daeso.utils.cli import DaesoArgParser
from daeso_nl.alpino.server import DEFAULT_HOST, DEFAULT_PORT


parser = DaesoArgParser(description=__doc__, version=__version__)



parser.add_argument(
    "-H", "--host", 
    default="%s:%d" % (DEFAULT_HOST, DEFAULT_PORT),
    metavar="HOST[:PORT]",
    help="name or IP address of host (default is '%s') "
    "optionally followed by a port number "
    "(default is %d)" % (DEFAULT_HOST, DEFAULT_PORT))

parser.add_argument(
    "-i", "--input-encoding", 
    default="utf8", 
    metavar="utf8|latin1|ascii|...",
    help="character encoding of input (default is utf8)")

parser.add_argument(
    "-o", "--output-encoding", 
    default="utf8", 
    metavar="utf8|latin1|ascii|...",
    help="character encoding of output (default is utf8)")

parser.add_argument(
    '-t', '--timeout', 
    type=int,
    default=30,
    help="timeout in seconds (default is 30)")
    

args = parser.parse_args()

server_proxy = ServerProxy("http://" + args.host, encoding="utf-8")

try:
    server_proxy.parse("test")
except socket.error, inst:
    sys.stderr.write('No Alpino server running on host "%s" ?\n' % args.host)
    raise inst
    

while True:
    try:
        sentence = raw_input()
    except (KeyboardInterrupt, EOFError):
        exit(0)

    sentence = sentence.decode(args.input_encoding)
    
    try:
        parse = server_proxy.parse(sentence, "last", args.timeout)
    except Fault, inst:
        if "Parser timeout" in str(inst):
            print "<PARSE_TIMED_OUT />"            
        elif "No parser output" in str(inst):
            print "<PARSE_FAILED />"
        else:
            raise inst
    else:
        # strip xml header produced by Alpino
        parse = parse.split("\n", 1)[1]
        # encoding errors raise ValueError (or a more codec specific
        # subclass, such as UnicodeEncodeError)
        parse = parse.encode(args.output_encoding)
        print parse.strip()
    

