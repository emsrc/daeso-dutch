"""
test AlpinoGraph class
"""

import unittest

from daeso_nl.graph.alpinograph import AlpinoGraph


class Test_AlpinoGraph(unittest.TestCase):

    def setUp(self):
        self.ag = AlpinoGraph(root="0")

        self.ag.add_node("0", "top", cat="top",
                         tokens="Ik wilde weten of hij echt begrip had .".split())
        self.ag.add_node("1", "smain", cat="smain",
                         tokens="Ik wilde weten of hij echt begrip had".split())
        self.ag.add_node("2", "pron", pos="pron", root="ik", index="1",
                         tokens="Ik".split())
        self.ag.add_node("3", "verb", pos="verb", root="willen",
                         tokens="wilde".split())	
        self.ag.add_node("4", "inf", cat="inf",
                         tokens="weten of hij echt begrip had".split())	
        self.ag.add_node("5", "index", index="1")	
        self.ag.add_node("6", "verb", pos="verb", root="weten",
                         tokens="weten".split())	
        self.ag.add_node("7", "cp", cat="cp",
                         tokens="of hij echt begrip had".split())	
        self.ag.add_node("8", "comp", pos="comp", root="of",
                         tokens="of".split())	
        self.ag.add_node("9", "ssub", cat="ssub",
                         tokens="hij echt begrip had".split())	
        self.ag.add_node("10", "pron", pos="pron", root="hij",
                         tokens="hij".split())	
        self.ag.add_node("11", "np", cat="np",
                         tokens="echt begrip".split())	
        self.ag.add_node("12", "adj", pos="adj", root="echt",
                         tokens="echt".split())	
        self.ag.add_node("13", "noun", pos="noun", root="begrip",
                         tokens="begrip".split())	
        self.ag.add_node("14", "verb", pos="verb", root="hebben",
                         tokens="had".split())	
        self.ag.add_node("15", "punt", pos="punct", root=".",
                         tokens=".".split())
        
        self.ag.add_edge("0", "1", "--")
        self.ag.add_edge("1", "2", "su")
        self.ag.add_edge("1", "3", "hd")
        self.ag.add_edge("1", "4", "vc")
        self.ag.add_edge("4", "5", "su")
        self.ag.add_edge("4", "6", "hd")
        self.ag.add_edge("4", "7", "vc")
        self.ag.add_edge("7", "8", "cmp")
        self.ag.add_edge("7", "9", "body")
        self.ag.add_edge("9", "10", "su")
        self.ag.add_edge("9", "11", "obj1")
        self.ag.add_edge("11", "12", "mod")
        self.ag.add_edge("11", "13", "hd")
        self.ag.add_edge("9", "14", "hd")
        self.ag.add_edge("0", "15", "punct")

        
    def test_print_subtree(self):
        print "\n", self.ag
        
        
    def test_node_is_nominal(self):
        self.assertTrue(self.ag.node_is_nominal("13"))
        self.assertFalse(self.ag.node_is_nominal("3"))
        
    
    def test_node_is_punct(self):
        self.assertTrue(self.ag.node_is_punct("15"))
        self.assertFalse(self.ag.node_is_punct("14"))
        
        
    def test_node_is_index(self):
        self.assertTrue(self.ag.node_is_index("5"))
        self.assertFalse(self.ag.node_is_index("1"))
        self.assertFalse(self.ag.node_is_index("2"))
        
        
    def test_get_root_node(self):
        self.assertEqual(self.ag.root, "0")
        
        
    def test_get_parent_node(self):
        self.assertEqual(self.ag.get_parent_node("0"), None)
        self.assertEqual(self.ag.get_parent_node("1"), "0")
        
        
    def test_get_node_deprel(self):
        self.assertEqual(self.ag.get_node_deprel("0"), None)
        self.assertEqual(self.ag.get_node_deprel("15"), "punct")
        
        
    def test_node_is_complement(self):
        self.assertTrue(self.ag.node_is_complement("11"))
        self.assertFalse(self.ag.node_is_complement("12"))
        
        
        
    
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()