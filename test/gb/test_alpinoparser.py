"""
test AlpinoPare class
"""

import sys
import unittest

from daeso_nl.gb.alpinoparser import AlpinoParser


class Test_AlpinoParser(unittest.TestCase):

    def setUp(self):
        pass
        
    def test_parse_file(self):
        parser = AlpinoParser()
        id2graph = {}
        parser.parse_file("data/gb-sample.xml", id2graph)
        
        for id, graph in id2graph.items():
            print id
            print graph.get_graph_token_string().encode("utf-8")
            print
            print graph.graph_to_string().encode("utf-8")
            print 78 * "="
            
            
    def test_parse_string(self):
        """
        test incremental parsing
        """
        parser = AlpinoParser()
        parser.parse_string("<treebank>")
        
        # extract xml for dependency structures from graphbank file
        xml = open("data/gb-sample.xml").read()
        xml = xml.split("<treebank>", 1)[1]
        
        while not xml.startswith("</treebank>"):
            ds, xml = xml.split("</alpino_ds>", 1)
            ds += "</alpino_ds>"
            # remove id
            ds = "<alpino_ds>" + ds.split(">",1)[1]
            id2graph = parser.parse_string(ds)
            id, graph = id2graph.items()[0]
            print id2graph
            print id
            print graph.get_graph_token_string().encode("utf-8")
            print
            print graph.graph_to_string().encode("utf-8")
            print 78 * "="
            
            
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()