"""
test weighting step of graph alignment experiment
"""

import os
import shutil
import tempfile
import unittest

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.classifier import entropy_weight
from daeso_nl.ga.exp.weight import weight, weight_corpus

from setup import create_setting

from tt.outparser import parse_timbl_output


        
class TestWeightFile(unittest.TestCase):
        
    def setUp(self):
        self.st = create_setting()
        # copy instances to tmp location
        inst_dir = tempfile.mkdtemp()
        os.rmdir(inst_dir)
        shutil.copytree(self.st.inst_dir, inst_dir)
        # change defaults
        self.st.inst_dir = inst_dir
        self.st.n = 2
        
    def tearDown(self):
        shutil.rmtree(self.st.inst_dir)
        
    def test_weight_dev(self):
        self.st.validate = False
        weight(self.st)
        
    def test_weight_val(self):
        self.st.develop = False
        weight(self.st)
        

        
class TestWeightCorpus(unittest.TestCase):

    def test_weight_corpus(self):
        st = create_setting()
        corpus_inst = CorpusInst()
        inst_fname = st.dev_inst_fns[0]
        corpus_inst.loadtxt(inst_fname, 
                            st.descriptor.dtype)
        graph_inst = corpus_inst[0]
        
        # clear predicted weights field
        graph_inst["pred_weight"] = 0.0
        # backup original for comparison later on
        weight_before = graph_inst["pred_weight"].copy()
        
        out_fname = st.dev_clas_fns[0]
        timbl_out = parse_timbl_output(open(out_fname))
        
        weight_corpus(corpus_inst,
                      timbl_out,
                      entropy_weight)
        
        # check that at least one weight is different (i.e. not 0.0)
        self.assertTrue(any(graph_inst["pred_weight"] != weight_before))        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()