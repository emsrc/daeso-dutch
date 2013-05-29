"""
test sampling step
"""

import unittest

from daeso_nl.ga.exp.sample import *

from setup import create_setting

from tt.sample import get_class_counts


class TestSample(unittest.TestCase):
    
    def setUp(self):
        self.st = create_setting()
        self.st.sample = True
        self.st.samp_dir = self.st.make_tmp_dir()
        
    def tearDown(self):
        clean_samp(self.st)
    
    def test_sample(self):
        fractions = [i/10.0 for i in range(1,10)]
        for fract in fractions:
            self.st.class_fracts = {"None": fract}
            sample(self.st)
        
            for inst_fname, samp_fname in zip(self.st.dev_inst_fns,
                                              self.st.dev_samp_fns):
                inst_counts = get_class_counts(inst_fname)
                target = inst_counts["None"] * fract
                samp_counts = get_class_counts(samp_fname)
                approx = samp_counts["None"]
                diff = abs(target - approx)
                err =  (diff * 100.0) / float(target)
                #print diff, err
                
                # check that error percentage < 5% of the target
                self.assertTrue(err < 5.0)
            
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()