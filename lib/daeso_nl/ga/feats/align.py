"""
alignment features
"""

from daeso.pair import Pair
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


def pp_yield(graphs):
    """
    A graph preprocessing function that calculates the terminal yields of
    non-terminal nodes
    """
    for graph in graphs:
        terminal_yield(graph, graph.root)
    
    
def terminal_yield(graph, n):
    try:
        # node already seen (should not happen in trees)
        return graph.node[n]["_yield"]
    except KeyError:
        graph.node[n]["_yield"] = set()
        
        if graph.node_is_terminal(n, with_empty=False, with_punct=False):
            graph.node[n]["_yield"].add(n)
        else:
            for m in graph.successors(n):
                graph.node[n]["_yield"].update(terminal_yield(graph, m))
        
        return graph.node[n]["_yield"]
    
    
def pp_term_align(nodes, graphs, alignment, **kwargs):
    """
    A node preprocessing function that computes the number of aligned
    terminals for a given pair of source and target nodes.
    
    Assumes the "_yield" attribute on nodes as computed by the pp_yield grap
    preprocessing functions.

    Provides the node attributes:
    _inside:  terminals aligned to terminals inside the other node
    _outside: aligned outside the other node or aligned to non-terminals
    _none:    unaligned terminals 
    
    """
    sn_attr = graphs.source.node[nodes.source]
    tn_attr = graphs.target.node[nodes.target]

    # handle source node
    sn_attr["_inside"] = {}
    sn_attr["_outside"] = []
    sn_attr["_none"] = []
    
    for st in sn_attr["_yield"]:
        # find aligned target node, if any
        tt = alignment.get_aligned_target_node(st)
        
        if tt:
            if tt in tn_attr["_yield"]:
                relation = alignment.get_align(Pair(st, tt))
                
                try:
                    sn_attr["_inside"][relation].append(st)
                except KeyError:
                    sn_attr["_inside"][relation] = [st]
            else:
                # if non-terminal alignments are available,
                # this includes all cases where a source terminal is aligned
                # to target *non-terminal*, even if it is within the scope of
                # nodes.target!
                sn_attr["_outside"].append(st)
        else:
            sn_attr["_none"].append(st)

    # handle target node
    # align inside count is by definition identical for source an target node
    tn_attr["_inside"] = sn_attr["_inside"]
    tn_attr["_outside"] = []
    tn_attr["_none"] = []
            
    for tt in tn_attr["_yield"]:
        # find aligned source node, if any
        st = alignment.get_aligned_source_node(tt)
        
        if st:
            if st not in sn_attr["_yield"]:
                # if non-terminal alignments are available,
                # this includes all case where a target terminal is aligned to
                # source *non-terminal*, even if it is within the scope of
                # nodes.source!
                tn_attr["_outside"].append(tt)
        else:
            tn_attr["_none"].append(tt)
            
    

#-------------------------------------------------------------------------------
# Terminal alignments
#-------------------------------------------------------------------------------

# overall counts

def ff_align_inside_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return sum([ len(l) 
                 for l in attr["_inside"].values() ])
            
align_inside_count= Feat(ff_align_inside_count, "i", "N",
                         pp_graph_hooks=[pp_yield],
                         pp_node_hooks=[pp_term_align]),



def ff_source_align_outside_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_outside"])
            
source_align_outside_count= Feat(ff_source_align_outside_count, "i", "N",
                                 pp_graph_hooks=[pp_yield],
                                 pp_node_hooks=[pp_term_align]),


