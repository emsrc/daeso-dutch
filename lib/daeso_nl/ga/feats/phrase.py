"""
phrase features
"""

from daeso.pair import Pair
from daeso_nl.ga.feature import Feat
from daeso.thirdparty.counter import Counter


# All global variables define feature *tuples*, 
# so it's easy to concatenate features using "+".

# A feature function (ff) is always called as:
#
# ff( n_count = Pair(source_node_count, target_node_count),
#     nodes = Pair(source_node, target_node),
#     graphs = Pair(source_graph, target_graph),
#     alignment = Graphpair )


# *********************************************************************
# Make sure that all values of string-valued features fit it the number
# of chars reserved for it in Numpy record! (e.g. "S10")
# Otherwise, they will get truncated, which is especially harmfull to 
# relation fields (e.g. pred_relation") during evaluation.
# *********************************************************************


#-------------------------------------------------------------------------------
# Preprocessing functions
#-------------------------------------------------------------------------------

def pp_phrase(graphs):
    """
    A preprocessing function that adds attributes to nodes
    
    1. lc_tokens: lower-cased tokens
    2. bag: bag/multi-set/counter of lower-cased tokens
    """
    for graph in graphs:
        for n in graph:
            lc_tokens = [ t.lower() for t in graph.node[n]["tokens"] ]
            graph.node[n]["lc_tokens"] = lc_tokens
            graph.node[n]["bag"] = Counter(lc_tokens)
            
            

#-------------------------------------------------------------------------------
# Basic
#-------------------------------------------------------------------------------

# FIXME: calculating the intersection twice is ineffecient... 

def ff_token_prec(nodes, graphs, **kwargs):
    """
    precision on tokens, regarding the source tokens as "true" and the target
    tokens as "predicted"  (all lower-cased)
    """
    target_bag = graphs.target.node[nodes.target]["bag"]

    if not target_bag: 
        # prevent zero-division
        return 0.0
        
    source_bag = graphs.source.node[nodes.source]["bag"]
    common_size = sum(source_bag.__and__(target_bag).values())
    target_size = float(len(graphs.target.node[nodes.target]["tokens"]))
    
    return common_size / target_size 
    
token_prec = Feat( ff_token_prec, "f8", "N", pp_graph_hooks=[pp_phrase]),



def ff_token_rec(nodes, graphs, **kwargs):
    """
    recall on tokens, regarding the source tokens as "true" and the target
    tokens as "predicted" (all lower-cased)
    """
    source_bag = graphs.source.node[nodes.source]["bag"]

    if not source_bag: 
        # prevent zero-division
        return 0.0

    target_bag = graphs.target.node[nodes.target]["bag"]
    common_size = sum(source_bag.__and__(target_bag).values())
    source_size = float(len(graphs.source.node[nodes.source]["tokens"]))
    
    return common_size / source_size 
    
token_rec = Feat( ff_token_rec, "f8", "N", pp_graph_hooks=[pp_phrase]),



def ff_same_lc_phrase(nodes, graphs, **kwargs):
    """
    same lower-cased phrase
    """
    try:
        if ( graphs.source.node[nodes.source]["lc_tokens"] ==
             graphs.target.node[nodes.target]["lc_tokens"] ):
            return "T"
        else:
            return "F"
    except KeyError:
        # should not happen
        return "?"
    
same_phrase = Feat( ff_same_lc_phrase, "S1",
                    pp_graph_hooks=[pp_phrase]),

# lenght

def ff_source_phrase_len(nodes, graphs, **kwargs):
    return len(graphs.source.node[nodes.source]["tokens"])

source_phrase_len = Feat(ff_source_phrase_len, "i", "N"),


def ff_target_phrase_len(nodes, graphs, **kwargs):
    return len(graphs.target.node[nodes.target]["tokens"])

target_phrase_len = Feat(ff_target_phrase_len, "i", "N"),


def ff_phrase_len_diff(nodes, graphs, **kwargs):
    # may return negative values
    return ( len(graphs.source.node[nodes.source]["tokens"]) - 
             len(graphs.target.node[nodes.target]["tokens"]) )

phrase_len_diff = Feat(ff_phrase_len_diff, "i", "N"),

phrase_len = source_phrase_len + target_phrase_len + phrase_len_diff


#-------------------------------------------------------------------------------
# parent phrases
#-------------------------------------------------------------------------------

def ff_same_parent_lc_phrase(nodes, graphs, **kwargs):
    """
    parent nodes have same lower-cased phrase
    """
    parent_nodes = Pair(
        graphs.source.get_parent_node(nodes.source),
        graphs.target.get_parent_node(nodes.target))
    
    return ff_same_lc_phrase(parent_nodes, graphs)
    
same_parent_phrase = Feat( ff_same_parent_lc_phrase, "S1",
                           pp_graph_hooks=[pp_phrase]),



# all phrase features

phrase = ( token_prec +
           token_rec +
           same_phrase +
           same_parent_phrase +
           phrase_len )


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]









