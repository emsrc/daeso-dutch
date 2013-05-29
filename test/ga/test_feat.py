"""
test properties of single features
"""

import unittest

from daeso.exception import DaesoError

from daeso_nl.ga.feature import Feat, ff_none


    
class TestFeat(unittest.TestCase):
    
    def test_defaults(self):
        f = Feat()
        self.assertEqual(f.type, "i")
        self.assertEqual(f.function, ff_none)
        self.assertEqual(f.metric, "O")
        self.assertEqual(f.name, "none")

    
    def test_default_name(self):
        def xxx(): pass
        
        self.assertRaises(DaesoError, Feat, xxx)
        
        
    def test_metric_change(self):
        f = Feat()
        f.metric = "I"
        self.assertEqual(f.metric, "I")
        
        
    def test_print(self):
        def ff_myfeat(): pass
        
        print Feat(ff_myfeat, "U24", "O")
        
        

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()
                
        
        