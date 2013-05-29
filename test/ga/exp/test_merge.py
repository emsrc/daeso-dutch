"""
test merging step of graph alignment experiment
"""

import shutil
import tempfile
import unittest

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE
from daeso.pair import Pair

from daeso_nl.ga.merger import Merger
from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.exp.merge import *

from setup import create_setting


class TestMergeFile(unittest.TestCase):
    
    def setUp(self):
        self.st = create_setting()
        # change default dir for writing predicted corpora files to a temp dir
        self.st.pred_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.st.pred_dir)
        
    def test_merge_dev(self):
        self.st.validate = False
        merge(self.st)
        self.assertEqual(len(self.st.dev_pred_fns), 
                         len(self.st.dev_true_fns))
        
        # check that there are alignments
        for pred_fname in self.st.dev_pred_fns:
            corpus = ParallelGraphCorpus(pred_fname, graph_loading=LOAD_NONE)
            align_count = sum( len(graph_pair)
                               for graph_pair in corpus)
            self.assertTrue(align_count)
            
    def test_merge_val(self):
        self.st.develop = False
        merge(self.st)
        self.assertEqual(len(self.st.val_pred_fns), 
                         len(self.st.val_true_fns))
        
        # check that there are alignments
        for pred_fname in self.st.val_pred_fns:
            corpus = ParallelGraphCorpus(pred_fname, graph_loading=LOAD_NONE)
            align_count = sum( len(graph_pair)
                               for graph_pair in corpus)
            self.assertTrue(align_count)

            
class TestMergeCorpus(unittest.TestCase):    
    
    def test_merge_corpus(self):
        st = create_setting()
        
        corpus_inst = CorpusInst()
        inst_fname = st.dev_inst_fns[0]
        corpus_inst.loadtxt(inst_fname, st.descriptor.dtype)
        
        true_fname = st.dev_true_fns[0]
        true_corpus = ParallelGraphCorpus(inf=true_fname,
                                          graph_loading=LOAD_NONE)
        pred_corpus = merge_corpus(corpus_inst, true_corpus, Merger()) 
        self.assertTrue(len(pred_corpus))
        
        for graph_inst, graph_pair in zip(corpus_inst, pred_corpus):
            for inst in graph_inst:
                rel = inst["match_relation"]
                if rel != str(None):
                    nodes = Pair(inst["source_node"], inst["target_node"] )
                    self.assertEqual(graph_pair.get_align(nodes), rel)    
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()