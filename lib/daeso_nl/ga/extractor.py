"""
Extract features from (aligned) graphs
"""

import numpy
import networkx

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pair import Pair

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.descriptor import Descriptor

__all__ = [
    "Extractor",
    "select_graph_pair",
    "select_parsed_graph_pair",
    "select_aligned_graph_pair",
    "select_node",
    "select_visible_node",
    "select_lexical_node"
    ]


class Extractor(object):
    """
    Abstract class for feature extraction from a single graph pair
    
    A Extractor object is created from a Descriptor object, which
    defines the features, their format and the feature functions to extract
    feature values. In addition, it takes an optional node selector function
    which may be used to filter nodes.

    It provides an "extract" method which takes a pair of graphs and
    optionally a true node alignment. It then output instances for
    classification, one for each possible alignment of a source node to a
    target node, in the format of a Numpy record array. It also takes care of
    the preprocessing hooks for nodes and graphs.
    """
    
    def __init__(self, descriptor, node_selector=None):
        """
        Create a new Extractor object
        
        @param descriptor: a Descriptor object, which describes the features,
        their format and the feature functions to extract feature values.
        
        @keyword node_selector: boolean node selection function; see
        select_node method
        """
        assert isinstance(descriptor, Descriptor)
        self.descriptor = descriptor
        self.node_selector = node_selector or select_node
        self.pp_graph_hooks, self.pp_node_hooks = \
        self._collect_pp_hooks(descriptor)
    
    #---------------------------------------------------------------------------
    # preprocessing hooks
    #---------------------------------------------------------------------------
  
    def _collect_pp_hooks(self, descriptor):
        """
        collect all preprocessing hooks
        """
        pp_graph_hooks = set()
        pp_node_hooks = set()
        
        for feat in descriptor:
            pp_graph_hooks.update(feat.pp_graph_hooks)
            pp_node_hooks.update(feat.pp_node_hooks)
            
        return pp_graph_hooks, pp_node_hooks
    
    
    def _apply_pp_graph_hooks(self, graphs):
        """
        apply preprocessing graph hooks to graphs
        """
        for func in self.pp_graph_hooks:
            func(graphs)
            
    def _apply_pp_node_hooks(self, nodes, graphs, alignment):
        """
        apply preprocessing node hooks to nodes
        """
        for func in self.pp_node_hooks:
            func(nodes=nodes,
                 graphs=graphs, 
                 alignment=alignment)

    #---------------------------------------------------------------------------
    # extraction
    #---------------------------------------------------------------------------

    def extract(self, graph_pair):
        """
        Extract features from aligned graph pair, limiting scope to selected
        nodes
        
        @keyword graph_pair: an instance of GraphMapping. NB Any node alignment
        involving a filtered node (cf. node_selector) is removed from the
        alignment!
        
        @return: a numpy record array with an instance for each possible pair
        of selected source node and target node.
        """
        graphs = graph_pair.get_graphs()
        self._apply_pp_graph_hooks(graphs)
        instances = self._empty_instances(graphs)
        # source and target node counters, counting from one
        n_count = Pair(0, 0)
        # instance counter
        inst_count= 0
            
        for source_node in graphs.source:
            source_selected = self.node_selector(source_node, graphs.source)
            
            if source_selected: 
                n_count.source += 1
                
            n_count.target = 0
            
            for target_node in graphs.target:
                nodes = Pair(source_node, target_node)
                target_selected = self.node_selector(target_node,
                                                     graphs.target)
                
                if source_selected and target_selected:
                    self._apply_pp_node_hooks(nodes, graphs, graph_pair)
                    n_count.target += 1

                    for feat in self.descriptor:
                        # Each feature function is called with the node
                        # counters, a pair of nodes, a pair of graphs, and an
                        # alignment
                        instances[inst_count][feat.name] = feat.function(
                            n_count=n_count, 
                            nodes=nodes,
                            graphs=graphs, 
                            alignment=graph_pair)
                    inst_count += 1
                else:
                    # Remove alignment (if any) between skipped nodes from
                    # alignment, because it should not occur in the true pgc.
                    # A not so elegant side effect, but more effcient than
                    # updating the alignment afterwards.
                    try:
                        graph_pair.del_align(nodes)
                    except networkx.NetworkXError:
                        pass
                    
        # original ndarray was n x m, but actual size may be less due to node
        # selection, so here we get rid of empty rows at the bottom
        return instances[:inst_count]
    
    
    def _empty_instances(self, graphs):
        """
        create an empty numpy array of the maximum size needed
        """
        size = len(graphs.source) * len(graphs.target)
        return numpy.ndarray(size, dtype=self.descriptor.dtype)
    
    
#---------------------------------------------------------------------------
# Graph pair selection functions
#---------------------------------------------------------------------------
    
# Boolean graph pair selection functions which take a pair of graphs and
# return a truth value. These are used to filter graph pairs during corpus
# alignment and alignment experiments. Some of these may be depend on the
# parser (Alpino).

def select_graph_pair(graph_pair):
    """
    Graph selection function that accepts every graph pair
    
    @param graph_pair: a Pair of DaesoGraph instances
    
    @return: Boolean
    """
    return True


def select_parsed_graph_pair(graph_pair):
    """
    Graph selection function that accepts only graph pairs without failed
    parses
    
    @param graph_pair: a Pair of DaesoGraph instances
    
    @return: Boolean
    """
    from_graph, to_graph = graph_pair.get_graphs()
    if not ( from_graph.is_failed_parse() or
             to_graph.is_failed_parse() ):
        return True
        
        
def select_aligned_graph_pair(graph_pair):
    """
    Graph selection function that accepts only graph pairs with aligned root
    nodes and without failed parses
    
    @param graph_pair: a Pair of DaesoGraph instances
    
    @return: Boolean
    """
    if graph_pair.roots_aligned():
        from_graph, to_graph = graph_pair.get_graphs()
        if not ( from_graph.is_failed_parse() or
                 to_graph.is_failed_parse() ):
            return True
        

#---------------------------------------------------------------------------
# Node pair selection functions
#---------------------------------------------------------------------------

# Boolean node pair selection functions which takes a node and return a truth
# value. Some of these may be depend on the parser (Alpino). 

def select_node(node, graph):
    """
    Node selection function that accepts every node pair
    
    @param node: a node in the graph
    
    @param graph: a source or target graph
    
    @return: Boolean
    """
    return True


def select_visible_node(node, graph):
    """
    Node selection function that accepts visible nodes, excluding punctuation
    and empty nodes.
    
    @param node: a node in the graph
    
    @param graph: a source or target graph
    
    @return: Boolean
    """
    return ( not graph.node_is_punct(node) and
             not graph.node_is_index(node) )


def select_lexical_node(node, graph):
    """
    Node selection function that accepts visible terminal nodes, excluding
    punctuation and empty nodes.
    
    @param node: a node in the graph
    
    @param graph: a source or target graph
    
    @return: Boolean
    """
    return graph.node_is_terminal(node, with_punct=False,
                                  with_empty=False)


    