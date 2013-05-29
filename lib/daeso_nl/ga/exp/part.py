"""
Create parts

This step creates the parallel graph corpora which serve as parts in cross
validation experiments. Each part is created by concatenating a number of pgc
files. This requires a partitioning of the available corpus files, which is
normally automatically generated using the partition.py script.
"""

import logging as log
import os
import shutil
import warnings


from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE
from daeso.utils.opsys import makedirs
from daeso.exception import DaesoWarning
from daeso.utils.report import header


__all__ = ["create_parts",
           "create_part_files",
           "clean_parts"]


def create_parts(setting):
    """
    Create the parallel graph corpora constituting the data parts for
    development and validation
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.part:
        log.info("\n" + header("PARTING STEP"))
        
        if setting.develop:
            create_part_files(
                setting.dev_parts,
                base_dir=setting.corpus_dir,
                part_dir=setting.part_dir,
                max_size=setting.part_max_size)
        if setting.validate:
            create_part_files(
                setting.val_parts,
                base_dir=setting.corpus_dir,
                part_dir=setting.part_dir,
                max_size=setting.part_max_size)
    

def clean_parts(setting):
    """
    remove directory with parts
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.part:
        shutil.rmtree(setting.part_dir)


def create_part_files(parts, 
                      base_dir=os.getenv("DAESO_CORPUS"),
                      part_dir=None,
                      max_size=None):
    """
    Create the parallel graph corpora constituting the parts for training and
    testing
    
    @param parts: a dictionary where each key specifies the filename for the
    part and each value a sequence of parallel graph corpora filenames merged
    into the part
    
    @keyword base_dir: filename paths of the original corpus files must be
    relative to base_dir
    
    @keyword part_dir: the destination directory for the parts, which will be
    created if it does not exist.
    
    @keyword max_size: limits the maximal number of corpus files per part,
    which is sometimes useful for try-out experiments with only a small number
    of corpus files.
    
    @return: a list of part filenames created
    
    Note that the created parts cannot be moved, because they depend on the
    graph bank files of the original pgc files from which they were derived.
    """
    if not part_dir:
        part_dir = os.getcwd()
    else:
        makedirs(part_dir)

    part_fnames = []
        
    for part_name, corpus_fnames in sorted(parts.items()):
        part_fname = os.path.join(part_dir, part_name)
        corpus_fnames = [ os.path.join(base_dir, fname) 
                          for fname in corpus_fnames ]
        corpus = join_pgc(corpus_fnames[:max_size])

        # graphbank file paths by default become relative to the new pgc file
        log.info("saving part file {0}".format(part_fname))
        corpus.write(part_fname, pprint=True)
        part_fnames.append(part_fname)
        
    return part_fnames


def join_pgc(corpus_fnames):
    """
    join parallel graph corpora
    
    @param corpus_fnames: list of parallel graph corpora filenames
    
    @return: new ParallelGraphCorpus object
    
    Corpora are assumed to have the same relations.
    Graphbanks are not read, but graphbanks in the result are purged.
    """
    corpus = ParallelGraphCorpus(inf=corpus_fnames.pop(),
                                 graph_loading=LOAD_NONE)
    
    # suppress DaesoWarning: meta data of other corpus is discarded!
    warnings.filterwarnings('ignore', category=DaesoWarning)
    
    for fname in corpus_fnames:
        corpus += ParallelGraphCorpus(inf=fname, graph_loading=LOAD_NONE)
        
    # corpus.purge() not required, as it is called during corpus.write
    return corpus
    
