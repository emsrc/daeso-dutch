"""
test feature description
"""

import unittest

from daeso_nl.ga.feature import Feat
from daeso_nl.ga.descriptor import Descriptor


class Test_Descriptor(unittest.TestCase):
    
    def a_descriptor(self):
        def ff(): pass
        
        return Descriptor( Feat(ff, name="f%d" % i)
                          for i in range(5) )
            
    def test_init(self):
        self.a_descriptor()
        
    def test_descr(self):
        fd = self.a_descriptor()
        self.assertTrue(fd.descr)
        print fd.descr
        
    def test_dtype(self):
        fd = self.a_descriptor()
        self.assertTrue(fd.dtype)
        print fd.dtype
        
    def test_pprint(self):
        def pp_graph(): pass
        def pp_node(): pass
        
        fd = self.a_descriptor()
        fd["f1"].pp_graph_hooks = [pp_graph] 
        fd["f1"].pp_node_hooks = [pp_node] 
        
        print
        fd.pprint()
        

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()        
        
        
        
        
        