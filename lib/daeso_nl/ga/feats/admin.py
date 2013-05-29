"""
administrative features
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
# Administrative features
#-------------------------------------------------------------------------------

# node count

def ff_source_node_count(n_count, **kwargs):
    """
    source node counter (counting from one)
    """
    return n_count.source

source_node_count = Feat(ff_source_node_count, "i", "I"),


def ff_target_node_count(n_count, **kwargs):
    """
    target node counter (counting from one)
    """
    return n_count.target

target_node_count = Feat(ff_target_node_count, "i", "I"),

node_count = source_node_count + target_node_count


# node

def ff_source_node(nodes, **kwargs):
    """
    source node (unique within graph)
    """
    return nodes.source

source_node = Feat(ff_source_node, "S4", "I"),


def ff_target_node(nodes, **kwargs):
    """
    target node (unique within graph)
    """
    return nodes.target

target_node = Feat( ff_target_node, "S4", "I"),


node = source_node + target_node


# predictions

def ff_pred_relation(**kwargs):
    """
    placeholder for the alignment relation predicted by Timbl
    """
    return None

pred_relation = Feat( ff_pred_relation, "S12", "I"),


def ff_pred_weight(**kwargs):
    """
    placeholder for the weight (confidence) of the predicted relation
    """
    return 0.0

pred_weight = Feat( ff_pred_weight, "f8", "I"),


def ff_match_relation(**kwargs):
    """
    placeholder for matched relation
    """
    return None

match_relation = Feat( ff_match_relation, "S12","I"),


# true relation

def ff_true_relation(nodes, alignment, **kwargs):
    """
    the true alignment relation between the source and target node
    (usually None)
    """
    return alignment.get_align(nodes)

true_relation = Feat(ff_true_relation,  "S12", None),


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]
