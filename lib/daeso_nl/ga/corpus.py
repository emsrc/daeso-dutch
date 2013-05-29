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
alignment of parallel graph corpus
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


__all__ = [
    "CorpusAligner"]


from daeso_nl.ga.aligner import GraphAligner
from daeso_nl.ga.merger import Merger
from daeso_nl.ga.extractor import select_graph_pair 

        
class CorpusAligner(object):
    """
    Processor for aligning graph pairs in a parallel graph corpus
    """
    
    def __init__(self, 
                 graph_aligner=None, 
                 merger=None,
                 graph_selector=select_graph_pair,
                 annotator=None):
        """
        Create a new CorpusAligner instance
        
        @keyword graph_aligner: GraphAligner instance
        
        @keyword merger: Merger instance
        
        @keyword graph_selector: Boolean graph pair selection function
        
        @keyword annotator: annotator string added to text of <annotor> element 
        """
        self.graph_aligner = graph_aligner or GraphAligner()
        self.merger = merger or Merger()
        self.graph_selector = graph_selector
        self.annotator = annotator
    
    def align(self, corpus, clear=False):
        """
        Align graph pairs in parallel graph corpus.
        
        @param corpus: ParalllelGraphCorpus instance
        
        @keyword clear: clear existing alignments
        """
        for graph_pair in corpus:
            if self.graph_selector(graph_pair):
                graph_inst = self.graph_aligner.align(graph_pair, clear)
                self.merger.merge(graph_inst, graph_pair)
                
        if self.annotator:
            corpus.set_annotator(self.annotator)
                
                
        
            
            