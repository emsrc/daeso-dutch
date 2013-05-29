"""
root features
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
# root
#-------------------------------------------------------------------------------

def ff_source_root(nodes, graphs, **kwargs):
    """
    lower-cased source root
    """
    try:
        return graphs.source.node[nodes.source]["root"].lower()
    except KeyError:
        # non-terminal
        pass

source_root = Feat(ff_source_root, "U24"),


def ff_target_root(nodes, graphs, **kwargs):
    """
    lower-cased target root
    """
    try:
        return graphs.target.node[nodes.target]["root"].lower()
    except KeyError:
        # non-terminal
        pass
        
target_root = Feat(ff_target_root, "U24"),


def ff_same_root(nodes, graphs, **kwargs):
    """
    same lower-cased root
    """
    # in order to avoid redundancy, do not use in combination with
    # root_subsumption
    try:
        if  ( graphs.source.node[nodes.source]["root"].lower() ==
              graphs.target.node[nodes.target]["root"].lower() ):
            return "T"
        else:
            return "F"
    except KeyError:
        # not a terminal
        return "?"  
        
same_root =  Feat(ff_same_root, "S1"),   


basic_root = source_root + target_root + same_root


#-------------------------------------------------------------------------
# Morphological analysis
#-------------------------------------------------------------------------

# Morphological is based on the value of the "root" attribute in Alpino
# parses. The parser performs some morphological analysis in terms of stems
# and inflectional/derivational affixes (although not always consistently).
# Phenomena addressed include:
# 
# * noun compounding: hoofd_lijn
# * compound verbs: schrijven_op
# * derivation: on_scherp, diepzinnig_heid
# * dmininutive: ziel_DIM, goochelen_kunst_DIM


def ff_roots_subsumption(nodes, graphs, **kwargs):
    """
    test for subsumption between root morhemes (if source morphemes form
    a prefix/suffix of the target morphemes, or vice versa)
    """
    # * the values are mutually exclusive
    # * with thsi feature, there is no need for ff_same_root
    source_root = graphs.source.node[nodes.source].get("root")
    target_root = graphs.target.node[nodes.target].get("root")
    
    if not source_root or not target_root:
        # non-terminal node(s) -- value undefined
        return "-"
    
    if source_root == target_root:
        # "wagen" equals "wagen"
        # "brandweer_wagen" equals "brandweer_wagen"
        return "equals"
    
    source_parts = source_root.split("_")
    target_parts = target_root.split("_")
    # don't bother to assign length to vars, because len(list) is O(1)
    
    if source_parts[:len(target_parts)] == target_parts:
        # "brandweer_wagen" has_prefix "brandweer"
        return "has_prefix"
        
    if source_parts == target_parts[:len(source_parts)]:
        # "brandweer" is_prefix "brandweer_wagen"
        return "is_prefix"
    
    if source_parts[-len(target_parts):] == target_parts:
        # "brandweer_wagen" has_suffix "wagen"
        return "has_suffix"
    
    if source_parts == target_parts[-len(source_parts):]:
        # wagen" is_suffix "brandweer_wagen"
        return "is_suffix"
    
    if len(source_parts) > len(target_parts):
        for i in range(1, len(source_parts) - len(target_parts)):
            if source_parts[i:i+len(target_parts)] == target_parts:
                # "fiets_ventiel_dopje" has_infix "ventiel"
                # "woon_wagen_bewoners_kamp_ingang" has_infix "wagen_bewoners"
                return "has_infix"
    else:
        for i in range(1, len(target_parts) - len(source_parts)):
            if source_parts == target_parts[i:i+len(source_parts)]:
                # "ventiel" is_infix "fiets_ventiel_dopje" 
                # "wagen_bewoners" is_infix "woon_wagen_bewoners_kamp_ingang"
                return "is_infix"
            
    # otherwise there is no subsumption
    return "none"

roots_subsumption =  Feat(ff_roots_subsumption, "S10"),     
                    


# The following three affix sharing features are not mutually exclusive 


def ff_roots_share_prefix(nodes, graphs, **kwargs):
    """
    test if root morphemes share a true prefix (excluding subsumption)
    """
    source_root = graphs.source.node[nodes.source].get("root")
    target_root = graphs.target.node[nodes.target].get("root")
    
    if not source_root or not target_root:
        # non-terminal node(s) -- value undefined
        return "-"
    
    source_parts = source_root.split("_")
    target_parts = target_root.split("_")

    if source_parts[0] == target_parts[0]:
        # check that at least one suffix is different
        for sp, tp in zip(source_parts[1:], target_parts[1:]):
            if sp != tp:
                # woon_wagen" / "woon_boot"
                return "T"
            
    # "woon_wagen" / "eet_tafel"
    # "woon_wagen" / "woon_wagen"
    # "woon_wagen" / "woon"
    return "F"

roots_share_prefix = Feat(ff_roots_share_prefix, "S1"),  
                    


def ff_roots_share_suffix(nodes, graphs, **kwargs):
    """
    test if root morphemes share a true suffix (excluding subsumption)
    """
    source_root = graphs.source.node[nodes.source].get("root")
    target_root = graphs.target.node[nodes.target].get("root")
    
    if not source_root or not target_root:
        # non-terminal node(s) -- value undefined
        return "-"
    
    source_parts = source_root.split("_")
    target_parts = target_root.split("_")

    if source_parts.pop() == target_parts.pop():
        # check that at least one prefix is different,
        # moving backwards
        while True:
            try:
                if source_parts.pop() != target_parts.pop():
                    # woon_wagen" / "mest_wagen"
                    return "T"
            except IndexError:
                break
            
    # "woon_wagen" / "eet_tafel"
    # "woon_wagen" / "woon_wagen"
    # "woon_wagen" / "wagen"
    return "F"

roots_share_suffix = Feat(ff_roots_share_suffix, "S1"),
        
        

def ff_roots_share_infix(nodes, graphs, **kwargs):
    """
    test if root morphemes share a true infix (excluding subsumption and
    sharing of only prefix/affix)
    """
    source_root = graphs.source.node[nodes.source].get("root")
    target_root = graphs.target.node[nodes.target].get("root")
    
    if not source_root or not target_root:
        # non-terminal node(s) -- value undefined
        return "-"
    
    source_parts = source_root.split("_")
    target_parts = target_root.split("_")
    
    for i in range(1, len(source_parts) - 1):
        for j in range(1, len(target_parts) - 1):
            if ( source_parts[i] == target_parts[j] and
                 # prefixes differ (always non-empty)
                 source_parts[:i] != target_parts[:j] and
                 # suffixes differ (always non-empty)
                 source_parts[i+1:] != target_parts[j+1:] ):
                return "T"

    return "F"

roots_share_infix = Feat(ff_roots_share_infix, "S1"),


root_morph = ( roots_subsumption + 
               roots_share_prefix +
               roots_share_infix +
               roots_share_suffix )


# all root features

all_root = ( basic_root +
         root_morph )

    

# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]

