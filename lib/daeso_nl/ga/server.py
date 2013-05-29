"""
graph alignment server
"""

# TODO:
# - proper handling of failed parses
    
import sys
import re

from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import ServerProxy
from xml.parsers.expat import ExpatError

from daeso.pgc.graphpair import GraphMatching
from daeso.gb.graphbank import GraphBank
from daeso.pair import Pair

from daeso_nl.gb.alpinoparser import AlpinoParser
from daeso_nl.alpino.server import (
    DEFAULT_HOST as ALPINO_HOST, 
    DEFAULT_PORT as ALPINO_PORT )

from daeso_nl.ga.aligner import GraphAligner


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5508


class AlignServer(object):
    # the maximum number that the parser for Alpino XML will be reused
    max_alpino_parser_reuse = 1000  
    
    # regexp to detect unescaped ampercent, that is, not part of an entity such &amp;, &apos;, etc.
    regexp = re.compile(r"&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+);)")
    
    def __init__(self, tokenizer=None, alpino=None, graph_aligner=None):
        self.init_tokenizer(tokenizer)
        self.init_alpino(alpino)
        self.init_graph_xml_parser()
        self.init_graph_aligner(graph_aligner)
        self.init_others()
        
        # a pair of graphbank dummies, which are needed when creating a new
        # GraphMapping instance
        self._graphbanks = Pair(
            GraphBank("", "alpino"),
            GraphBank("", "alpino"))
        
    def init_tokenizer(self, tokenizer=None):
        self._tokenizer = tokenizer
        
    def init_alpino(self, alpino):
        # "if alpino: ..." does not work because op peculiarities of xml-rpc
        # implementation
        if alpino is None:
            host = "http://%s:%d" % (ALPINO_HOST, ALPINO_PORT)
            self._alpino = ServerProxy(host, 
                                       encoding="iso-8859-1")
        else:
            self._alpino = alpino

        self._alpino.parse("test")
            
    def init_graph_xml_parser(self):
        self._alpino_xml_parser = AlpinoParser()
        self._alpino_parser_reused = 0
        # feed fake root node to the xml parser
        self._alpino_xml_parser.parse_string(
            '<?xml version="1.0" encoding="utf-8"?>\n<treebank>')
            
    def init_graph_aligner(self, graph_aligner):
        if graph_aligner:
            self._graph_aligner = graph_aligner
        else:
            self._graph_aligner = GraphAligner()
            
        self.no_rel = self._graph_aligner.descriptor.no_rel

    def init_others(self):
        # hook for subclasses
        pass
    
    def align(self, source_sent, target_sent):
        # the strings received here after transport through XML-RPC are either
        # plain ascii or unicode
        sent_pair = Pair(source_sent, target_sent)
        
        tok_sent_pair = self._tokenize(sent_pair)
        
        parse_pair = self._parse(tok_sent_pair)
        
        graph_pair = self._load_graphs(parse_pair)
        
        instances = self._align_graphs(graph_pair)
        
        parse_align, phrase_align = self._get_alignment(instances, graph_pair)
        
        return dict(
            source_sent = sent_pair.source,
            target_sent = sent_pair.target,
            source_tok = tok_sent_pair.source,
            target_tok = tok_sent_pair.target,
            source_parse = parse_pair.source,
            target_parse = parse_pair.target,
            parse_align = parse_align,
            phrase_align = phrase_align 
        )
        
    def _tokenize(self, sent_pair):
        if self._tokenizer:
            return self._tokenizer(sent_pair)
        else:
            return sent_pair
    
    def _parse(self, tok_sent_pair):
        return Pair(
            self._parse_single_sent(tok_sent_pair.source),
            self._parse_single_sent(tok_sent_pair.target))    
    
    def _parse_single_sent(self, tok_sent):
        # Sentence will be of type unicode if the original sentence passed
        # to the server proxy (client) contained any non-ascii chars, but
        # will be of type str otherwise. Input to the alpino server proxy
        # must be iso-8859-1 encoded, so we have to convert
        tok_sent = tok_sent.encode("iso-8859-1")
        
        graph = self._alpino.parse(tok_sent)

        # The returned parse is string of type unicode or str, regardless
        # of what the xml header produced by alpino says. First we get rid
        # of this xml header.
        return graph.split("\n", 1)[1]

    def _load_graphs(self, parse_pair):        
        # The AlpinoParser instance can be reused to avoid the overhead of
        # creating a new one. It seems that there is maximum to the number of
        # lines though. After that we get an error like:
        #
        # xml.parsers.expat.ExpatError: not well-formed (invalid token): 
        # line 2654543, column 300
        #
        # We therefore count the number of reuses and create a new instance
        # when self.max_parser_reuse is reached.
        if self._alpino_parser_reused < self.max_alpino_parser_reuse:
            self._alpino_parser_reused += 1
        else:
            self.init_graph_xml_parser()
        
        # The xml parser for graphbanks wants utf-8,
        # so we encode as utf-8
        xml_string = ( parse_pair.source.encode("utf-8") + 
                       parse_pair.target.encode("utf-8") )
        
        # Alpino outputs ill-formed xml because some "&" are not escaped
        # e.g. <node begin="0" cat="mwu" end="3" id="1" mwu_root="erwin & mireille" mwu_sense="erwin & mireille" rel="--">
        # This is a hack to correct that.
        xml_string = self.regexp.sub("&amp;", xml_string)
        
        try:
            id2graph = self._alpino_xml_parser.parse_string(xml_string)
        except ExpatError, inst:
            sys.stderr.write("Error:%s\nInput:\n%s\n" % (inst, xml_string))
            # reset parser
            sys.stderr.write("Resetting Alpino output parser\n")
            self.init_graph_xml_parser()
            raise inst
            # the exception surfaces as an xmlrpc fault,
            # but subsequent calls to align method should work 
                      
        graph_pair = Pair(*id2graph.values())
        return GraphMatching(
            banks=self._graphbanks,
            graphs=graph_pair)
        
    def _align_graphs(self, graph_pair):
        return self._graph_aligner.align(graph_pair)
        
    def _get_alignment(self, instances, graph_pair):
        graph_align = []
        parse_align = []
        graphs = graph_pair.get_graphs()
        
        for inst in instances:
            if inst["match_relation"] != self.no_rel:
                # cast to python string because xml-rpc cannot serialize
                # numpy.string_ type
                graph_align.append( (int(inst["source_node"]), 
                                     str(inst["match_relation"]),
                                     int(inst["target_node"])) )
                
                source_str = \
                graphs.source.get_node_token_string(inst["source_node"])
                target_str = \
                graphs.target.get_node_token_string(inst["target_node"])
                
                parse_align.append( (source_str.encode("utf-8"),
                                     str(inst["match_relation"]),
                                     target_str.encode("utf-8")) )

        return graph_align, parse_align
        
    
    

def echo(s):
    """
    simply returns the input (useful for testing the socket connection)
    """
    return s
            
            
        
def start_server(server_inst, host=DEFAULT_HOST, port=DEFAULT_PORT, log=None):
    server = SimpleXMLRPCServer((host, port), logRequests=log)
    server.register_introspection_functions()
    server.register_function(echo)
    server.register_instance(server_inst)
    
    print >>sys.stderr, "Listening on %s:%d" % (host, port)
    server.serve_forever()    
