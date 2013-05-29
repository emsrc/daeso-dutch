"""
Merging step in graph alignment experiment
"""

import copy
import logging as log

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE
from daeso.utils.opsys import makedirs
from daeso.utils.report import header

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.merger import Merger


__all__ = [ 
    "merge",
    "merge_files",
    "merge_corpus"
]


def merge(setting):
    """
    Merge data
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.merge:
        log.info("\n" + header("MERGE STEP"))        
        makedirs(setting.pred_dir)
        
        if setting.develop:
            pred_fns = setting.make_pred_fns(setting.dev_true_fns)
            
            merge_files(
                setting.dev_inst_fns, 
                setting.dev_true_fns,
                pred_fns,
                merger=setting.merger, 
                descriptor=setting.descriptor, 
                n=setting.n, 
                binary=setting.binary)
        if setting.validate:
            pred_fns = setting.make_pred_fns(setting.val_true_fns)
            
            merge_files(
                setting.val_inst_fns, 
                setting.val_true_fns,
                pred_fns,
                merger=setting.merger, 
                descriptor=setting.descriptor, 
                n=setting.n, 
                binary=setting.binary)
  
    
        
def merge_files(inst_fns, true_fns, pred_fns, merger=Merger(),
                descriptor=None, n=None, binary=False):
    """
    Merge corpus instance files
    
    @param inst_fns: list of corpus instance filenames
    
    @param true_fns: list of corpus filenames containing the true alignments

    @param pred_fns: list of predicted corpus filenames to be created
    
    @param merger: instance of Merger class for merging instances into a graph
    pair
    
    @keyword descriptor: a Descriptor instance, required if corpus instances
    are loaded in text format
    
    @keyword n: limit merging to the first n files
    
    @keyword binary: corpus instances in binary rather than text format
    """
    assert isinstance(merger, Merger)
    assert len(inst_fns) == len(true_fns) > 0
    
    for inst_fname, true_fname, pred_fname in zip(inst_fns,
                                                  true_fns,
                                                  pred_fns)[:n]:
        corpus_inst = CorpusInst()
        
        if binary:
            corpus_inst.loadbin(inst_fname)
        else:
            corpus_inst.loadtxt(inst_fname, descriptor.dtype)
            
        true_corpus = ParallelGraphCorpus(inf=true_fname,
                                          graph_loading=LOAD_NONE)
        pred_corpus = merge_corpus(corpus_inst, true_corpus, merger)
        log.info("saving predictd corpus {0}".format(inst_fname))
        pred_corpus.write(pred_fname)


def merge_corpus(corpus_inst, true_corpus, merger):
    """
    Merge matched relations from corpus instances into a new predicted corpus
    derived from a true corpus.
    
    @param corpus_inst: CorpusInst object containing the instances for a
    corpus of aligned parallel graphs
    
    @param true_corpus: a ParallelGraphCorpus instance containing the true
    alignments; remains untouched
    
    @param merger: instance of Merger class for merging instances into a
    graph pair
    
    @return: a new ParallelGraphCorpus instance containing the predicted
    alignments
    """
    # This copies the graph pairs as well, so the true corpus remains
    # untouched. However, it might be  cheaper to just create new graph pairs? 
    pred_corpus = copy.deepcopy(true_corpus)
    
    for graph_inst, graph_pair in zip(corpus_inst, pred_corpus):
        graph_pair.clear()
        merger.merge(graph_inst, graph_pair)
        
    return pred_corpus
    

