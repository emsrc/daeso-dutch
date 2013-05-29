"""
ga1 graph alignment configuration
"""

import os


# create feature description
from daeso_nl.ga.feats import *
from daeso_nl.ga.descriptor import Descriptor

feats = (
    basic_word +
    word_uniq +
    same_words_context +
    word_len_diff +
    word_overlap +
    root_morph + 
    pos +
    same_pos +
    cornet_sim
)
    
descriptor = Descriptor(feats)


# create graph aligner
from daeso_nl.ga.aligner import create_timbl_graph_pair_aligner

inst_file = os.path.join(
    os.path.dirname(__file__),
    "ga1.inst")
graph_aligner = create_timbl_graph_pair_aligner(descriptor, inst_file)
    

                
def set_up_corpus_aligner():
    from daeso_nl.ga.corpus import CorpusAligner    
    return CorpusAligner(graph_aligner)


def set_up_server():
    from daeso_nl.ga.server import AlignServer
    # setup alpino client if other than localhost:5506
    from xmlrpclib import ServerProxy
    alpino =  ServerProxy("http://ilk.uvt.nl:5506",
                          encoding="iso-8859-1")
    return AlignServer(
        alpino=alpino,
        graph_aligner=graph_aligner)








