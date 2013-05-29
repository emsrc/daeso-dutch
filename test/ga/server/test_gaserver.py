# -*- coding: utf-8 -*-

"""
test graph alignment server
"""

    
import unittest
import os

from daeso_nl.ga.server import AlignServer

from daeso_nl.ga import feats
from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.extractor import TimblExtractor

from tt.server import TimblServer






class Test_GraphAlignServer(unittest.TestCase):
    """
    Tests with an immediate GraphAlignSrver instance
    """
    
    def setUp(self):
        self.init_feat_extractor()
        self.setup_timbl_server()
        self.gaserver = AlignServer(feat_extractor=self.feat_extractor)
        self.s1 = "Ik ben één zin .".decode("utf-8")
        self.s2 = "Ik ben ook een zin .".decode("utf-8")
        

    def init_feat_extractor(self):
        # create base feature description
        descriptor = Descriptor.fromfeats(feats.same_root + feats.same_pos)
        self.feat_extractor = TimblExtractor(
            descriptor,
            node_selector=TimblExtractor.select_lexical_node) 
        # get feature descrition including administrative features for Timbl
        self.descriptor = self.feat_extractor.descriptor
        
        
    def setup_timbl_server(self):
        options = "+vo +vdb +vdi %s -f %s" % (
            self.descriptor.metrics,
            os.path.abspath("data/base.inst"))
        # Timbl server will automatically terminate when TimblServer object
        # dies, so keep a reference to it
        self.server = TimblServer(options=options)
        self.server.start()

        
    def test_1(self):
        result = self.gaserver.align(self.s1, self.s2)
        
        
   
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()
        
    