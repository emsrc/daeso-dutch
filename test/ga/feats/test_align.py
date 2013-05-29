"""
test align features
"""

import unittest

from daeso.pair import Pair

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.extractor import Extractor, select_visible_node
from daeso_nl.ga.feats import *

# TODO: add asserts for other features


class Test_AlignFeatures(unittest.TestCase):
    
    def setUp(self):
        self.corpus = ParallelGraphCorpus(
            inf="../exp/corpora/news/pgc/ma/2006-11/news-2006-11-aligned-part-00.pgc")

    def dump(self, graph_pair, instances):
        graphs = graph_pair.get_graphs()
        feat_names = [ t[0] for t in instances.dtype.descr[4:-4] ]
        
        for i, inst in enumerate(instances):
            nodes = Pair(inst["source_node"], inst["target_node"])
            
            print "instance:", i
            print "source: %s: %s: %s" % (
                nodes.source,
                graphs.source.node[nodes.source]["label"],
                graphs.source.get_node_token_string(nodes.source))  
            print "target: %s: %s: %s" % (
                nodes.target,
                graphs.target.node[nodes.target]["label"],
                graphs.target.get_node_token_string(nodes.target))  
            
            for fn in feat_names:
                print "%s: %s" %( fn, inst[fn])
            
            print 40 * "-"

        
    def test_align_count(self):
        descriptor = Descriptor(term_align) 
        
        feat_extr = Extractor(
            descriptor,
            node_selector=select_visible_node)
        
        graph_pair = self.corpus[0]
        instances = feat_extr.extract(graph_pair)
        self.dump(graph_pair, instances)
        
        # check for a couple of "interesting" instances
        
        #instance: 0
        #source: 0: top: Posters Partij voor de Dieren verwijderd
        #target: 0: top: Zeeland verwijdert posters Partij voor de Dieren
        #align_inside_count: 6
        #source_align_outside_count: 0
        #target_align_outside_count: 0
        #source_align_none_count: 0
        #target_align_none_count: 1
        self.assertEqual(instances[0]["align_inside_count"], 6)
        self.assertEqual(instances[0]["source_align_outside_count"], 0)
        self.assertEqual(instances[0]["target_align_outside_count"], 0)
        self.assertEqual(instances[0]["source_align_none_count"], 0)
        self.assertEqual(instances[0]["target_align_none_count"], 1)

        #instance: 2
        #source: 0: top: Posters Partij voor de Dieren verwijderd
        #target: 2: name: Zeeland
        #align_inside_count: 0
        #source_align_outside_count: 6
        #target_align_outside_count: 0
        #source_align_none_count: 0
        #target_align_none_count: 1
        self.assertEqual(instances[2]["align_inside_count"], 0)
        self.assertEqual(instances[2]["source_align_outside_count"], 6)
        self.assertEqual(instances[2]["target_align_outside_count"], 0)
        self.assertEqual(instances[2]["source_align_none_count"], 0)
        self.assertEqual(instances[2]["target_align_none_count"], 1)
        
        #instance: 25
        #source: 2: noun: Posters
        #target: 3: verb: verwijdert
        #align_inside_count: 0
        #source_align_outside_count: 1
        #target_align_outside_count: 1
        #source_align_none_count: 0
        #target_align_none_count: 01
        self.assertEqual(instances[25]["align_inside_count"], 0)
        self.assertEqual(instances[25]["source_align_outside_count"], 1)
        self.assertEqual(instances[25]["target_align_outside_count"], 1)
        self.assertEqual(instances[25]["source_align_none_count"], 0)
        self.assertEqual(instances[25]["target_align_none_count"], 0)

    
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()