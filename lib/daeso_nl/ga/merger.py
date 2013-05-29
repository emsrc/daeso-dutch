"""
Merging matched graphs into a parallel graph corpus
"""

import copy
import numpy

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.graphpair import GraphPair
from daeso.pair import Pair

from daeso_nl.ga.corpusinst import CorpusInst


class Merger(object):
    """
    Merging of matched relations into a graph pair as node alignments
    """
    
    def __init__(self,  no_relation=str(None)):
        """
        Create a new Merger instance
        
        @keyword no_relation: relation label representing "no relation"
        """
        self.no_rel = no_relation
    
    
    def merge(self, graph_inst, graph_pair):
        """
        Merges matched relations from graph instances into a graph pair as
        node alignments
        
        @param graph_inst: a Numpy record array containing the instances for a
        pair of graphs; it should contain the fields source_node, target_node
        and match_relation
        
        @param graph_pair: a GraphPair instance
        """
        assert isinstance(graph_inst, numpy.ndarray)
        assert isinstance(graph_pair, GraphPair)
        
        for inst in graph_inst:
            if inst["match_relation"] != self.no_rel:
                nodes = Pair( inst["source_node"], 
                              inst["target_node"] )
                graph_pair.add_align(nodes, inst["match_relation"])
                
          