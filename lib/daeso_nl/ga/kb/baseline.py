"""
simple alignment baselines
"""


# TODO:
# - better implementions

from daeso.pair import Pair


def greedy_align_equal_words(corpus):
    for graph_pair in corpus:
        graph_pair.clear()
        graphs = graph_pair.get_graphs()
        
        target_nodes = graphs.target.terminals(with_punct=False,
                                               with_empty=False)
        target_words = [ graphs.target.node[tn]["word"].lower()
                         for tn in target_nodes ]
        
        for sn in graphs.source.terminals_iter(with_punct=False,
                                               with_empty=False):
            sw = graphs.source.node[sn]["word"].lower()
            
            try:
                j = target_words.index(sw)
            except:
                continue
            
            tn = target_nodes[j]        
            graph_pair.add_align(Pair(sn, tn), "equals")
            
            del target_nodes[j]
            del target_words[j]
            
            
def greedy_align_equal_words_roots(corpus):
    # if words are equal, align as equals
    # elif roots are equals, align as restates
    for graph_pair in corpus:
        graph_pair.clear()
        graphs = graph_pair.get_graphs()
        
        target_nodes = graphs.target.terminals(with_punct=False,
                                               with_empty=False)
        target_words = [ graphs.target.node[tn]["word"].lower()
                         for tn in target_nodes ]
        target_roots = [ graphs.target.node[tn]["root"]
                         for tn in target_nodes ]
        
        for sn in graphs.source.terminals_iter(with_punct=False,
                                               with_empty=False):
            sw = graphs.source.node[sn]["word"].lower()
            sr = graphs.source.node[sn]["root"]
                        
            try:
                j = target_words.index(sw)
            except:
                try:
                    j = target_roots.index(sr)
                except:
                    continue
                else:
                    relation = "restates"
            else:
                relation = "equals"
            
            tn = target_nodes[j]        
            graph_pair.add_align(Pair(sn, tn), relation)
            
            del target_nodes[j]
            del target_words[j]
            del target_roots[j]

            

            
def greedy_align_words(corpus):
    # if words are equal -> equals
    # if roots are equals -> restates
    # if source in target root and len(source)>3 -> generalizes
    # if target in source root and len(target)>3-> specifies
    # if target and source root share a morph segment ->intersects
    for graph_pair in corpus:
        graph_pair.clear()
        graphs = graph_pair.get_graphs()
        
        target_nodes = graphs.target.terminals(with_punct=False,
                                               with_empty=False)
        target_words = [ graphs.target.node[tn]["word"].lower()
                         for tn in target_nodes ]
        target_roots = [ graphs.target.node[tn]["root"]
                         for tn in target_nodes ]
        
        for sn in graphs.source.terminals_iter(with_punct=False,
                                               with_empty=False):
            sw = graphs.source.node[sn]["word"].lower()
            relation = None
            
            # align identical words
            for i, tw in enumerate(target_words):
                if sw == tw:
                    relation = "equals"
                    break
                    
            if not relation:
                sr = graphs.source.node[sn]["root"]
            
                # align identical roots
                for i, tr in enumerate(target_roots):
                    if sr == tr:
                        relation = "restates"
                        break
                        
            if not relation:
                sparts = set(sr.split("_"))
                
                # check for spec, gen, or intersect
                for i, tr in enumerate(target_roots):
                    tw = target_words[i]
                    
                    if sr in tr and len(sw) > 3:
                        relation = "generalizes"
                        break
                    elif tr in sr and len(tw) > 3:
                        relation = "specifies"
                        break
                    # check if roots share a morphological segment
                    elif sparts.intersection(tr.split("_")):
                        relation = "intersects"
                        break
            
            if relation:
                tn = target_nodes[i]        
                graph_pair.add_align(Pair(sn, tn), relation)
                
                del target_nodes[i]
                del target_words[i]
                del target_roots[i]     
            

                

#=====================================================================
# Full tree alignment
#=====================================================================
        

def lc_roots(graph, n):
    """
    Return the list of the lower-cased roots of the terminals in
    the yield of node n.
    Store list in attribute "_lc_roots" of node n.
    Also recursively calls lc_roots for all nodes dominated by node n. 
    """
    try:
        # node already seen (should not happen in trees)
        return graph.node[n]["_lc_roots"]
    except KeyError:
        graph.node[n]["_lc_roots"] = []
        
        if graph.node_is_terminal(n, with_empty=False, with_punct=False):
            root = graph.node[n].get("root", "").lower()
            if root:
                graph.node[n]["_lc_roots"].append(root)
        else:
            # punct and empty nodes end here
            for m in graph.successors(n):
                graph.node[n]["_lc_roots"] += lc_roots(graph, m)
        
        return graph.node[n]["_lc_roots"]
    
         
def greedy_align_phrases(corpus):
    # greedy align phrases with the same lower-cased words as strings and with
    # the same lower-cased roots as restates
    for graph_pair in corpus:
        graph_pair.clear()
        graphs = graph_pair.get_graphs()
        lc_roots(graphs.source, graphs.source.root)
        lc_roots(graphs.target, graphs.target.root)
        
        target_nodes = [ tn for tn in graphs.target
                         if ( not graphs.target.node_is_punct(tn) and 
                              not graphs.target.node_is_empty(tn) ) ]
        
        target_words = [ graphs.target.get_node_token_string(tn).lower()
                         for tn in target_nodes ]
        
        target_roots = [ graphs.target.node[tn].get("_lc_roots", [])
                         for tn in target_nodes ]

        for sn in graphs.source:
            if ( graphs.source.node_is_punct(sn) or 
                 graphs.source.node_is_empty(sn) ):
                continue
            
            sw = graphs.source.get_node_token_string(sn).lower()
            sr = graphs.source.node[sn].get("_lc_roots")
                        
            try:
                j = target_words.index(sw)
            except:
                try:
                    j = target_roots.index(sr)
                except:
                    continue
                else:
                    tn = target_nodes[j]        
                    graph_pair.add_align(Pair(sn, tn), "restates")
                    #print "RESTATES"
                    #print " ".join(sr)
                    #print " ".join(target_roots[j])
            
                    del target_nodes[j]
                    del target_words[j]
                    del target_roots[j]
            else:
                tn = target_nodes[j]        
                graph_pair.add_align(Pair(sn, tn), "equals")
                #print "EQUALS"
                #print sw
                #print target_words[j]
            
                del target_nodes[j]
                del target_words[j]
                del target_roots[j]

                