def ff_target_align_outside_count(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_outside"])

target_align_outside_count= Feat(ff_target_align_outside_count, "i", "N",
                                 pp_graph_hooks=[pp_yield],
                                 pp_node_hooks=[pp_term_align]),



def ff_source_align_none_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_none"])
            
source_align_none_count= Feat(ff_source_align_none_count, "i", "N",
                              pp_graph_hooks=[pp_yield],
                              pp_node_hooks=[pp_term_align]),


def ff_target_align_none_count(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_none"])
            
target_align_none_count= Feat(ff_target_align_none_count, "i", "N",
                              pp_graph_hooks=[pp_yield],
                              pp_node_hooks=[pp_term_align]),


term_align_count = (
    align_inside_count +
    source_align_outside_count +
    target_align_outside_count +
    source_align_none_count +
    target_align_none_count
    )



# overall percentages

def ff_source_align_inside_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    count = sum([ len(l) 
                  for l in attr["_inside"].values() ]) 
    return count / float(len(attr["_yield"]))
            
source_align_inside_percent= Feat(ff_source_align_inside_percent, "f8", "N",
                                  pp_graph_hooks=[pp_yield],
                                  pp_node_hooks=[pp_term_align]),


def ff_target_align_inside_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    count = sum([ len(l) 
                  for l in attr["_inside"].values() ]) 
    return count / float(len(attr["_yield"]))
            
target_align_inside_percent= Feat(ff_target_align_inside_percent, "f8", "N",
                                  pp_graph_hooks=[pp_yield],
                                  pp_node_hooks=[pp_term_align]),



def ff_source_align_outside_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_outside"]) / float(len(attr["_yield"]))
            
source_align_outside_percent= Feat(ff_source_align_outside_percent, "f8", "N",
                                   pp_graph_hooks=[pp_yield],
                                   pp_node_hooks=[pp_term_align]),


def ff_target_align_outside_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_outside"]) / float(len(attr["_yield"]))

target_align_outside_percent= Feat(ff_target_align_outside_percent, "f8", "N",
                                   pp_graph_hooks=[pp_yield],
                                   pp_node_hooks=[pp_term_align]),



def ff_source_align_none_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_none"]) / float(len(attr["_yield"]))
            
source_align_none_percent= Feat(ff_source_align_none_percent, "f8", "N",
                                pp_graph_hooks=[pp_yield],
                                pp_node_hooks=[pp_term_align]),


def ff_target_align_none_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_none"]) / float(len(attr["_yield"]))
            
target_align_none_percent= Feat(ff_target_align_none_percent, "f8", "N",
                                pp_graph_hooks=[pp_yield],
                                pp_node_hooks=[pp_term_align]),


term_align_percent = (
    source_align_inside_percent +
    target_align_inside_percent +
    source_align_outside_percent +
    target_align_outside_percent +
    source_align_none_percent +
    target_align_none_percent
    )



# inside counts per relation

def ff_align_inside_eq_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("equals", []))
            
align_inside_eq_count= Feat(ff_align_inside_eq_count, "i", "N",
                            pp_graph_hooks=[pp_yield],
                            pp_node_hooks=[pp_term_align]),


def ff_align_inside_re_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("restates", []))
            
align_inside_re_count= Feat(ff_align_inside_re_count, "i", "N",
                            pp_graph_hooks=[pp_yield],
                            pp_node_hooks=[pp_term_align]),


def ff_align_inside_spec_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("specifies", []))
            
align_inside_spec_count= Feat(ff_align_inside_spec_count, "i", "N",
                              pp_graph_hooks=[pp_yield],
                              pp_node_hooks=[pp_term_align]),


def ff_align_inside_gen_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("generalizes", []))
            
align_inside_gen_count= Feat(ff_align_inside_gen_count, "i", "N",
                             pp_graph_hooks=[pp_yield],
                             pp_node_hooks=[pp_term_align]),


def ff_align_inside_int_count(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("intersects", []))
            
align_inside_int_count= Feat(ff_align_inside_int_count, "i", "N",
                             pp_graph_hooks=[pp_yield],
                             pp_node_hooks=[pp_term_align]),

term_align_inside_rel_count = (
    align_inside_eq_count +
    align_inside_re_count +
    align_inside_spec_count +
    align_inside_gen_count +
    align_inside_int_count )



# inside percentages per relation, source

def ff_source_align_inside_eq_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("equals", [])) / float(len(attr["_yield"]))
            
source_align_inside_eq_percent= Feat(ff_source_align_inside_eq_percent,
                                     "f8", "N",
                                     pp_graph_hooks=[pp_yield],
                                     pp_node_hooks=[pp_term_align]),


