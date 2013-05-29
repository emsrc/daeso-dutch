"""
Feature descriptions
"""

import sys

import numpy

from daeso.thirdparty.odict import OrderedDict
from daeso_nl.ga.feature import Feat
from daeso_nl.ga import feats
  

class _Descriptor(object):
    """
    Abstract class for feature descriptions
    
    A _Descriptor instance describes the features of a dataset (instances). The
    order is significant. It wraps an ordered dictionary where the keys are
    unique feature names and the values are Feat instances. Each Feat instance
    defines the properties of a feature (it's type, the associated feature
    function, etc.).
    """
    
    def __init__(self, features=()):
        """
        @param features: a iterable of Feat instances describing feature
        properties
        
        @return: a _Descriptor object
        """
        self._odict = OrderedDict()
        self.extend(features)

        
    def __getitem__(self, name):
        return self._odict[name]
        
        
    def __setitem__(self, name, feat):
        assert isinstance(feat, Feat)
        self._odict[name] = feat
        
        
    def __iter__(self):
        # in contrast to dict, iterates over values (i.e. features) rather
        # than keys (i.e. feature names)
        return iter(self._odict.values())
        
        
    def extend(self, features):
        for feat in features: 
            self[feat.name] = feat 

    
    @property       
    def descr(self):
        """
        return feature description as a Numpy field description
        (list of feature name and type pairs)
        """
        return [ (feat.name, feat.type)
                 for feat in self ]

    
    @property 
    def dtype(self):
        """
        return feature description as a Numpy dtype
        """
        return numpy.dtype(self.descr)

    
    def pprint(self, out=sys.stdout):
        """
        pretty print feature description
        """
        # feature properties are hard coded...
        out.write("No:".ljust(4) + "\t" +
                  "Name:".ljust(32) + "\t" +
                  "Type:".ljust(8) + "\t" +
                  "Metric:".ljust(8) + "\t" +
                  "Function:".ljust(32) + "\t" +
                  "Preprep graph hooks:".ljust(32) + "\t" +
                  "Preprep node hooks:\n")
            
        for i, feat in enumerate(self):
            pp_graph_hooks = ", ".join(obj.__name__
                                       for obj in feat.pp_graph_hooks)
            pp_node_hooks = ", ".join(obj.__name__
                                       for obj in feat.pp_node_hooks)
            out.write("%-4d\t%-32s\t%-8s\t%-8s\t%-32s\t%-32s\t%-32s\n"  % (
                i+1,
                feat.name,
                feat.type,
                feat.metric,
                feat.function.func_name,
                pp_graph_hooks,
                pp_node_hooks))
            
            
            
    
            
        
class Descriptor(_Descriptor):
    """
    A number of obligatory administrative features are automatically added. 
    
    At the head::
    
    1. source_node_count: counter of selected nodes from the source graph
    (starting at 1).
    
    2. target_node_count: counter of selected nodes from the target graph
    (starting at 1).
    
    3. source_node: source node (unique within the source graph)
    
    4. target_node: target node (unique within the target graph)
    
    In the middle columns are the features from the "features" argument 
    passed on initialization.
    
    At the tail:

    1. true_relation: the true alignment relation
    
    2. pred_relation: initial relation predicted by classifier
    
    3. pred_weight: weight associated with prediction
    
    4. match_relation: final relation after matching
    """
    
    head_feats = (
        feats.node_count +
        feats.node)
    
    tail_feats = (
            feats.pred_relation +
            feats.pred_weight + 
            feats.match_relation +
            feats.true_relation )
    
    
    def __init__(self, features=(), no_rel=str(None)):
        """
        @param features: a iterable of Feat instances describing feature
        properties

        @keyword no_rel: special relation label representing "no relation"
        
        @return: a Descriptor object
        """
        # using extend because features may be a generator object,
        # for which __add__ would fail
        _Descriptor.__init__(self, self.head_feats)
        self.extend(features)
        self.extend(self.tail_feats)
        self.no_rel = no_rel
        
        
        
    