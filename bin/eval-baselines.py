#!/usr/bin/env python

"""
calculate simple baselines based on greedy alignment of equal words/roots

run from the exp dir which contains a data subdir with the true pgc
files and an eval subdir for evaluation results
"""

import copy
import glob
import os

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.evaluate import AlignEval
from daeso_nl.ga.kb.baseline import greedy_align_equal_words, greedy_align_equal_words_roots


eval1 = AlignEval()
eval2 = AlignEval()

for pgc_fn in glob.glob("data/part*true.pgc"):
    true_corpus = ParallelGraphCorpus(inf=pgc_fn)
    pred_corpus = copy.deepcopy(true_corpus)
    
    greedy_align_equal_words(pred_corpus)
    eval1.add(true_corpus, pred_corpus, os.path.basename(pgc_fn))
    
    greedy_align_equal_words_roots(pred_corpus)
    eval2.add(true_corpus, pred_corpus, os.path.basename(pgc_fn))
    
eval1.run_eval()
eval1.write("eval/greedy_align_equals_words.txt")
    
eval2.run_eval()
eval2.write("eval/greedy_align_equals_words_roots.txt")
    
