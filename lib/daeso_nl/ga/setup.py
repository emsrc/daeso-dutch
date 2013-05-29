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
Setup a corpus aligner or a graph align server on the basis of a 
configuration file.

The "config" parameter passed to the function is a Python module instance.
Below is an example of a configuration file that documents all supported
attributes. All attributes are optional, except when stated otherwise.

--

from daeso_nl_cfg import *

#-----------------------------------------------------------------------------
# Descriptor
#-----------------------------------------------------------------------------

# *REQUIRED* feature tuple
features = coling10_feats

# custum Descriptor instance
descriptor_inst = MyDescriptor(features)

#-----------------------------------------------------------------------------
# Extractor
#-----------------------------------------------------------------------------

# boolean node selection function; default is "select_node"
node_selector = select_visible_node

# custom Extractor object
extractor_inst = MyExtractor(descriptor_inst, node_selector)

#-----------------------------------------------------------------------------
# Classifier
#-----------------------------------------------------------------------------

# *REQUIRED* Timbl instance base filename; required when using Timbl
timbl_ib_fname = "news_best.ib"

# Timbl instances file;name required when dumping an instance base file
timbl_inst_fname = "news_best.inst"

# additional Timbl options
timbl_opts = "-k15"

# Timbl logging  filename
timbl_log_fname = "news_best_timbl_server_log.txt"

# custom Classifier object
classifier_inst = MyTimblClassifier(
    descriptor_inst, 
    inst_base_fname=inst_base_fname,
    options=timbl_opts,
    server_log_fname=timbl_log_fname)

#-----------------------------------------------------------------------------
# Matcher
#-----------------------------------------------------------------------------

# custom matcher object
matcher_inst = MyMatcher(no_rel=descriptor_inst.no_rel)

#-----------------------------------------------------------------------------
# Graph Aligner
#-----------------------------------------------------------------------------

# custum graph aligner object
graph_aligner_inst = MyGraphAligner(
    descriptor=descriptor_inst,
    extractor=extractor_inst,
    classifier=classifier_inst,
    matcher=matcher_inst)

#-----------------------------------------------------------------------------
# Corpus Aligner
#-----------------------------------------------------------------------------

# boolean graph selector function; default is "select_graph_pair"
corpus_graph_selector = select_parsed_graph_pair

# annotator string added to text of <annotor> element 
corpus_annot = "news_best_v1.0"

# custum corpus aligner instance
corpus_aligner_inst = MyCorpusAligner(
    graph_aligner=graph_aligner_inst,
    graph_selector=corpus_graph_selector)

#-----------------------------------------------------------------------------
# Cornetto
#-----------------------------------------------------------------------------

# Cornetto database is used, e.g. with the cornet similarity features
cornet_required = True

# Cornetto server host address; ; default is http://locallost:5507
cornet_host = "http://ilk.uvt.nl:5507"

# setup Cornetto server 
cornet_create_server = False

# setup Cornetto client
cornet_create_client = True

# load Cornetto databae directly
cornet_load_db = False

# Cornetto lexical units filename
cornet_cdb_lu_fname = "cdb_lu.xml"

# Cornetto synsets filename
cornet_cdb_syn_fname = "cdb_syn.xml"

# custom DaesoCornet instance
cornet_inst =  MyDaesoCornet(
    cornet_cdb_lu_fname,
    cornet_cdb_syn_fname)

#-----------------------------------------------------------------------------
# Alpino
#-----------------------------------------------------------------------------

# This section is only relevant when setting up a graph alignment server. 

# Alpino server host address; default is http://locallost:5506
alpino_host = "http://ilk.uvt.nl:5506" 

# setup Alpino server
alpino_create_server = False

# custom Alpino instance
alpino_inst = MyAlpino()

"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



# all supported configuration attributes
__cfg_attr__ = """
features
descriptor_inst
node_selector
extractor_inst
timbl_ib_fname
timbl_inst_fname
timbl_opts
timbl_log_fname
classifier_inst
matcher_inst
graph_aligner_inst
corpus_graph_selector
corpus_annot
corpus_aligner_inst
cornet_required
cornet_host
cornet_create_server
cornet_create_client
cornet_load_db
cornet_cdb_lu_fname
cornet_cdb_syn_fname
cornet_inst
alpino_host
alpino_create_server
alpino_inst
"""

# TODO:
# - doc strings
# - implement creation of Alpino server and Cornetto server
# - check config for invalid attrs?


from os.path import join, isabs, dirname, abspath, splitext

