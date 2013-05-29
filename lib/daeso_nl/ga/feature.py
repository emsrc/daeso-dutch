"""
Properties of a single feature
"""

from daeso.exception import DaesoError


def ff_none(*args, **kwargs):
    """
    the none feature function
    """
    # returning zero is OK for int, float and string valued features
    return 0            


class Feat(object):
    """
    A Feat instance represents the general properties of a feature (apart from
    its value in a particular instance)
    """
    
    def __init__(self, function=ff_none, type="i", metric="O",
                 name=None, pp_graph_hooks=[], pp_node_hooks=[]):
        """
        @keyword function: feature function which is called to compute the
        feature's value in a particular instance
                
        @keyword type: Numpy data type
        
        @keyword metric: Timbl feature metric (e.g. "O","N", ...).
        
        @keyword name: alternative feature name; by default the feature name
        is derived from the name of the feature function by striping the
        initial "ff_" string        
        
        @keyword pp_graph_hooks: a list op preprocessing hooks, where each
        preprocesing function takes a pair of source and target graphs as
        input
        
        @keyword pp_node_hooks: a list op preprocessing hooks, where each
        preprocesing function takes a pair of source and target nodes as
        input
        """  
        self.type = type
        self.function = function
        self.init_metric = self.metric = metric
        self.pp_graph_hooks = pp_graph_hooks
        self.pp_node_hooks = pp_node_hooks
        
        if name:
            self.name = name
        elif function.__name__.startswith("ff_"):
            self.name = function.__name__[3:]
        else:
            raise DaesoError("cannot infer feature name from function named "
                             + function.__name__)
        
        
    def hide(self):
        """
        hide feature for Timbl by setting the feature metric to "I"
        """
        self.metric = "I"
        
        
    def restore(self):
        """
        restore feature to Timbl by restoring the initial feature metric
        """
        self.metric = self.init_metric
    
        
    def __repr__(self):
        return ( "Feat(" + 
                 ", ".join(str(attr) + "=" + repr(val) 
                           for attr, val in self.__dict__.items()) +
                 ")" )
        
    
    def __str__(self):
        return self.__repr__()
    
    
    
def hide(features):
    """
    hide features for Timbl by setting all feature metrics to "I"
    
    @param features: a sequence of Feat instances 
    """
    for feat in features:
        feat.hide()
        
        
def restore(features):
    """
    restore features for Timbl by restoring all initial feature metrics
    
    @param features: a sequence of Feat instances 
    """
    for feat in features:
        feat.restore()
        
        
        
def dummify(features):
    """
    Turns features into dummy's by replacing their feature function by a zero
    function, deleting their preprocessing hooks. It does not change the feature name or type.
    
    @param features: tuple of Feat instances
    
    @return: tuple of modified copies of the orginal features
    """
    return tuple( Feat(type=feat.type,
                       metric=feat.metric,
                       name=feat.name)
                  for feat in features )


        
   