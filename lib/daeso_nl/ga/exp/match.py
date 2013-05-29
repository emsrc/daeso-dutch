"""
Matching step in graph alignment experiment
"""

import logging as log

from daeso.utils.opsys import glob
from daeso.utils.report import header

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.matcher import Matcher

__all__ = [ 
    "match",
    "match_files",
    "match_corpus"
]

def match(setting):
    """
    Match data
    
    @param setting: Setting instance specifying the experimental setting
    """    
    if setting.match:
        log.info("\n" + header("MATCH STEP"))
        
        if setting.develop:
            match_files(
                setting.dev_inst_fns,
                setting.matcher,
                descriptor=setting.descriptor,
                n=setting.n,
                binary=setting.binary)
        if setting.validate:
            match_files(
                setting.val_inst_fns,
                setting.matcher,
                descriptor=setting.descriptor,
                n=setting.n,
                binary=setting.binary)
    
    
def match_files(inst_fns, matcher, descriptor=None, n=None, binary=False):
    """
    Match corpus instances files
    
    @param inst_fns: list of corpus instance filenames
    
    @param matcher: a Matcher instance for matching source to target instances
    
    @keyword descriptor: a Descriptor instance, required if corpus instances
    are loaded in text format
    
    @keyword binary: corpus instances in binary rather than text format

    @keyword n: limit matching to the first n files
    """
    for inst_fname in inst_fns[:n]:
        corpus_inst = CorpusInst()    
        if binary:
            corpus_inst.loadbin(inst_fname)
        else:
            corpus_inst.loadtxt(inst_fname, descriptor.dtype)
        match_corpus(corpus_inst, matcher)
        log.info("saving matched corpus instances to {0}".format(inst_fname))
        corpus_inst.save()
        

def match_corpus(corpus_inst, matcher):
    """
    Match corpus instances
    
    @param corpus_inst: CorpusInst instance
    
    @param matcher: a Matcher instance for matching source to target instances
    """
    for graph_inst in corpus_inst:
        matcher.match(graph_inst)
    
    
