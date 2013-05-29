"""
align nodes of graph pair with the equals relation
"""

from daeso_nl.ga.aligner import GraphAligner


# SOME REMAINING PROBLEMS

# Precision error
#
# s1: Energieprijs Nederland in topdrie EU 
# s2: Elektriciteit duur in Nederland 
#
# "in " is aligned because it is unique,
# but of course it shouldn't be
#
# This might be solved by checking, later on,
# if their obj1 are aligned
# Same errors occuer with determiners and otehr function words


# Recall error
#
# s1: Verdonk en Rutte debatteren in Utrecht 
# s2: Rutte en Verdonk in Utrecht in debat voor JOVD 
# (from headline-cluster-439b2b0d.pgc)
#
# "in" is not aligned, because the parent cannot be aligned
# (i.e, "in Utrecht" in s1 and "in Utrecht in debat voor JOVD" is s2)


# s1: ' Geen WW , WIA en Zietewet na seizoens- en vakantiewerk ' 
# s2  ' Geen WW , WIA en Ziektewet na seizoen- en vakantiewerk ' 
#
# Problem here is a typo in s1



class EqualsAligner(GraphAligner):
    
    def align(self, from_graph, to_graph, alignment):
        # all of this assumes that there are no alignment yet
        
        from_tokens2node = self.tokens_tables(from_graph)
        to_tokens2node = self.tokens_tables(to_graph)
        
        # sort, so nodes corresponding to amount of tokens, that is, higher nodes,
        # are aligned first
        all_from_tokens = from_tokens2node.keys()
        all_from_tokens.sort(lambda x, y: len(y) - len(x))
        
        edge = { "equals": 1.0 }        
        
        for tokens in all_from_tokens:
            from_nodes = from_tokens2node[tokens]
            
            try: 
                to_nodes = to_tokens2node[tokens]
            except KeyError:
                # no matching token strings in other graph
                continue
            
            if len(from_nodes) == len(to_nodes) == 1:
                # nodes are unique, so align
                # this can be refined 
                from_node, to_node = from_nodes[0], to_nodes[0]
                alignment.update_edge(from_node, to_node, edge)
                continue
            
            # align those node pairs of which the parent nodes are already aligned 
            for from_node in from_nodes:
                try:
                    from_parent = from_graph.predecessors(from_node)[0]
                except IndexError:
                    continue

                for to_node in to_nodes:
                    try:
                        to_parent = to_graph.predecessors(to_node)[0]
                    except IndexError:
                        continue
                    
                    if alignment.has_edge(from_parent, to_parent):
                        alignment.update_edge(from_node, to_node, edge)
                        from_nodes.remove(from_node)
                        to_nodes.remove(to_node)
                        
            # This still leaves a number of cases unaligned,
            # which have the following pattern.
            # 
            # s1: Volgens peiling blijft VVD winnen 
            # s2: Peiling : VVD blijft winnen 
            # (from headline-cluster-439b2b0d.pgc)
            # 
            # "winnen" is not aligned, because token "winnen" has two nodes in s2:
            # one terminal (the word itself) and one non-terminal (the inf node)
            #
            # The same pattern also frequently occurs with top and smain nodes 
            # with the same token string!
            # 
            # The solution is to check if the remaining nodes are connected
            # by one or more child-parent relations

            if self.connected(from_graph, from_nodes) and self.connected(to_graph, to_nodes):
                for from_node in from_nodes:
                    for to_node in to_nodes:
                        # heuristic: try to align from_node and to_node 
                        # with the same cat or pos
                        try:
                            if from_node.pos == to_node.pos:
                                alignment.update_edge(from_node, to_node, edge)
                        except AttributeError:
                            pass
                        
                        try:
                            if from_node.cat == to_node.cat:
                                alignment.update_edge(from_node, to_node, edge)
                        except AttributeError:
                            pass
            
                        
    def connected(self, graph, nodes):
        """
        test if the node pairs in the list of nodes are all in a parent-child relation
        """
        # ordering of the nodes from high to low is crucial here
        for i in range(1, len(nodes)):
            if not graph.has_edge(nodes[i-1], nodes[i]):
                return False
            
        return True
            
        
    def tokens_tables(self, graph):
        """
        creates a mapping for every token string to a list of one or more nodes
        which correspond to this token string
        """
        tokens2node = {}
        
        for node in graph:
            # skip punctuation -  alpino specific
            if not node.is_punct() and not node.is_empty():
                tokens = node.get_token_string().lower()
                tokens2node.setdefault(tokens, []).append(node)
            
        return tokens2node
    
    
    