#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
simple server providing access to the Alpino parser for Dutch through XML-RPC
"""

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'

__version__ = "0.9"

from sys import exit

from daeso.utils.cli import DaesoArgParser
from daeso_nl.alpino.server import start_server, DEFAULT_HOST, DEFAULT_PORT

parser = DaesoArgParser(description=__doc__, version="%(prog)s version " +
                        __version__)


parser.add_argument("-H", "--host", 
                    default="%s:%d" % (DEFAULT_HOST, DEFAULT_PORT),
                    metavar="HOST[:PORT]",
                    help="name or IP address of host (default is '%s') "
                    "optionally followed by a port number "
                    "(default is %d)" % (DEFAULT_HOST, DEFAULT_PORT))

parser.add_argument("-c", "--command",
                    help="command line to start Alpino parser")

parser.add_argument("-o", "--out_dir",
                    help="directory for writing temporary files")

parser.add_argument('-l', '--log', 
                    action='store_true', 
                    help="log requests")

parser.add_argument('-V', '--verbose', 
                    action='store_true', 
                    help="verbose output")

parser.add_argument('-s', '--cache-size', 
                    type=int,
                    default=0,
                    help="max number of cached parses")

args = parser.parse_args()


try:
    host, port = args.host.split(":")[:2]
except ValueError:
    host, port = args.host, None
    
args.host = host or DEFAULT_HOST


try:
    args.port = int(port or DEFAULT_PORT)
except ValueError:
    exit("Error: %s is not a valid port number" % repr(port))
    

start_server(**args.__dict__)    
