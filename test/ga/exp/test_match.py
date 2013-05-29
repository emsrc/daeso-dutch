"""
test matching step of graph alignment experiment
"""

import os
import shutil
import tempfile
import unittest

from daeso_nl.ga.matcher import Matcher
from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.exp.match import *

from setup import create_setting



class TestMatchFile(unittest.TestCase):
    
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
        
    def test_match_dev(self):
        self.st.validate = False
        match(self.st)
        
    def test_match_val(self):
        self.st.develop = False
        match(self.st)
        


class TestMatchCorpus(unittest.TestCase):        

    def test_match_corpus(self):
        st = create_setting()
        corpus_inst = CorpusInst()
        inst_fname = st.dev_inst_fns[0]
        corpus_inst.loadtxt(inst_fname, 
                            st.descriptor.dtype)
        graph_inst = corpus_inst[0]
        
        # clear pred_match field
        graph_inst["match_relation"] = str(None)
        # backup original for comparison later on
        match_before = graph_inst["match_relation"].copy()
        
        match_corpus(corpus_inst, Matcher())
        
        # check that at least one relation is different (i.e. not None)
        self.assertTrue(any(graph_inst["match_relation"] != match_before))
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()