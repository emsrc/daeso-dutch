"""
test creation of parts
"""

import unittest

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.exp.part import *

from setup import create_setting

import partition

    
class Test_Parts(unittest.TestCase):
    
    def test_create_parts_dev(self):
        st = create_setting()
        st.part = True
        st.validate = False
        st.dev_parts=partition.dev_parts
        st.part_dir = st.make_tmp_dir()
        st.part_max_size = 2

        create_parts(st)
        
        self.assertTrue(st.dev_parts)
        self.assertEqual(len(st.dev_parts), len(st.dev_part_fns))
                         
        # test if the part is readable
        ParallelGraphCorpus(inf=st.dev_part_fns[0])
        
        clean_parts(st)
    
    def test_create_parts_val(self):
        st = create_setting()
        st.part = True
        st.develop = False
        st.val_parts=partition.val_parts
        st.part_dir = st.make_tmp_dir()
        
        create_parts(st)
        
        self.assertTrue(st.val_parts)
        self.assertEqual(len(st.val_parts), len(st.val_part_fns))
                         
        # test if the part is readable
        ParallelGraphCorpus(inf=st.val_part_fns[0])
        
        clean_parts(st)
    

if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()
