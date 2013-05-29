"""
test cornet features

These test rely on the presence of a DaesoCornet server and the Cornetto
database files!
"""
SERVER = "ilk.uvt.nl:5507"

CDB_LU_FNAME = "/Users/erwin/Projects/Pycornetto/db/cdb_lu.xml"
CDB_SYN_FNAME = "/Users/erwin/Projects/Pycornetto/db/cdb_syn.xml"

import unittest

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.extractor import Extractor, select_visible_node
from daeso_nl.ga.feats import *


class TestCornetFeatures(unittest.TestCase):

    def setUp(self):
        corpus = ParallelGraphCorpus(
            inf="../exp/corpora/news/pgc/ma/2006-11/news-2006-11-aligned-part-00.pgc")
        self.graph_pair = corpus[0]
        
        descriptor = Descriptor(cornet_sim) 
        self.feat_extr = Extractor(
            descriptor,
            node_selector=select_visible_node)
        
    def test_cornet_server(self):
        create_cornet_server_proxy(SERVER)
        
        instances = self.feat_extr.extract(self.graph_pair)
        print instances
        # FIXME add asserts
        
    def test_cornet_load(self):
        print "\n(Loading Cornetto database - may take a long time...)"
        load_cornet(CDB_LU_FNAME, CDB_SYN_FNAME)
        instances = self.feat_extr.extract(self.graph_pair)
        print instances
        # FIXME add asserts
        
        
        
        
        
        
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()