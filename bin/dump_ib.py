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
dump instance base

Converts a Timbl instance file to a Timbl instance base file given a graph
aligner configuration. Timbl options and filenames are taken from the
configuration file (cf. the "timbl_inst_fname" and "timbl_ib_fname"
attributes).
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.9"

import imp 

from daeso.utils.cli import DaesoArgParser
from daeso_nl.ga.setup import dump_inst_base

parser = DaesoArgParser(description=__doc__, version=__version__)

parser.add_argument(
    "config",
    metavar="FILE",
    help="configuration file to set up a corpus aligner")  

args = parser.parse_args()

config = imp.load_source("config", args.config)
dump_inst_base(config)