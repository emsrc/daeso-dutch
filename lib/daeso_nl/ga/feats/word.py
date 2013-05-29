"""
word features
"""

from daeso.string.lcs import lcs

from daeso_nl.ga.feature import Feat
from daeso_nl.string.stopword import stopwords

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


def pp_words(graphs):
    """
    A preprocessng function that adds two attributes to terminal nodes:
    
    1. "lc_word" (str): lower-cased version of word
    
    2. "type_count" (int): count of lower-cased word among all the lower-cased
    tokens of the graph
    
    In addition, it adds an attribute "lc_tokens" to graphs, which is a list
    of lower-cased tokens.
    """
    for graph in graphs:
        # TODO use collections.Counter for this in Python >= 2.7 
        type_count = {}
        lc_graph_tokens = []
       
        # count the number of occurrences of each lower cased token
        for token in graph.tokens:
            lc_token = token.lower()
            lc_graph_tokens.append(lc_token)
            type_count[lc_token] = type_count.get(lc_token, 0) + 1
            
        for n in graph:
            try:
                lc_word = graph.node[n]["word"].lower()
            except KeyError:
                pass
            else:
                graph.node[n]["lc_word"] = lc_word
                # FIXME: lc_word should always be in the type_count dict;
                # however, there are still some tokenization/char encoding
                # errors in the ma autosub nos segment which cause broken 
                # words (e.g. "enqu tecommissie" 
                graph.node[n]["type_count"] = type_count.get(lc_word, 1)
                
        graph.graph["lc_tokens"] = lc_graph_tokens



#-------------------------------------------------------------------------------
# Basic
#-------------------------------------------------------------------------------


def ff_source_word(nodes, graphs, **kwargs):
    return graphs.source.node[nodes.source].get("word")

source_word = Feat(ff_source_word, "U24"),


def ff_target_word(nodes, graphs, **kwargs):
    return graphs.target.node[nodes.target].get("word")

target_word = Feat(ff_target_word, "U24"),

basic_word = source_word + target_word



def ff_source_lc_word(nodes, graphs, **kwargs):
    return graphs.source.node[nodes.source]["lc_word"]

source_lc_word = Feat(ff_source_lc_word, "U24"),


def ff_target_lc_word(nodes, graphs, **kwargs):
    return graphs.target.node[nodes.target]["lc_word"]

target_lc_word = Feat(ff_target_lc_word, "U24"),


def ff_same_lc_word(nodes, graphs, **kwargs):
    """
    same lower-cased word
    """
    # to avoid redundancy in encoding "equals", do not use in combination with
    # words_subsumption
    try:
        if ( graphs.source.node[nodes.source]["lc_word"] ==
             graphs.target.node[nodes.target]["lc_word"] ):
            return "T"
        else:
            return "F"
    except KeyError:
        # not a terminal node(s)
        return "?"
    
same_lc_word = Feat( ff_same_lc_word, "S1",
                     pp_graph_hooks=[pp_words]),


basic_lc_word = ( source_lc_word + 
                  target_lc_word +
                  same_lc_word )


# length

def ff_source_word_len(nodes, graphs, **kwargs):
    return len(graphs.source.node[nodes.source].get("word", ""))

source_word_len = Feat(ff_source_word_len, "i", "N"),


def ff_target_word_len(nodes, graphs, **kwargs):
    return len(graphs.target.node[nodes.target].get("word", ""))

target_word_len = Feat(ff_target_word_len, "i", "N"),


def ff_word_len_diff(nodes, graphs, **kwargs):
    return ( ff_source_word_len(nodes, graphs) - 
             ff_target_word_len(nodes, graphs) )

word_len_diff = Feat(ff_word_len_diff, "i", "N"),


word_len = ( source_word_len + 
             target_word_len + 
             word_len_diff )


#-------------------------------------------------------------------------------
# stop word
#-------------------------------------------------------------------------------

stopwords = set(stopwords)

def ff_source_stopword(nodes, graphs, **kwargs):
    """
    test if lower-cased source word is a stop word
    """
    # relies on pp_words preprocessing hook 
    try:
        if graphs.source.node[nodes.source]["lc_word"] in stopwords:
            return "T"
        else:
            return "F"
    except KeyError:
        # not-terminal node
        return "?"
    
source_stopword = Feat(ff_source_stopword, "S1",
                       pp_graph_hooks=[pp_words]),


