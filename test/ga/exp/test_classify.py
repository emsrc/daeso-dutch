"""
test classification step of graph alignment experiment
"""

# When testing from within WING IDE, the PATH env var must be extended with
# the path to the Timbl executable project in the Project's environment.

import os
import tempfile
import unittest

from daeso_nl.ga.exp.classify import *

from setup import create_setting


class TestClassify(unittest.TestCase):
    
    def setUp(self):
        self.st = create_setting()
        self.st.clas_dir = tempfile.mkdtemp()
        self.st.timbl_log = True
        self.st.timbl_opts = "-k2"
        self.st.n = 2
        
    def tearDown(self):
        clean_clas(self.st)
    
    def test_classify_dev(self):
        self.st.validate = False
        self.st.n = 2
        # classify() does not set  self.st.timbl_opts
        #self.assertTrue(self.st.timbl_opts in self.st.classifier.default_opts)
        classify(self.st)
        
        inst_fns = self.st.dev_inst_fns[:self.st.n]
        out_fns = self.st.dev_clas_fns
        self.assertEqual(len(out_fns), len(inst_fns))
        for out_fname in out_fns:
            self.assertTrue(os.path.exists(out_fname))
        
    def test_classify_val(self):
        self.st.develop = False
        # classify() does not set  self.st.timbl_opts
        #self.assertTrue(self.st.timbl_opts in self.st.classifier.default_opts)
        classify(self.st)
        
        out_fns = self.st.val_clas_fns
        self.assertEqual(len(out_fns), 
                         len(self.st.val_inst_fns))
        for out_fname in out_fns:
            self.assertTrue(os.path.exists(out_fname))
        

if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main() 

