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
Alpino client
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import socket
import xmlrpclib

from daeso_nl.alpino.server import DEFAULT_HOST, DEFAULT_PORT


def alpino_client(uri=None):
    if not uri:
        uri = "http://%s:%d" % (DEFAULT_HOST, DEFAULT_PORT)
        
    server_proxy = xmlrpclib.ServerProxy(uri, encoding="utf-8")

    try:
        server_proxy.parse("test")
    except socket.error, inst:
        sys.stderr.write('No Alpino server running on host "%s" ?\n' % uri)
        raise inst
    
    return server_proxy