def ff_target_stopword(nodes, graphs, **kwargs):
    """
    test if lower-cased target word is a stop word
    """
    # relies on pp_words preprocessing hook 
    try:
        if graphs.target.node[nodes.target]["lc_word"] in stopwords:
            return "T"
        else:
            return "F"
    except KeyError:
        # not-terminal node
        return "?"
    
target_stopword = Feat(ff_target_stopword, "S1",
                       pp_graph_hooks=[pp_words]),


stopword = ( 
    source_stopword + 
    target_stopword )


#-------------------------------------------------------------------------------
# word overlap (string overlap)
#-------------------------------------------------------------------------------

def ff_words_subsumption(nodes, graphs, **kwargs):
    """
    test for subsumption between lower-cased words (that is, if source word
    forms a prefix/suffix of the target word, or vice versa)
    """
    # * the values are mutually exclusive
    # * with this feature, there is no need for ff_same_lc_word
    source_word = graphs.source.node[nodes.source].get("lc_word")
    target_word = graphs.target.node[nodes.target].get("lc_word")
    
    if not source_word or not target_word:
        # non-terminal node(s) -- value undefined
        return "-"
    
    if source_word == target_word:
        # "wagen" equals "wagen"
        # "brandweer_wagen" equals "brandweer_wagen"
        return "equals"
    
    if source_word.startswith(target_word):
        # "brandweerwagen" has_prefix "brandweer"
        return "has_prefix"
        
    if target_word.startswith(source_word):
        # "brandweer" is_prefix "brandweerwagen"
        return "is_prefix"
    
    if source_word.endswith(target_word):
        # "brandweer_wagen" has_suffix "wagen"
        return "has_suffix"
    
    if target_word.endswith(source_word):
        # wagen" is_suffix "brandweer_wagen"
        return "is_suffix"
    
    if target_word in source_word:
        return "has_infix"

    if source_word in target_word:
        return "is_infix"
            
    # otherwise there is no subsumption
    return "none"

words_subsumption =  Feat(ff_words_subsumption, "S10",
                          pp_graph_hooks=[pp_words]),     
                    



def ff_words_shared_prefix_len(nodes, graphs, **kwargs):
    """
    Return the length in chars of the shared true prefix between the
    lower-cased source and target word. However, in order to avoid redundancy
    between features (i.e. to not encode "equals"), zero is returned whenever
    one word is fully contained in (or equal to) the other.
    """
    source_word = graphs.source.node[nodes.source].get("lc_word", "")
    target_word = graphs.target.node[nodes.target].get("lc_word", "")

    # prevent spurious prefix
    if ( source_word in target_word or
         target_word in source_word ):
        return 0
    
    i = 0
    
    for sc, tc in zip(source_word, target_word):
        if sc == tc:
            i += 1
        else:
            break
        
    return i

words_shared_prefix_len = Feat(ff_words_shared_prefix_len, "i", "N",
                               pp_graph_hooks=[pp_words]),  



def ff_words_shared_suffix_len(nodes, graphs, **kwargs):
    """
    Return the length in chars of the shared true suffix between the
    lower-cased source and target word. However, in order to avoid redundancy
    between features (i.e. to not encode "equals"), zero is returned whenever
    one word is fully contained in (or equal to) the other.
    """
    source_word = graphs.source.node[nodes.source].get("lc_word", "")
    target_word = graphs.target.node[nodes.target].get("lc_word", "")
    
    # prevent spurious prefix
    if ( source_word in target_word or
         target_word in source_word ):
        return 0
    
    i = 0
    
    for i in range(1, min(len(source_word), len(target_word)) + 1):
        if source_word[-i] != target_word[-i]:
            break
    
    return i

words_shared_suffix_len = Feat(ff_words_shared_suffix_len, "i", "N",
                               pp_graph_hooks=[pp_words]),  



def ff_words_shared_infix_len(nodes, graphs, **kwargs):
    """
    Return the length in chars of the shared true infix between the
    lower-cased source and target word, which equals the length of the longest
    common subsequence. However, in order to avoid redundancy between features
    (i.e. to not encode "equals"), zero is returned whenever one word is fully
    contained in (or equal to) the other.
    """
    # this probably an expensive feature
    source_word = graphs.source.node[nodes.source].get("lc_word", "")
    target_word = graphs.target.node[nodes.target].get("lc_word", "")
    
    # prevent spurious prefix
    if ( source_word in target_word or
         target_word in source_word ):
        return 0
    
    return len(lcs(source_word, target_word))

