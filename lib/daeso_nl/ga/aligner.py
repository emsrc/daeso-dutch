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
alignment of a pair of graphs
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


__all__ = [
    "GraphAligner"]

from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.extractor import Extractor
from daeso_nl.ga.classifier import Classifier, TimblClassifier
from daeso_nl.ga.matcher import Matcher


class GraphAligner(object):
    """
    Aligns a pair of graph
    """
    
    def __init__(self, 
                 descriptor=None, 
                 extractor=None,
                 classifier=None,
                 matcher=None):
        self.descriptor = descriptor or Descriptor()
        self.extractor = extractor or Extractor(self.descriptor)
        self.classifier = classifier or Classifier()
        self.matcher = matcher or Matcher(no_rel=self.descriptor.no_rel)
    
    def align(self, graph_pair, clear=True):
        if clear: graph_pair.clear()
        graph_inst = self.extractor.extract(graph_pair)
        class_output = self.classifier.classify(graph_inst)
        self.matcher.match(graph_inst)
        return graph_inst
    
        

    