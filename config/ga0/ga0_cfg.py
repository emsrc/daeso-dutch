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
Example of the most basic Graph aligner configuration
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from daeso_nl_cfg import *

# feature definition 
features = same_root + same_pos

# selection of candidate nodes for alignment
node_selector = select_visible_node

# Timbl instance base
timbl_inst_fname = "ga0.inst"

# selection of graph pairs to align (during corpus alignment)
corpus_graph_selector = select_parsed_graph_pair

# address of Alpino server
alpino_host = "http://ilk.uvt.nl:5506" 






