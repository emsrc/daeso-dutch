"""
parser for graphbanks in Alpino format
"""

from daeso.gb.parser import XmlGraphbankParser
from daeso_nl.graph.alpinograph import AlpinoGraph
from daeso.exception import DaesoError


# TODO:
# - doc strings
# - option to parse comments


class AlpinoParser(XmlGraphbankParser):
    """
    expat-based parser for graphbanks in Alpino format
    """
    
    def __init__(self):
        XmlGraphbankParser.__init__(self)
        self._graph = None
        self._in_sentence = False
        self._n = 0

        
    def _start_element(self, tag, attrs):
        if tag == "alpino_ds":
            self._start_graph(attrs)
        elif self._graph_is_wanted():
            if tag == "node":
                self._start_node(attrs)
            elif tag == "sentence":
                self._start_sentence(attrs)      
            
        
    def _graph_is_wanted(self):
        """
        Test if current graph is to be parsed or skipped
        """
        # graph will also return false if just empty, 
        # i.e. testing "if self._graph:" does not work
        return self._graph is not None
            
            
    def _start_graph(self, attrs):
        # to enable parsing graphs without id attribute,
        # id defaults to graph number
        id = attrs.get("id", self._n)
        self._n += 1
        
        if not self._sparse or id in self._id2graph:
            self._graph = self._id2graph[id] = AlpinoGraph(id=id)
            
            # stack that records ancestor nodes,
            # because we need a node's parent to add a new edge 
            self._ancestors = []
            
            # list of tokens in the order that they are encountered in the tree
            # (which is often different from the order in the sentence)
            self._tokens = []
            
            # tracks the current position in self._tokens
            self._index = 0 
            
            # stack which records self._index upon entering a non-terminal node,
            # which is required to calculate the tokens belonging to non-terminal
            # when exiting a non-terminal
            self._index_stack = []
            
            
    def _start_node(self, attrs):
        n = attrs.pop("id")
        rel = attrs.pop("rel")
        word = attrs.get("word")
        
        if word:
            # terminal
            tokens = [word]
            self._tokens.append(word)
            self._index += 1
        elif attrs.has_key("cat"):
            # non-terminal
            tokens = []
            self._index_stack.append(self._index)
        else:
            # empty node with "index" attribute
            tokens = []
            
        self._graph.add_node(n, 
                             label=self._get_node_label(attrs),
                             tokens=tokens,
                             attr_dict=attrs)
        try:
            parent_n = self._ancestors[-1]
        except IndexError:
            # root node
            self._graph.root = n
        else:
            self._graph.add_edge(parent_n, n, rel)
        
        self._ancestors.append(n)
        
        
    def _get_node_label(self, attrs):
        """
        return node label, which is the 'pos', 'cat' or 'index' attribute, in
        that order
        """
        for key in ("pos", "cat", "index"):
            try:
                return attrs[key]
            except KeyError:
                pass
        else:
            raise DaesoError("Alpino <node> element must have "
                             "'pos', 'cat' or 'index' attribute")

            
    def _start_sentence(self, attrs):
        self._in_sentence = True  
        self._sentence = ""
    
    
    def _end_element(self, tag):
        if self._graph_is_wanted():
            if tag == "alpino_ds":
                self._end_graph()
            elif tag == "node":
                self._end_node()
            elif tag == "sentence":
                self._end_sentence()
    
    
    def _end_graph(self):
        if len(self._graph) == 0:
            msg = "encountered empty graph (id=%s) while parsing graphbank" % self._graph.id
            raise DaesoError(msg)
        
        self._update_tokens()
        self._graph = None
            
            
    def _end_node(self):
        n = self._ancestors.pop()            
        
        if self._graph.node_is_non_terminal(n):
            # non-terminal
            i = self._index_stack.pop()
            self._graph.set_node_tokens(n, self._tokens[i:])
            
            
    def _end_sentence(self):
        self._in_sentence = False
        self._graph.set_graph_token_string(self._sentence)
            
        
    def _char_data(self, data):
        if self._graph_is_wanted:
            if self._in_sentence:
                self._sentence += data
            
            
    def _update_tokens(self):
        """
        A tree may contain empty terminal nodes ("traces") that have no
        "word" content. Empty nodes are co-indexed with a non-empty node
        higher up in the tree. Example:
        
          <node begin="0" cat="ppart" end="16" id="26" rel="cnj">
           <node begin="0" end="11" id="27" index="1" rel="obj1" />
           <node begin="12" end="13" id="28" index="2" rel="mod" />
           <node begin="15" end="16" id="29" pos="verb" rel="hd" root="stelen" word="gestolen" />
          </node>
       
        from the sentence: 
       
          "Verkiezingsposters van de Partij voor de Dieren in de provincie
          Zeeland worden systematisch vernield of gestolen ."
       
        Empty nodes are omitted from the Dot graph and thus invisible to the
        annotator. Hence, when selecting the node "ppart" (id=26), the
        annotator expects to see the corresponding string "gestolen".
        However, according to the "begin" (=0) and "end" (=16) attributes, the
        corresponding string is the full sentence! 
       
        The reason is that "begin" and "end" attributes can only define a
        continous substring, and are thus unable to represent a gapped
        string. Futhermore, note that empty nodes can also occur in the
        middle of tree rather than at the start (as here) or end. Therefore,
        Alpino chooses to include the subtrings covered by empty nodes.
        
        The solution is to ignore Alpino's "begin"/"end" attributes and to
        explicitly calculate the yield of each subtree. This means that the
        yield the above subtree becomes "gestolen", which is as intended.
       
        So far so good. Now, consider the following example:
       
          <node begin="12" cat="oti" end="18" id="22" rel="mod">
            <node begin="12" end="13" id="23" pos="comp" rel="cmp" root="om" word="om" />
            <node begin="13" cat="ti" end="18" id="24" rel="body">
              <node begin="16" end="17" id="25" pos="comp" rel="cmp" root="te" word="te" />
              <node begin="13" cat="inf" end="18" id="26" rel="body">
                <node begin="13" cat="np" end="15" id="27" rel="obj1">
                  <node begin="13" end="14" id="28" pos="det" rel="det" root="die" word="die" />
                  <node begin="14" end="15" id="29" pos="noun" rel="hd" root="bord" word="borden" />
                </node>
                <node begin="15" end="16" id="30" pos="part" rel="svp" root="weg" word="weg" />
                <node begin="17" end="18" id="31" pos="verb" rel="hd" root="halen_weg" word="halen" />
              </node>
            </node>
          </node>
       
        from the sentence:
       
           "We zijn getipt dat er 's nachts mensen met auto's komen om die borden weg te halen ."
        
        The yield of this subtree is "om te die borden weg halen". It does
        not correspond to the surface string, because there is no way to
        represent both the syntactic dominance relations and the surface
        word order without introducing crossing branches. Clearly, using the
        yield here is inferior to using the substring defined by the the
        "begin"/"end" attributes, i.e. "om die borden weg te halen".
        Moreover, there is no reason for using the yield, because the
        subtree contains no empty nodes.
       
        So now the question becomes: when do we use the yield and when do we
        use the substring? Keeping track of empty nodes and their resolution
        by means of a stack would require a lot of boring and complicated
        administrative code. The good news is that it can be avoided using
        the crucial observation that if the substring and the yield are of
        equal size, then the subtree contains no empty nodes. Therefore, if
        their size is equal, we use the substring, otherwise we fall back to
        the yield.
       
        This must be the longest comment ever for five lines of code :-) 
        """
        for n in self._graph:
            begin = int(self._graph.node[n]["begin"])
            end = int(self._graph.node[n]["end"])
            len_alpino_tokens = end - begin
            
            if len(self._graph.get_node_tokens(n)) == len_alpino_tokens:
                self._graph.set_node_tokens(n, self._graph.tokens[begin:end])
            
            
            