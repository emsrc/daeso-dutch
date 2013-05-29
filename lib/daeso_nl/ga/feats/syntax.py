"""
syntactic features
"""

from daeso_nl.ga.feature import Feat


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

def pp_head(graphs):
    """
    A preprocessing functions that finds the head of a word/phrase.
    Adds a "head_n" attribute to nodes containing the head node.
    Value may be None for some nodes, .e.g. the root node.
    """
    for graph in graphs:
        for n in graph:
            graph.node[n]["head_n"] = graph.get_dep_head(n)
           

#-------------------------------------------------------------------------------
# cat
#-------------------------------------------------------------------------------


def ff_source_cat(nodes, graphs, **kwargs):
    return graphs.source.node[nodes.source].get("cat") 

source_cat = Feat(ff_source_cat, "S10"),


def ff_target_cat(nodes, graphs, **kwargs):
    return graphs.target.node[nodes.target].get("cat") 

target_cat = Feat(ff_target_cat, "S10"),



def ff_same_cat(nodes, graphs, **kwargs):
    try:
        if ( graphs.source.node[nodes.source]["cat"]  ==
             graphs.target.node[nodes.target]["cat"] ):
            return "T"
        else:
            return "F"
    except KeyError:
        # terminal
        return "?"
    
same_cat = Feat(ff_same_cat, "S1"),


cat = source_cat + target_cat + same_cat


#-------------------------------------------------------------------------------
# parent cat
#-------------------------------------------------------------------------------

def ff_source_parent_cat(nodes, graphs, **kwargs):
    # returns None for root
    n = graphs.source.get_parent_node(nodes.source)
    
    try:
        return graphs.source.node[n]["cat"]
    except KeyError:
        # root node
        pass

source_parent_cat = Feat(ff_source_parent_cat, "S8"),


def ff_target_parent_cat(nodes, graphs, **kwargs):
    # returns None for root
    n = graphs.target.get_parent_node(nodes.target)
    
    try:
        return graphs.target.node[n]["cat"]
    except KeyError:
        # root node
        pass

target_parent_cat = Feat(ff_target_parent_cat, "S8"),


def ff_same_parent_cat(nodes, graphs, **kwargs):
    n = graphs.source.get_parent_node(nodes.source)
    m = graphs.target.get_parent_node(nodes.target)
    
    try:
        if ( graphs.source.node[n]["cat"]  ==
             graphs.target.node[m]["cat"] ):
            return "T"
        else:
            return "F"
    except KeyError:
        # terminal
        return "?"
    
same_parent_cat = Feat(ff_same_parent_cat, "S1"),


parent_cat = source_parent_cat + target_parent_cat + same_parent_cat


#-------------------------------------------------------------------------------
# dependency relation
#-------------------------------------------------------------------------------

def ff_source_dep_rel(nodes, graphs, **kwargs):
    # returns None for root
    return graphs.source.get_node_deprel(nodes.source)

source_dep_rel = Feat(ff_source_dep_rel, "S8"),


def ff_target_dep_rel(nodes, graphs, **kwargs):
    # returns None for root
    return graphs.target.get_node_deprel(nodes.target)

target_dep_rel = Feat(ff_target_dep_rel, "S8"),


def ff_same_dep_rel(nodes, graphs, **kwargs):
    # returns "T" for root nodes
    if ( graphs.source.get_node_deprel(nodes.source)  ==
         graphs.target.get_node_deprel(nodes.target) ):
        return "T"
    else:
        return "F"
    
same_dep_rel = Feat(ff_same_dep_rel, "S1"),


dep_rel = source_dep_rel + target_dep_rel + same_dep_rel


#-------------------------------------------------------------------------------
# dependency head
#-------------------------------------------------------------------------------

def ff_source_dep_head_root(nodes, graphs, **kwargs):
    head_n = graphs.source.node[nodes.source]["head_n"] 
    
    try:
        return graphs.source.node[head_n]["root"].lower()
    except KeyError:
        # head_n is None or head_n is a non-terminal (?)
        pass

source_dep_head_root = Feat(ff_source_dep_head_root, "U24",
                            pp_graph_hooks=[pp_head]),



def ff_target_dep_head_root(nodes, graphs, **kwargs):
    head_n = graphs.target.node[nodes.target]["head_n"] 
    
    try:
        return graphs.target.node[head_n]["root"].lower()
    except KeyError:
        # head_n is None or head_n is a non-terminal (?)
        pass

target_dep_head_root = Feat(ff_target_dep_head_root, "U24",
                            pp_graph_hooks=[pp_head]),


def ff_same_dep_head_root(nodes, graphs, **kwargs):
    """
    same lower-cased dependency head root
    """
    source_head = graphs.source.node[nodes.source]["head_n"] 
    target_head = graphs.target.node[nodes.target]["head_n"] 
    
    try:
        if  ( graphs.source.node[source_head]["root"].lower() ==
              graphs.target.node[target_head]["root"].lower() ):
            return "T"
        else:
            return "F"
    except KeyError:
        # not a terminal
        return "?"  
        
same_dep_head_root =  Feat(ff_same_dep_head_root, "S1",
                           pp_graph_hooks=[pp_head]),   


dep_head_root = ( source_dep_head_root + 
                  target_dep_head_root + 
                  same_dep_head_root )



# all syntactic features

syntax = ( cat +
           parent_cat +
           dep_rel +
           dep_head_root )



# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]
