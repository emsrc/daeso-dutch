"""
Definition of AlpinoGraph class
"""

# TODO:
# * docstrings

from daeso.graph.daesograph import DaesoGraph



class AlpinoGraph(DaesoGraph):
    
    compl_dep_rels = ( "hd su sup obj1 pobj1 se obj2 predc vc pc "
                       "me ld svp obcomp rhd whd body" ).split()
    
    
    def graph_to_string(self, n=None, deprel=None, indent=0, with_tokens=True):
        if not n:
            n = self.root
            
        if not deprel:
            deprel = self.get_node_deprel(n)
            
        label = self.node[n]["label"].upper()
        
        if indent:
            s = ( indent * " " +
                  str(deprel).center(8, "=") + "> " +
                  str(n) + ":" +
                  label )
        else:
            s = str(n) + ":" + label
        
        if with_tokens:
            s += ': "' + self.get_node_token_string(n) + '"'
        
        s += "\n" 
        
        for n, succ_n, edge in self.edges_iter((n,), data=True):
            s += self.graph_to_string(succ_n, 
                                      edge["label"], 
                                      indent + 4,
                                      with_tokens=with_tokens)
        return s
    
            
    def is_failed_parse(self):
        # only works by Daeso convention
        try:
            return self.node[self.root]["cat"] == "FAILED PARSE"
        except KeyError:
            pass
        
    
    def __str__(self):
        return self.graph_to_string()
            
    #-------------------------------------------------------------------------
    # Node methods 
    #-------------------------------------------------------------------------
    
    # convention: we assume that the node argument exists in the graph
    
    def node_is_nominal(self, n):
        return ( self.node[n].get("cat") == "np" or 
                 self.node[n].get("pos") in ("noun", "name") )

    
    def node_is_punct(self, n):
        return self.node[n].get("pos") == "punct"
    
    
    def node_is_index(self, n):
        # this is not exactly the same as node_is_empty,
        # because e.g. a failed parse has no tokens either
        return ( self.node[n].get("index") and
                 not self.node[n].get("tokens") )
            
    
    def get_parent_node(self, n):
        # assume Alpino graph is a tree and therefore each node has at most
        # one predecessors
        try:
            return self.predecessors_iter(n).next()
        except StopIteration:
            # node is root node
            return None
    
        
    def get_node_deprel(self, n):
        try:
            datadict = self.pred[n].itervalues().next()
        except StopIteration:
            # if n is root node, then it has no deprel
            return
        
        return datadict["label"]
        
        
    def node_is_complement(self, n):
        try:
            return self.get_node_deprel(n) in self.compl_dep_rels
        except ValueError:
            # if node is a root node, then it's not a complement
            pass
        
        
    def get_phrase_head(self, n):
        """
        get the syntactic head of a non-terminal phrasal node,
        which is the daughter with the "hd" deprel (if any)
        """
        for m in self.successors_iter(n):
            if self.succ[n][m]["label"] == "hd":
                return m
            

    def get_dep_head(self, n):
        """
        get the dependency head of which this node is a dependent
        """
        for parent_n in self.predecessors_iter(n):
            # search for the head of the parent node,
            # which must be different from the starting node n
            head_n = self.get_phrase_head(parent_n)
            
            if head_n != None and head_n != n:
                # one of the sibbling nodes is the head
                return head_n
            else:
                # continue searching for the head higher up in the tree
                return self.get_dep_head(parent_n)
            
        # root node reached without finding a head: return None
            
            
        
        
            

  
             

    
    

        

    
    