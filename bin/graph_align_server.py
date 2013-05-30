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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
server providing a graph alignment service through XML-RPC
"""

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.9"


import imp
import sys

from daeso.utils.cli import DaesoArgParser

from daeso_nl.ga.setup import set_up_align_server
from daeso_nl.ga.server import ( 
    start_server, 
    DEFAULT_HOST,
    DEFAULT_PORT )

#-------------------------------------------------------------------------------

parser = DaesoArgParser(description=__doc__, version=__version__)

parser.add_argument(
    "config",
    metavar="FILE",
    help="configuration file to set up a graph align server")  

parser.add_argument(
    "-H", "--host", 
    default="%s:%d" % (DEFAULT_HOST, DEFAULT_PORT),
    metavar="HOST[:PORT]",
    help="name or IP address of host (default is '%s') " % DEFAULT_HOST +
    "optionally followed by a port number (default is %d)" % DEFAULT_PORT)

parser.add_argument(
    "-l", "--log", 
    action="store_true", 
    help="log requests")

args = parser.parse_args()


try:
    host, port = args.host.split(":")[:2]
except ValueError:
    host, port = args.host, None
    
args.host = host or "localhost"


try:
    args.port = int(port or DEFAULT_PORT)
except ValueError:
    sys.exit("Error: %s is not a valid port number" % repr(port))
    

config = imp.load_source("config", args.config)
server_inst = set_up_align_server(config)  

start_server(server_inst,
             host=args.host,
             port=args.port,
             log=args.log)