words_shared_infix_len = Feat(ff_words_shared_infix_len, "i", "N",
                              pp_graph_hooks=[pp_words]),



word_overlap = ( words_subsumption +
                 words_shared_prefix_len +
                 words_shared_infix_len +
                 words_shared_suffix_len )



#-------------------------------------------------------------------------------
# Unique
#-------------------------------------------------------------------------------

# FIXME: this is rather inefficient...


def ff_source_word_uniq(nodes, graphs, **kwargs):
    """
    test if lower-cased source word is unique among the lower-cased tokens of
    the source sentence
    """
    # relies on pp_words preprocessing hook 
    try:
        if graphs.source.node[nodes.source]["type_count"] == 1:
            return "T"
        else:
            return "F"
    except KeyError:
        # not-terminal node
        return "?"
    
source_word_uniq = Feat( ff_source_word_uniq, "S1",
                         pp_graph_hooks=[pp_words]),


def ff_target_word_uniq(nodes, graphs, **kwargs):
    """
    test if lower-cased target word is unique among the lower-cased tokns of
    the target sentence
    """
    # relies on pp_words preprocessing hook 
    try:
        if graphs.target.node[nodes.target]["type_count"] == 1:
            return "T"
        else:
            return "F"
    except KeyError:
        # not-terminal node
        return "?"
    
target_word_uniq = Feat( ff_target_word_uniq, "S1",
                         pp_graph_hooks=[pp_words]),


word_uniq = source_word_uniq + target_word_uniq


#-------------------------------------------------------------------------------
# word context
#-------------------------------------------------------------------------------


# Notes:
# * These features look at the Alpino "begin" and "end" attributes and the graph
#   tokens, rather than at individual node tokens, which may sometimes be
#   different.
# * Punctuation is included and nothing smart is done to ignore it.  


def ff_same_words_lhs(nodes, graphs, **kwargs):
    """
    return the number of equal lower-cased words at the left-hand side in the
    surface string
    """
    # also works for non-terminals
    source_tokens = graphs.source.graph["lc_tokens"]
    target_tokens = graphs.target.graph["lc_tokens"]
    source_index = int(graphs.source.node[nodes.source].get("begin"))
    target_index = int(graphs.target.node[nodes.target].get("begin"))
    same = 0

    while source_index >= 0 and target_index >= 0:
        if ( source_tokens[source_index] == 
             target_tokens[target_index] ):
            same += 1
        else:
            break

        source_index -= 1
        target_index -= 1
        
    #if same:
    #    print "same_word_lhs", same
    #    print graphs.source.node[nodes.source]
    #    print graphs.target.node[nodes.target]
    #    print graphs.source.get_graph_token_string().encode("utf-8")
    #    print graphs.target.get_graph_token_string().encode("utf-8")
    #    print graphs.source.tokens[source_index + 1 : source_index + same + 1]
    #    print graphs.target.tokens[target_index + 1 : target_index + same + 1]
    #    print

    return same

same_words_lhs = Feat(ff_same_words_lhs, "i", "N",
                      pp_graph_hooks=[pp_words]),



def ff_same_words_rhs(nodes, graphs, **kwargs):
    """
    return the number of equal lower-cased words at the right-hand side in the
    surface string
    """
    # also works for non-terminals
    source_index = int(graphs.source.node[nodes.source].get("begin"))
    target_index = int(graphs.target.node[nodes.target].get("begin"))
    same = 0
    pairs = zip( graphs.source.graph["lc_tokens"][source_index:], 
                 graphs.target.graph["lc_tokens"][target_index:] )

    for source_tok, target_tok in pairs:
        if source_tok == target_tok:
            same += 1
        else:
            break

    #if same:
    #    print "same_word_rhs", same
    #    print graphs.source.node[nodes.source]
    #    print graphs.target.node[nodes.target]
    #    print graphs.source.get_graph_token_string().encode("utf-8")
    #    print graphs.target.get_graph_token_string().encode("utf-8")
    #    print graphs.source.tokens[source_index: source_index + same]
    #    print graphs.target.tokens[target_index: target_index + same]
    #    print
        
    return same

same_words_rhs = Feat(ff_same_words_rhs, "i", "N",
                      pp_graph_hooks=[pp_words]),


same_words_context = ( same_words_lhs +
                       same_words_rhs )


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]








