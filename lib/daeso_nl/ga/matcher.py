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
Reduction of alignments to a matching
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


__all__ = [
    "Matcher" ]


import numpy

from daeso_nl.ga.corpusinst import CorpusInst

try:
    # if available, use Harold Cooper's wrapper of the C++ implementation
    from hungarian import lap2
    
    def solve_lap(cost_mat):
        return enumerate(lap(cost_mat)[0])
    
except ImportError:
    # otherwise backoff to Brian Clapper's pure Python implementation
    from daeso.thirdparty.munkres import Munkres

    munkres = Munkres()
    
    def solve_lap(cost_mat):
        return munkres.compute (cost_mat)

    

        
class Matcher(object):
    """
    Graph matching for a pair of graphs
    
    A Matcher provides a "match" method which reduces a weighed graph
    alignment to a maximally-weighted graph matching by solving the linear
    asignment problem.
    
    The input is a predicted graph alignment. Formally, this alignment is a
    weighted labeled bipartite graph, i.e. 
    - source and target nodes are in disjoint sets (the source and 
      target graphs) 
    - edges have a label (the alignment relation)
    - edges have a weight (the classifiers' "confidence" associated with 
      the predicted relation)
    
    The output is a graph matching. Formally, a matching is a bipartite graph
    where    
    - source and target nodes are in disjoint sets, and
    - the set of edges has no common nodes
    
    In other words, every node has at most one edge. Notice that the matching
    is not necessarily complete, that is, some nodes may remain unaligned.
    
    In implementation terms, a graph alignment between a source graph with
    source nodes s_1,...,s_N and a target graph with target nodes t_1, ...,
    t_M is represented as a Numpy record array with N x M records. Each record
    represents a possible node alignment, where 
    - the nodes are identfied by the "source_node_count" and 
      "target_node_count" fields,
    - the predicted relation is present in the "pred_relation" field, and
    - the associated weight is present in the "pred_weight" field. 
    
    The weights column is reshaped into a square matrix with dimensions equal
    to the max(N,M). The weights are also converted to costs by subtracting
    them from the maximum possible weight. This matrix is then input to a
    solver which solves the linear assignment problem using the Hungarian
    algorithm, linear programming, or any other algorithm. The solution (i.e.
    a maximally weighted graph matching) is then inserted in the
    "match_relation" field of the original record array, while alignments
    below a certain threshold are ignored (i.e. not all nodes need to be
    aligned)
    """
    
    def __init__(self, max_weight=1.0, no_rel=str(None)):
        """
        Create a new Matcher instance
        
        @param max_weight: maximum weight that can be associated to a
        predicted relation (used to convert weights to costs)
        
        @keyword no_rel: special relation label representing "no relation"
        """
        self.max_weight = max_weight
        self.no_rel = no_rel

    
    def match(self, graph_inst, threshold=0):
        """
        Match nodes from a pair of source and target graphs
        
        Reduces a weighed graph alignment to a maximally-weighted graph
        matching by solving the linear asignment problem. The result is stored
        in the "match_relation" field of the input record array, skipping
        alignments with a weight below the threshold.
        
        @param graph_inst: a Numpy record array containing the instances for a
        pair of graphs; it should contain the fields "source_node_count",
        "target_node_count", "pred_relation", "pred_weight" and "match_weight"
        
        @keyword threshold: node alignments with a weight below the threshold
        are deleted.
        """
        assert isinstance(graph_inst, numpy.ndarray)

        # reset results from any previous matchings on the same corpus
        # instances (because the solution only rewrites the "match_relation"
        # field of max(n,m) instances of the total n*m instances)
        graph_inst["match_relation"] = self.no_rel
        
        # n and m are the number of source and target nodes,
        # counted from one
        n, m = ( graph_inst[-1]["source_node_count"], 
                 graph_inst[-1]["target_node_count"] )
        assert n * m == len(graph_inst)
        
        pred_weights = graph_inst["pred_weight"].reshape((n,m))
        
        # turn weights into costs
        cost_mat = self.max_weight - self._square_matrix(pred_weights)
        
        solution = solve_lap(cost_mat)
        
        for row, col in solution:
            if ( row < n and col < m ):
                rec = graph_inst[row * m + col]
                
                if rec["pred_weight"] >= threshold:
                    rec["match_relation"] = rec["pred_relation"]
                else:
                    rec["match_relation"] = self.no_rel
                    
    
    def _square_matrix(self, mat):
        """
        convert a rectangular matrix to a square matrix
        
        @param mat: Numpy matrix
        """
        # there are probably smarter ways to do this... 
        n,m = mat.shape
        
        if n > m:
            filler = numpy.zeros((n, n-m), dtype="f8")
            return numpy.concatenate((mat, filler), axis=1)
        elif n < m:
            filler = numpy.zeros((m-n, m), dtype="f8")
            return numpy.concatenate((mat, filler))
        else:
            return mat
        
        

##class CorpusMatcher(object):
    ##"""
    ##Graph matching nodes for all graph pairs in a corpus
    ##"""
    
    ##def __init__(self, graph_matcher=Matcher()):
        ##"""
        ##Create a new CorpusMatcher instance
        
        ##@keyword graph_matcher: a Matcher instance
        ##"""
        ##self.graph_matcher = graph_matcher
        
        
    ##def match(self, corpus_inst, threshold=0):
        ##"""
        ##Match nodes for all graph pairs in a corpus
        
        ##Simply calls the "match" method of the graph matcher object for all
        ##graph pairs in the corpus.
        
        ##@param corpus_inst: CorpusInst object containing the instances for a
        ##corpus of aligned parallel graphs
        
        ##@keyword threshold: node alignments with a weight below the threshold
        ##are deleted.
        ##"""
        ##assert isinstance(corpus_inst, CorpusInst)
                
        ##for graph_inst in corpus_inst:
            ##self.graph_matcher.match(graph_inst, threshold=threshold)
        