def ff_source_align_inside_re_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("restates", [])) / float(len(attr["_yield"]))
            
source_align_inside_re_percent= Feat(ff_source_align_inside_re_percent, 
                                     "f8", "N",
                                     pp_graph_hooks=[pp_yield],
                                     pp_node_hooks=[pp_term_align]),


def ff_source_align_inside_spec_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("specifies", [])) / float(len(attr["_yield"]))
            
source_align_inside_spec_percent= Feat(ff_source_align_inside_spec_percent, 
                                       "f8", "N",
                                       pp_graph_hooks=[pp_yield],
                                       pp_node_hooks=[pp_term_align]),


def ff_source_align_inside_gen_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("generalizes", [])) / float(len(attr["_yield"]))
            
source_align_inside_gen_percent= Feat(ff_source_align_inside_gen_percent, 
                                      "f8", "N",
                                      pp_graph_hooks=[pp_yield],
                                      pp_node_hooks=[pp_term_align]),


def ff_source_align_inside_int_percent(nodes, graphs, **kwargs):
    attr = graphs.source.node[nodes.source]
    return len(attr["_inside"].get("intersects", [])) / float(len(attr["_yield"]))
            
source_align_inside_int_percent= Feat(ff_source_align_inside_int_percent, 
                                      "f8", "N",
                                      pp_graph_hooks=[pp_yield],
                                      pp_node_hooks=[pp_term_align]),

term_source_align_inside_rel_percent = (
    source_align_inside_eq_percent +
    source_align_inside_re_percent +
    source_align_inside_spec_percent +
    source_align_inside_gen_percent +
    source_align_inside_int_percent )


# inside percentages per relation, target

def ff_target_align_inside_eq_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_inside"].get("equals", [])) / float(len(attr["_yield"]))
            
target_align_inside_eq_percent= Feat(ff_target_align_inside_eq_percent,
                                     "f8", "N",
                                     pp_graph_hooks=[pp_yield],
                                     pp_node_hooks=[pp_term_align]),


def ff_target_align_inside_re_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_inside"].get("restates", [])) / float(len(attr["_yield"]))
            
target_align_inside_re_percent= Feat(ff_target_align_inside_re_percent, 
                                     "f8", "N",
                                     pp_graph_hooks=[pp_yield],
                                     pp_node_hooks=[pp_term_align]),


def ff_target_align_inside_spec_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_inside"].get("specifies", [])) / float(len(attr["_yield"]))
            
target_align_inside_spec_percent= Feat(ff_target_align_inside_spec_percent, 
                                       "f8", "N",
                                       pp_graph_hooks=[pp_yield],
                                       pp_node_hooks=[pp_term_align]),


def ff_target_align_inside_gen_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_inside"].get("generalizes", [])) / float(len(attr["_yield"]))
            
target_align_inside_gen_percent= Feat(ff_target_align_inside_gen_percent, 
                                      "f8", "N",
                                      pp_graph_hooks=[pp_yield],
                                      pp_node_hooks=[pp_term_align]),


def ff_target_align_inside_int_percent(nodes, graphs, **kwargs):
    attr = graphs.target.node[nodes.target]
    return len(attr["_inside"].get("intersects", [])) / float(len(attr["_yield"]))
            
target_align_inside_int_percent= Feat(ff_target_align_inside_int_percent, 
                                      "f8", "N",
                                      pp_graph_hooks=[pp_yield],
                                      pp_node_hooks=[pp_term_align]),

term_target_align_inside_rel_percent = (
    target_align_inside_eq_percent +
    target_align_inside_re_percent +
    target_align_inside_spec_percent +
    target_align_inside_gen_percent +
    target_align_inside_int_percent )


term_align_inside_rel_percent = (
    term_source_align_inside_rel_percent +
    term_target_align_inside_rel_percent )




# all

term_align_count = (
    term_align_count +
    term_align_inside_rel_count 
    )
    
term_align_percent = (
    term_align_percent +
    term_align_inside_rel_percent
    )

term_align = (
    term_align_count +
    term_align_percent
    )


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]





