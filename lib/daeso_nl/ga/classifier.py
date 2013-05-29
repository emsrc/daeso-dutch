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
Classification and weighting of alignment relations
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


__all__ = [
    "TimblClassifier",
    "entropy_weight" ]

import math

from tt.client import TimblClient
from tt.server import TimblServer
from tt.outparser import parse_distrib


class Classifier(object):
    
    def classify(self, instances):
        pass


class TimblClassifier(Classifier):
    
    def __init__(self, descriptor, inst_fname=None, inst_base_fname=None, 
                 options="", weight_func=None, server_log_fname=None):
        """
        Create a new TimblClassifier instance
        
        @param descriptor: Descriptor instance
        
        @keyword inst_fname: name of file containing Timbl instances 
        
        @keyword inst_base_fname: name of file containing Timbl instance base 
        
        @keyword options: list of additional Timbl options, excluding -f, -m,
        +vo, +vdb, +vdi
        
        @keyword server_log_fname: filename for Timbl server log
        
        @param weight_func: weight function; defaults to entropy_weight
        """
        self.no_rel = descriptor.no_rel
        self._init_server(descriptor, inst_fname, inst_base_fname, options,
                          server_log_fname)
        self._init_client()
        self.weight_func = weight_func or entropy_weight
        
    def _init_server(self, descriptor, inst_fname, inst_base_fname, options,
                     server_log_fname):
        options = timbl_options_string(descriptor, 
                                       inst_fname=inst_fname,
                                       inst_base_fname=inst_base_fname,
                                       other=options)
        # Timbl server will automatically terminate when TimblServer object
        # dies, so keep a reference to it
        self._server = TimblServer(timbl_opts=options,
                                   server_log_fname=server_log_fname)
        self._server.start()
        
    def _init_client(self):
        self._client = TimblClient(self._server.port)
        self._client.connect()
    
    def classify(self, instances):
        """
        adds predicted class and associated weight to instances
        
        @param instances: numpy.ndarray instance 
        """
        for inst in instances:
            # Assumes that last field in instance is the true class
            inst_str = "\t".join( self._to_str(value) 
                                  for value in inst )
            result = self._client.classify(inst_str) 
            inst["pred_relation"] = result["CATEGORY"]
            # The Timbl client is lazy and does not automatically parse the
            # distribution string, so we use parse_distrib to obtain an
            # iterator over (class, count) pairs
            distribution = parse_distrib(result["DISTRIBUTION"]) 
            inst["pred_weight"] = self.weight_func(
                category=result["CATEGORY"], 
                distribution=distribution)
    
    def _to_str(self, value):
        # value can be a bool, number, ascii string or unicode string
        try:
            return str(value)
        except UnicodeEncodeError:
            return value.encode("utf-8")


#---------------------------------------------------------------------------
# Weight functions
#---------------------------------------------------------------------------

# Weight functions are called with two keyword arguments:
#
#   1. category: the predicted relation as a string 
#
#   2. distribution: the class distribution as a sequence of (relation, count)
#      tuples, where relation is a string and count is a float   
#
# Weight functions must return a float between 0.0 and 1.0, where highter
# weight indicates higher confidence in the prediction.

def entropy_weight(category, distribution, no_rel=str(None), **kwargs):
    """
    Prediction weight function based on entropy of the class distribution.
    If the relation is different from no_rel, than the weight is one minus
    the normalized class distribution entropy. Otherwise it is zero.
    
    @param category: the predicted relation as a string 
    
    @param distribution: class distribution as a sequence of (class, count)
    tuples
    
    @return: weight as a float value between 0.0 and 1.0
    """
    if category != no_rel:
        return 1 - _class_distrib_entropy(distribution)
    else:
        return 0.0


# support functions

def _class_distrib_entropy(distribution):
    """
    Normalized entropy of the class distribution.
    
    @param distribution: class distribution as a sequence of (class, count)
    tuples
    
    @return: entropy as a float value between 0.0 and 1.0
    
    Other keyword arguments are ignored.
    
    Intuitively the normalized entropy is zero if all nearest neighbours are
    of the same class, whereas it goes to 1 if the nearest neighbours are
    equally distributed over all possible classes.
    """
    # FIXME: there is probably a more efficient way to calculate this
    counts = [ count 
               for class_, count in distribution ]
    total = float(sum(counts))
    entropy = -sum([ ((c/total) * math.log((c/total), 2))
                     for c in counts])
    try:
        norm_entropy = entropy / math.log(len(counts), 2)
    except ZeroDivisionError:
        # there is only one nearest neighbour
        norm_entropy = 0.0
    
    return norm_entropy
    

#-----------------------------------------------------------------------------
# Timbl helper functions
#-----------------------------------------------------------------------------

def feature_metrics_string(descriptor, default="O"):
    """
    return the Timbl feature metrics string for this feature description
    (e.g. "O:N1:O2:I3")
    """
    # the last feature, i.e. "true_relation", has None as its value for metric
    # value, and is thus skipped
    return ( default + ":" +
             ":".join([ feat.metric + str(i + 1) 
                        for i,feat in enumerate(descriptor)
                        if feat.metric not in (default, None) ]) )



def timbl_options_string(descriptor, inst_fname=None, inst_base_fname=None,
                         other=None):
    """
    return Timbl options options string for this feature description
    and instances filename
    """
    # verbosity features force output of distribution and distance
    options = "+vo +vdb +vdi "
    
    # timbl feature metrics are derived from the feature description 
    options += "-m" + feature_metrics_string(descriptor)
    
    if inst_fname:
        options += " -f " + inst_fname
    
    if inst_base_fname:
        options += " -i " + inst_base_fname
        
    if other:
        options += " " + other
        
    return options
    