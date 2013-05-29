"""
testing matching of nodes for graphs and corpora
"""

import unittest

from daeso_nl.ga.matcher import Matcher
from daeso_nl.ga.corpusinst import CorpusInst

from exp.setup import create_setting


class Test_Matcher(unittest.TestCase):
    
    def test_match(self):
        corpus_inst = CorpusInst()
        dtype = create_setting().descriptor.dtype
        corpus_inst.loadtxt("exp/inst/dev001.inst", dtype)
        graph_inst = corpus_inst[0]

        graph_inst["match_relation"] = "None"
        match_before = graph_inst["match_relation"].copy()

        gm = Matcher()
        gm.match(graph_inst)

        ## print graph_inst["match_relation"]
        # check that at least one match is different 
        self.assertTrue(any(graph_inst["match_relation"] != match_before))
        

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()