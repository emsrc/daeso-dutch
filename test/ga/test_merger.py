"""
testing merging for graphs and corpora
"""

import unittest

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.merger import Merger
from daeso_nl.ga.corpusinst import CorpusInst

from exp.setup import create_setting


class Test_Merger(unittest.TestCase):
    
    def test_merge(self):
        corpus_inst = CorpusInst()
        dtype = create_setting().descriptor.dtype
        corpus_inst.loadtxt("exp/inst/dev001.inst", dtype)
        graph_inst = corpus_inst[0]
        
        pgc = ParallelGraphCorpus(inf="exp/true/dev001_true.pgc")
        graph_pair = pgc[0]
        
        gm = Merger()
        gm.merge(graph_inst, graph_pair)
        
        

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()