"""
test baselines
"""

import copy
import unittest

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.evaluate import AlignEval

from daeso_nl.ga.kb.baseline import *



class TestBaseline(unittest.TestCase):
    
    def setUp(self):
        fn = ( "../exp/corpora/news/pgc/ma/2006-11/"
               "news-2006-11-aligned-part-00.pgc" )
        self.true_pgc = ParallelGraphCorpus(inf=fn)
        
    def test_word_baseline_1(self):
        # evaluation is incorrect, because true corpus also contains phrase
        # alignments
        print "Baseline: greedy_align_equal_words_roots"
        pred_pgc = copy.deepcopy(self.true_pgc)
        greedy_align_equal_words_roots(pred_pgc)
        align_eval = AlignEval()
        align_eval.add(self.true_pgc, pred_pgc)
        align_eval.run_eval()
        align_eval.write_alignment_overall()
    
    def test_word_baseline_2(self):
        # evaluation is incorrect, because true corpus also contains phrase
        # alignments
        print "Baseline: greedy_align_words"
        pred_pgc = copy.deepcopy(self.true_pgc)
        greedy_align_words(pred_pgc)
        align_eval = AlignEval()
        align_eval.add(self.true_pgc, pred_pgc)
        align_eval.run_eval()
        align_eval.write_alignment_overall()
        
    def test_word_baseline_3(self):
        print "Baseline: greedy_align_phrases"
        pred_pgc = copy.deepcopy(self.true_pgc)
        greedy_align_phrases(pred_pgc)
        align_eval = AlignEval()
        align_eval.add(self.true_pgc, pred_pgc)
        align_eval.run_eval()
        align_eval.write_alignment_overall()
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()        
        