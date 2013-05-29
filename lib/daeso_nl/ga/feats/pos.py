"""
pos features
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


def ff_source_pos(nodes, graphs, **kwargs):
    return graphs.source.node[nodes.source].get("pos") 

source_pos = Feat(ff_source_pos, "S10"),


def ff_target_pos(nodes, graphs, **kwargs):
    return graphs.target.node[nodes.target].get("pos") 

target_pos = Feat(ff_target_pos, "S10"),


def ff_same_pos(nodes, graphs, **kwargs):
    try:
        if ( graphs.source.node[nodes.source]["pos"]  ==
             graphs.target.node[nodes.target]["pos"] ):
            return "T"
        else:
            return "F"
    except KeyError:
        # non-terminal
        return "?"
    
same_pos = Feat(ff_same_pos, "S1"),


# content/function word

# doesn't work for auxiliary verbs, some functional adverbs, etc. 
content_pos = set("noun verb adj adv name".split()) 

def ff_source_content_word(nodes, graphs, **kwargs):
    try:
        if graphs.source.node[nodes.source]["pos"] in content_pos:
            return "T"
        else:
            return "F"
    except KeyError:
        return "-"
    
source_content_word = Feat(ff_source_content_word, "S1"),


def ff_target_content_word(nodes, graphs, **kwargs):
    try:
        if graphs.target.node[nodes.target]["pos"] in content_pos:
            return "T"
        else:
            return "F"
    except KeyError:
        return "-"
    
target_content_word = Feat(ff_target_content_word, "S1"),


def ff_both_content_word(nodes, graphs, **kwargs):
    try:
        if ( graphs.source.node[nodes.source]["pos"] in content_pos and
             graphs.target.node[nodes.target]["pos"] in content_pos ):
            return "T"
        else:
            return "F"
    except KeyError:
        # non-terminal
        return "?"
    
both_content_word = Feat(ff_both_content_word, "S1"),


# all pos features

pos = ( source_pos + 
        target_pos +
        same_pos +
        source_content_word +
        target_content_word +
        both_content_word )


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]





