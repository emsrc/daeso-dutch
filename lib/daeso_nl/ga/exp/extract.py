"""
Extract features, create instances and true pgc files

This step extracts features from the parallel graph corpora and creates Timbl
instances. Each instance represents a possible alignment & labeling from a
node n in the source graph to a node m in the target graph. In addition, true
pgc files are generated, which may differ from the original parts because of
ignored nodes and/or graphs.
"""

import logging as log
import os
import shutil

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.utils.opsys import makedirs
from daeso.utils.report import header

from daeso_nl.ga.extractor import Extractor
from daeso_nl.ga.corpusinst import CorpusInst


__all__ = [ 
    "extract",
    "clean_inst",
    "clean_true",
    "extract_files",
    "extract_corpus"]


def extract(setting):
    """
    Extract features from corpus files, producing instance files and true
    corpus files.
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.extract:
        log.info("\n" + header("EXTRACT STEP"))
        
        makedirs(setting.inst_dir)
        makedirs(setting.true_dir)
        
        if setting.develop:
            inst_fns = setting.make_inst_fns(setting.dev_part_fns)
            true_fns = setting.make_true_fns(setting.dev_part_fns)
        
            extract_files(
                setting.extractor,
                setting.graph_selector,
                setting.dev_part_fns,
                inst_fns,
                true_fns,
                binary=setting.binary)
        if setting.validate:
            inst_fns = setting.make_inst_fns(setting.val_part_fns)
            true_fns = setting.make_true_fns(setting.val_part_fns)
            
            extract_files(
                setting.extractor,
                setting.graph_selector,
                setting.val_part_fns,
                inst_fns,
                true_fns,
                binary=setting.binary)


def clean_inst(setting):
    """
    remove directory with corpus instances
    
    @param setting: Setting instance specifying the experimental setting
    """
    shutil.rmtree(setting.inst_dir)
    
    
def clean_true(setting):
    """
    remove directory with true corpora
    
    @param setting: Setting instance specifying the experimental setting
    """
    shutil.rmtree(setting.true_dir)

    

def extract_files(extractor,
                  selector,
                  part_fns,
                  inst_fns,
                  true_fns,
                  binary=False):
    """
    Extract features from source corpus files, produce instance files and true
    corpus files.
    
    @param extractor: Extractor instance for feature extraction from graph
    pairs
    
    @param selector: boolean graph pair selection function
    
    @param part_fns: list of corpus filenames
    
    @param inst_fns: list of instance filenames to be created
    
    @param true_fns: list of true corpus filenames to be created
    
    @keyword binary: save corpus instances in binary rather than text format
    
    Note that the true corpus files may be substantially different from the
    original corpus files because of node and graph selection. 
    """
    # The reason for generating true corpus files is that it makes evaluation
    # against predicted corpus files much easier.
    assert isinstance(extractor, Extractor)
    assert len(part_fns)
    
    for part_fname, inst_fname, true_fname in zip(part_fns,
                                                  inst_fns,
                                                  true_fns):
        part_corpus = ParallelGraphCorpus(inf=part_fname)
        corpus_inst, true_corpus = extract_corpus(extractor, selector,
                                                  part_corpus)

        log.info("saving instances file {0}".format(inst_fname))
        if binary:
            corpus_inst.savebin(inst_fname)
        else:
            corpus_inst.savetxt(inst_fname)   
            
        log.info("saving true corpus file {0}".format(true_fname))
        true_corpus.write(true_fname, pprint=True)                

        
# utility functions for creating filenames, which can be used without a Setting

def make_inst_fns(inst_dir, part_fns):
    """
    Derive file paths for corpus instances from those of the corpus parts
    """
    return [ os.path.join(self.inst_dir, 
                          os.path.splitext(
                              os.path.basename(part_fname))[0] + ".inst")
             for part_fn in part_fns ]

def make_true_fns(true_dir, part_fns):
    """
    Derive file paths for new true corpora from those of the corpus parts
    """
    return [ os.path.join(self.inst_dir, 
                          os.path.splitext(
                              os.path.basename(part_fname))[0] + "_true.pgc")
             for part_fn in part_fns ]
    

def extract_corpus(extractor, selector, corpus):
    corpus_inst = CorpusInst()
    # create an empty copy, because append() is faster than __del__() or
    # remove()
    true_corpus = ParallelGraphCorpus(
        relations=corpus.get_relations(),
        meta_data=corpus.get_meta_data())
    
    for graph_pair in corpus:
        if selector(graph_pair):
            true_corpus.append(graph_pair)
            corpus_inst.append(
                extractor.extract(graph_pair))
            
    return corpus_inst, true_corpus
