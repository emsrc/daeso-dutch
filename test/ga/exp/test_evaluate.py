"""
test evaluation step of graph alignment experiment
"""

import os
import shutil
import unittest

from daeso_nl.ga.exp.evaluate import *

from setup import create_setting


class TestEvaluate(unittest.TestCase):
    
    def setUp(self):
        self.st = create_setting()
        # copy instances to tmp location
        self.st.eval_dir = self.st.make_tmp_dir()
        
    def tearDown(self):
        shutil.rmtree(self.st.eval_dir)
    
    def test_evaluate_dev(self):
        self.st.validate = False
        evaluate(self.st)
        self.assertTrue(os.path.exists(self.st.dev_eval_fname))
        
    def test_evaluate_val(self):
        self.st.develop = False
        evaluate(self.st)
        self.assertTrue(os.path.exists(self.st.val_eval_fname))
        


if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()