"""
test alignment experiment
"""

import os
import pickle
import shutil
import unittest

from daeso_nl.ga.exp.experiment import *

from setup import create_setting
import partition


class TestExperiment(unittest.TestCase):
        
    def test_exp(self):
        try:
            st = create_setting()
            # include parting step
            st.part=True
            st.dev_parts=partition.dev_parts
            st.val_parts=partition.val_parts
            st.part_max_size = 1
            st.exp_dir = st.make_tmp_dir()
        
            st.validate = False
            exp(st)
            self.assertTrue(os.path.exists(st.dev_eval_fname))
            
            st.develop = False
            st.validate = True
            exp(st)
            self.assertTrue(os.path.exists(st.val_eval_fname))
            
        finally:
            shutil.rmtree(st.exp_dir)
        
    def test_exp_dev_fast(self):
        try:
            st = create_setting()
            st.validate = False
            st.extract = False
            st.classify = False
            st.eval_dir = st.make_tmp_dir()
        
            exp_dev_fast(st)
            
            self.assertTrue(os.path.exists(st.dev_eval_fname))
        finally:
            shutil.rmtree(st.eval_dir)
            
    def test_pickle(self):
        st = create_setting()
        st.part = False
        st.extract = False
        st.weight = False
        st.match = False
        st.merge = False
        st.eval_dir = st.make_tmp_dir()
        st.pickle = True
        st.pickle_dir = st.make_tmp_dir()
        exp(st)
        pkl_file = open(st.pickle_fname, "rb")
        st2 = pickle.load(pkl_file)
        
        
class TestExpSequence(unittest.TestCase):
        
    def test_exp_sequence(self):
        """
        test sequence of exps to make sure that changing timbl options works
        and that re-using evaluator works
        """
        try:
            st = create_setting()
            st.validate = False
            st.exp_dir = st.make_tmp_dir()
            st.extract = False
            shutil.copytree("inst", st.inst_dir) 
            st.true_dir = "true"
            st.n = 1
            
            # on this limited featureset, changing -k or -w will not change
            # the scores, so we change the algorithm
            st.timbl_opts = "-a1 +D"
            exp(st)
            score1 = st.evaluator.measure_stats["f"]["micro"]["mean"]
            
            st.timbl_opts = None
            exp(st)
            score2 = st.evaluator.measure_stats["f"]["micro"]["mean"]
            self.assertNotEqual(score1, score2)
            
            st.timbl_opts = "-a1 +D"
            exp(st)
            score3 = st.evaluator.measure_stats["f"]["micro"]["mean"]
            self.assertAlmostEqual(score1, score3, 4)
        finally:
            shutil.rmtree(st.exp_dir)
        
            
            
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()