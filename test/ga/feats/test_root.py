"""
test root features
"""

import unittest

from daeso.pair import Pair

from daeso_nl.graph.alpinograph import AlpinoGraph
from daeso_nl.ga.feats import *
from daeso_nl.ga.feats.root import ( ff_roots_share_infix,
                                     ff_roots_share_prefix, 
                                     ff_roots_share_suffix, 
                                     ff_roots_subsumption )



class Test_RootFeatures(unittest.TestCase):
        
    def test_roots_subsumption(self):
        graphs = Pair(AlpinoGraph(), AlpinoGraph()) 
        graphs.source.add_node(1, "x")
        graphs.target.add_node(2, "y")
        nodes = Pair(1, 2)
        
        # no roots
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "-")
        
        graphs.source.node[1]["root"] = "wagen"
        graphs.target.node[2]["root"] = "wagen"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "equals")
        
        graphs.source.node[1]["root"] = "brandweer_wagen"
        graphs.target.node[2]["root"] = "brandweer"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "has_prefix")
        
        graphs.source.node[1]["root"] = "brandweer"
        graphs.target.node[2]["root"] = "brandweer_wagen"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "is_prefix")
        
        graphs.source.node[1]["root"] = "brandweer_wagen"
        graphs.target.node[2]["root"] = "wagen"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "has_suffix")
        
        graphs.source.node[1]["root"] = "wagen"
        graphs.target.node[2]["root"] = "brandweer_wagen"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "is_suffix")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoners_kamp_ingang"
        graphs.target.node[2]["root"] = "wagen_bewoners"
        self.assertEqual(ff_roots_subsumption(nodes, graphs),
                         "has_infix")
        
        graphs.source.node[1]["root"] = "wagen_bewoners"
        graphs.target.node[2]["root"] = "woon_wagen_bewoners_kamp_ingang"
        self.assertEqual(ff_roots_subsumption(nodes, graphs), 
                         "is_infix")
        
        # no subsumption
        graphs.source.node[1]["root"] = "brandweer_wagen"
        graphs.target.node[2]["root"] = "kamp_ingang"
        self.assertEqual(ff_roots_subsumption(nodes, graphs), 
                         "none")
        
        
    def test_roots_share_prefix(self):
        graphs = Pair(AlpinoGraph(), AlpinoGraph()) 
        graphs.source.add_node(1, "x")
        graphs.target.add_node(2, "y")
        nodes = Pair(1, 2)
        
        # no roots
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "-")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "eet_tafel"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "woon_wagen"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "woon"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "woon_wagen"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "woon_boot"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "T")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "woon_wagen_kamp"
        self.assertEqual(ff_roots_share_prefix(nodes, graphs),
                         "T")
        
        
    def test_roots_share_suffix(self):
        graphs = Pair(AlpinoGraph(), AlpinoGraph()) 
        graphs.source.add_node(1, "x")
        graphs.target.add_node(2, "y")
        nodes = Pair(1, 2)
        
        # no roots
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "-")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "eet_tafel"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "woon_wagen"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "wagen"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "wagen_bewoner"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "mest_wagen"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "T")
        
        graphs.source.node[1]["root"] = "woon_wagen_trekker"
        graphs.target.node[2]["root"] = "mest_wagen_trekker"
        self.assertEqual(ff_roots_share_suffix(nodes, graphs),
                         "T")
        
        
    def test_roots_share_infix(self):
        graphs = Pair(AlpinoGraph(), AlpinoGraph()) 
        graphs.source.add_node(1, "x")
        graphs.target.add_node(2, "y")
        nodes = Pair(1, 2)
        
        # no roots
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "-")
        
        graphs.source.node[1]["root"] = "woon_wagen"
        graphs.target.node[2]["root"] = "woon_wagen"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "eet_tafel_laken"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "woon_wagen_bewoner"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "woon_wagen_kamp"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "F")
        
        graphs.source.node[1]["root"] = "woon_wagen_bewoner"
        graphs.target.node[2]["root"] = "mest_wagen_trekker"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "T")
        
        graphs.source.node[1]["root"] = "woon_wagen_kamp_bewoner"
        graphs.target.node[2]["root"] = "mest_wagen_kamp_trekker"
        self.assertEqual(ff_roots_share_infix(nodes, graphs),
                         "T")
        
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()