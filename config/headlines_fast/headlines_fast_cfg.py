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
Graph aligner configuration for book text using fast setting

Features: include Cornetto similarity features, so a Cornetto server must be
configured or the Cornetto database must be loaded directly.

Instances: all develop and validation parts from manually annotated headlines
corpus segment, where the "None" is 50% downsampled.

Timbl: uses IGTree
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"
__version__ = "0.9"



from daeso_nl_cfg import *

#import logging
#logging.basicConfig(level=logging.INFO,
#                    format="%(levelname)s <%(name)s> :: %(message)s")


# Descriptor
features = coling10_feats

# Extractor
node_selector = select_visible_node

# Classifier
timbl_ib_fname = "headlines_fast.ib"
timbl_inst_fname = "headlines_fast.inst"
timbl_opts = "-a1 +D"
timbl_log_fname = "headlines_fast_timbl_server_log.txt"

# Corpus aligner
corpus_annot = "%s: v%s" % (__name__, __version__)
corpus_graph_selector = select_parsed_graph_pair

# Cornetto
cornet_required = True
#cornet_host = "http://ilk.uvt.nl:5507"
#cornet_create_client = True

cornet_load_db = True
cornet_cdb_lu_fname = "/exp/projects/Daeso/trunk/software/intern/pycornetto/db/cdb_lu.xml"
cornet_cdb_syn_fname = "/exp/projects/Daeso/trunk/software/intern/pycornetto/db/cdb_syn.xml"

# Alpino
alpino_host = "http://ilk.uvt.nl:5506" 

        
