"""
test feature extraction step of graph alignment experiment
"""

import unittest
import tempfile

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.descriptor import Feat
from daeso_nl.ga.corpusinst import CorpusInst

from daeso_nl.ga.exp.setting import Setting
from daeso_nl.ga.exp.extract import *

from setup import create_setting

    
class TestExtract(unittest.TestCase):
    
    def test_extract_dev(self):
        st = create_setting()
        st.validate = False
        # create tmp dirs for extraction output
        st.inst_dir = tempfile.mkdtemp()
        st.true_dir = tempfile.mkdtemp()
        
        extract(st)
        
        # check no of files
        self.assertEqual(len(st.dev_true_fns), 
                         len(st.dev_part_fns))
        self.assertEqual(len(st.dev_inst_fns), 
                         len(st.dev_part_fns))
        
        # test loading a corpus file
        corpus = ParallelGraphCorpus(inf=st.dev_true_fns[0])
        
        # test loading a instances file
        inst = CorpusInst()
        inst.loadtxt(st.dev_inst_fns[0],
                     st.descriptor.dtype)
        self.assertEqual(len(corpus), len(inst))
        
        clean_inst(st)
        clean_true(st)
        
    def test_extract_val_binary(self):
        st = create_setting()
        st.develop = False
        # create tmp dirs for extraction output
        st.inst_dir = tempfile.mkdtemp()
        st.true_dir = tempfile.mkdtemp()
        st.binary = True
        
        extract(st)
        
        # check no of files
        self.assertEqual(len(st.val_true_fns), 
                         len(st.val_part_fns))
        self.assertEqual(len(st.val_inst_fns), 
                         len(st.val_part_fns))
        
        # test loading a corpus file
        corpus = ParallelGraphCorpus(inf=st.val_true_fns[0])
        
        # test loading a instances file
        inst = CorpusInst()
        inst.loadbin(st.val_inst_fns[0])
        self.assertEqual(len(corpus), len(inst))
        
        clean_inst(st)
        clean_true(st)
        
    def test_extract_with_pp_graph_hooks(self):
        """
        test of extracting feature with preprocessing hook
        """
        st = create_setting()
        st.validate = False
        # create tmp dirs for extraction output
        st.inst_dir = tempfile.mkdtemp()
        st.true_dir = tempfile.mkdtemp()
        
        # a preprocessing function which insert an attribute "x" with value
        # "y" on every node inthe graphs
        def pp_hook1(graphs):
            for g in graphs:
                for attrs in g.node.values():
                    attrs[u"x"] = u"y"
        
        # a feature function which relies on the pp_hook above
        def ff_x(nodes, graphs, **kwargs):
            return graphs.source.node[nodes.source][u"x"]
        
        # create a feature description
        f = Feat(ff_x, "S1", pp_graph_hooks=[pp_hook1])
        
        # add to features; descriptor and extractor are automatically derived
        st.features = (f,)
        
        extract(st)
        
        # check no of files
        self.assertEqual(len(st.dev_true_fns), 
                         len(st.dev_part_fns))
        self.assertEqual(len(st.dev_inst_fns), 
                         len(st.dev_part_fns))

        # test loading a corpus file
        corpus = ParallelGraphCorpus(inf=st.dev_true_fns[0])

        # test loading a instances file
        inst = CorpusInst()
        inst.loadtxt(st.dev_inst_fns[0],
                     st.descriptor.dtype)
        self.assertEqual(len(corpus), len(inst))
        
        # check values produced by preprocessing function
        self.assertTrue(all(inst[0]["x"] == "y"))

        clean_inst(st)
        clean_true(st)

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()