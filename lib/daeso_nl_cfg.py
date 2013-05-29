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
Configuration namespace

Convenience module to import everything related to configuring a parallel
graph corpus aligner or a graph align server in a single flat name space. 
Use as:

from daeso_nl_cfg import *
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# Description
from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.descriptor import *

# Extraction
from daeso_nl.ga.feats import *
from daeso_nl.ga.extractor import *

# Classification
from daeso_nl.ga.classifier import *

# Matching
from daeso_nl.ga.matcher import *

# Graph alignment
from daeso_nl.ga.aligner import *

# Corpus alignment
from daeso_nl.ga.corpus import *

# Cornetto db
from daeso_nl.ga.feats.cornet import (
    create_cornet_server_proxy, 
    load_cornet,
    init_cornet )

# Alpino parser
from daeso_nl.alpino.client import alpino_client

# Align server
from daeso_nl.ga.server import AlignServer


