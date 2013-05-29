"""
testing classification and weighting of alignment relations
"""

import unittest

from daeso_nl.ga.classifier import TimblClassifier
from daeso_nl.ga.corpusinst import CorpusInst

from exp.setup import create_setting


class Test_TimblClassifier(unittest.TestCase):
    
    def test_classify(self):
        corpus_inst = CorpusInst()
        descriptor = create_setting().descriptor
        corpus_inst.loadtxt("exp/inst/dev001.inst", 
                            descriptor.dtype)
        graph_inst = corpus_inst[0]
        
        # clear relevant fields
        graph_inst["pred_relation"] = "None"
        graph_inst["pred_weight"] = 0.0

        # backup original for comparison later on
        pred_before = graph_inst["pred_relation"].copy()
        weight_before = graph_inst["pred_weight"].copy()
        
        classifier = TimblClassifier(descriptor,
                                     "exp/inst/dev001.inst")
        classifier.classify(graph_inst)
        
        # delete classifier to make sure that server is killed,
        # even if test fails
        del classifier
        
        # check that at least one prediction is different (i.e. not None)
        self.assertTrue(any(graph_inst["pred_relation"] != pred_before))
        
        # check that at least one weight is different (i.e. not 0.0)
        self.assertTrue(any(graph_inst["pred_weight"] != weight_before))
        
        
        

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()