from daeso_nl_cfg import *


def set_up_corpus_aligner(config):
    try:
        return config.corpus_aligner_inst
    except AttributeError:
        pass
    
    graph_aligner = set_up_graph_aligner(config)
    graph_selector = getattr(config, "corpus_graph_selector",
                             select_graph_pair)
    annotator = getattr(config, "corpus_annot", None)
    
    return CorpusAligner(
        graph_aligner=graph_aligner,
        graph_selector=graph_selector,
        annotator=annotator)


def set_up_align_server(config):
    alpino = set_up_alpino(config)
    
    try:
        return config.corpus_aligner
    except AttributeError:
        pass
    
    graph_aligner = set_up_graph_aligner(config)
    
    return AlignServer(
        alpino=alpino,
        graph_aligner=graph_aligner)


def set_up_graph_aligner(config):
    set_up_services(config)
    
    try:
        return config.graph_aligner_inst
    except AttributeError:
        pass
    
    descriptor = getattr(config, "descriptor_inst",
                         Descriptor(config.features))
    
    node_selector = getattr(config, "node_selector",
                            select_node)
    
    extractor = getattr(config, "extractor_inst",
                        Extractor(
                            descriptor,
                            node_selector))
        
    classifier = getattr(config, "classifier_inst",
                         set_up_classifier(config, descriptor))
    
    matcher = getattr(config, "matcher_inst", 
                      Matcher(no_rel=descriptor.no_rel))
    
    return GraphAligner(
        descriptor=descriptor,
        extractor=extractor,
        classifier=classifier,
        matcher=matcher)


def set_up_classifier(config, descriptor):
    inst_base_fname = _abspath(config, "timbl_ib_fname")
    if not inst_base_fname:
        inst_fname = _abspath(config, "timbl_inst_fname")
    else:
        inst_fname = None
    assert inst_base_fname or inst_fname
    
    server_log_fname = _abspath(config, "timbl_log_fname")
    timbl_opts = getattr(config, "timbl_opts", None)
    
    return TimblClassifier(
        descriptor,
        inst_fname=inst_fname,
        inst_base_fname=inst_base_fname, 
        options=timbl_opts,
        server_log_fname=server_log_fname)
    

def set_up_services(config):
    if getattr(config, "cornet_required", False):
        set_up_cornetto(config)
        
    
def set_up_cornetto(config):
    if getattr(config, "cornet_create_server", False):
        raise NotImplemented("Creating Cornetto server not implemented. "
                             "Start manually using cornet_daeso_server.py.")
    
    if getattr(config, "cornet_inst", False):
        init_cornet(config.cornet)
    elif getattr(config, "cornet_create_client", False):
        host = getattr(config, "cornet_host", "")
        create_cornet_server_proxy(host)
    elif getattr(config, "cornet_load_db", False):
        load_cornet(
            _abspath(config, "cornet_cdb_lu_fname"),
            _abspath(config, "cornet_cdb_syn_fname"))    

    
def set_up_alpino(config):
    if getattr(config, "alpino_create_server", False):
        raise NotImplemented("Creating Alpino server not implemented. "
                             "Start manually using alpino_server.py.")
    
    if getattr(config, "alpino_inst", False):
        alpino = config.alpino
    else:
        host = getattr(config, "alpino_host", None)
        alpino = alpino_client(host)
        
    return alpino


def dump_inst_base(config):
    from daeso_nl.ga.classifier import timbl_options_string
    from tt.timblfile import TimblFile
    
    # determine Timbl options
    descriptor = getattr(config, "descriptor_inst",
                         Descriptor(config.features))
    
    timbl_opts = getattr(config, "timbl_opts", None)
    options = timbl_options_string(descriptor, 
                                   other=timbl_opts)
    
    # determine filenames
    inst_fname = _abspath(config, "timbl_inst_fname")
    assert inst_fname
    inst_base_fname = _abspath(config, "timbl_ib_fname")
    if not inst_base_fname:
        inst_base_fname = splitext(inst_fname)[0] + ".ib"
    
    # dump instance base file
    timbl = TimblFile()
    timbl.train(
        inst_fname, 
        inst_base_fname, 
        options=options)


def _abspath(config, name):
    # unless already absolute, interpret filename relative to configuration
    # file, and return absolute normalized path
    fname = getattr(config, name, None)
    
    if not fname:
        return None
    elif isabs(fname):
        return fname
    else:
        config_dir = dirname(config.__file__)
        return abspath(join(config_dir, fname))