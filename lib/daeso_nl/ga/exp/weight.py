"""
Weighting of relation predictions
"""

import logging as log

from daeso.utils.report import header

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.classifier import entropy_weight

from tt.outparser import parse_timbl_output, parse_inst, parse_distrib


__all__ = [ 
    "weight",
    "weight_files",
    "weight_corpus"]


def weight(setting):
    """
    Weight predictions
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.weight:
        log.info("\n" + header("WEIGHT STEP"))
        
        if setting.develop:
            weight_files(
                setting.dev_inst_fns,
                setting.dev_clas_fns,
                setting.weight_func, 
                descriptor=setting.descriptor,
                n=setting.n,
                binary=setting.binary)
        if setting.validate:
            weight_files(
                setting.val_inst_fns,
                setting.val_clas_fns,
                setting.weight_func, 
                descriptor=setting.descriptor,
                n=setting.n,
                binary=setting.binary)

    
def weight_files(inst_fns, out_fns, weight_func=entropy_weight,
                 descriptor=None, n=None, binary=False):
    """
    Weight corpus instance files
    
    @param inst_fns: list of corpus instance filenames
    
    @param out_fns: list of filenames containing Timbl output
    
    @keyword weight_func: weighting fuction
    
    @keyword descriptor: a Descriptor instance, required if corpus instances
    are loaded in text format

    
    @keyword n: limit merging to the first n files
    """
    for inst_fname, out_fname in zip(inst_fns, out_fns)[:n]:
        corpus_inst = CorpusInst()
        if binary:
            corpus_inst.loadbin(inst_fname)
        else:
            corpus_inst.loadtxt(inst_fname, descriptor.dtype)
            
        timbl_out = parse_timbl_output(open(out_fname))
        weight_corpus(corpus_inst, timbl_out, weight_func)
        log.info("saving weighted corpus instances to {0}".format(inst_fname))
        corpus_inst.save()


def weight_corpus(corpus_inst, timbl_out, weight_func):
    """
    Weight corpus instances
    
    @param corpus_inst: CorpusInst instance
    
    @param timbl_out: iterator over Timbl output
    
    @param weight_func: weighting fuction
    """
    for graph_inst in corpus_inst:
        for inst, (inst_str, k_nn_list) in zip(graph_inst, timbl_out):
            feats_str, true_class, pred_class, distrib_str, distance = \
            parse_inst(inst_str, with_distrib=True, with_distance=True) 
            
            inst["pred_relation"] = pred_class            
            inst["pred_weight"] = weight_func(
                category=pred_class, 
                distribution=parse_distrib(distrib_str))
        
    