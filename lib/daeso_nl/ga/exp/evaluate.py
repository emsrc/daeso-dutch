"""
Evaluation step in graph alignment experiment
"""

import logging as log
import itertools
import os

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE
from daeso.pgc.evaluate import AlignEval
from daeso.utils.opsys import makedirs
from daeso.utils.report import header


__all__ = [
    "evaluate",
    "eval_files",
    "eval_corpora"]


def evaluate(setting):
    """
    Evaluate development data
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.evaluate:
        log.info("\n" + header("EVALUATE STEP"))
        makedirs(setting.eval_dir)
            
        if setting.develop:
            setting.dev_eval = eval_files(
                setting.dev_true_fns,
                setting.dev_pred_fns,
                setting.dev_eval_fname,
                align_eval=setting.evaluator,
                n=setting.n)
             
        if setting.validate:
            setting.val_eval = eval_files(
                setting.val_true_fns,
                setting.val_pred_fns,
                setting.val_eval_fname,
                align_eval=setting.evaluator,
                n=setting.n)


def eval_files(true_fns, pred_fns, eval_fname, align_eval=None, n=None):
    """
    Evaluate predicted against true parallel graph corpora files.
    
    @param true_fns: list of true corpora filenames
    
    @param pred_fns: list of predicted corpora filenames
    
    @keyword eval_fname: name of file to which evaluation output is written 
    
    @keyword align_eval: AlignEval instance
    
    @keyword n: limit evaluation to the first n files
    """
    assert ( len(true_fns[:n]) == 
             len(pred_fns[:n]) > 0 )
    
    # use iterators so only one corpus  
    true_corpora = ( ParallelGraphCorpus(inf=true_fname,
                                          graph_loading=LOAD_NONE)
                     for true_fname in true_fns[:n] )
    
    pred_corpora = ( ParallelGraphCorpus(inf=pred_fname,
                                         graph_loading=LOAD_NONE)
                     for pred_fname in pred_fns[:n] )
    
    names = ( os.path.basename(true_fname).split("_")[0]
              for true_fname in true_fns[:n] )
    
    return eval_corpora(true_corpora, pred_corpora, names,
                        eval_fname, align_eval, n)
    
    
def eval_corpora(true_corpora, pred_corpora, names, eval_fname,
                 align_eval=None, n=None):
    """
    Evaluate predicted against true parallel graph corpora.
    
    @param true_fns: iterable of true corpora
    
    @param pred_fns: iterable of predicted corpora
    
    @param names: iterable of labels for true/predicted pairs
    
    @param eval_fname: name of file to which evaluation output is written 
    
    @keyword align_eval: AlignEval instance
    
    @keyword n: limit evaluation to the first n files
    """
    if align_eval:
        assert isinstance(align_eval, AlignEval)
        # reset evaluator to prevent accidents
        align_eval.__init__()
    else:
        align_eval = AlignEval()
    
    count = 0

    for true_corpus, pred_corpus, name in itertools.izip(true_corpora, 
                                                         pred_corpora,
                                                         names):
        align_eval.add(true_corpus, pred_corpus, name)   
        count += 1
        if count == n:
            break
        
    align_eval.run_eval()
    log.info("saving evaluation report {0}".format(eval_fname))
    makedirs(os.path.dirname(eval_fname))
    align_eval.write(eval_fname)
    return align_eval

