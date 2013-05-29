"""
test feature extraction from graphs and corpora
"""

# TODO:
# - Hardly any tests yet. E.g no test for extract method...
    
import unittest


from daeso_nl.ga.extractor import Extractor
from daeso_nl.ga.feature import Feat
from daeso_nl.ga.descriptor import Descriptor



class Test_Extractor(unittest.TestCase):

    def test_init_1(self):
        feat_extr = Extractor(Descriptor()) 
        print
        feat_extr.descriptor.pprint()
        
    def test_init_2(self):
        """
        adding a new feature 
        """
        def ff_new_feat(**kwargs):
            return 1
        
        def pp_hook1(): pass
        
        f1 = Feat( ff_new_feat , "i", pp_graph_hooks=[pp_hook1]),
        
        fd = Descriptor(f1)
        
        e = Extractor(fd)
        print
        e.descriptor.pprint()        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()
        
    