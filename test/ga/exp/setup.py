"""
Shared code to set up the sample data for unittesting

These functions are called to prepare the sample data required for unit
testing. They need to be called only when the corpus, the classifier (Timbl)
or some other essential part changes. The sample data is under version
control. Unittest must have read-only access, writing their output to
temporary files.
"""

from daeso_nl.ga import feats
from daeso_nl.ga.extractor import ( Extractor, select_lexical_node,
                                    select_aligned_graph_pair )
from daeso_nl.ga.exp.setting import Setting
from daeso_nl.ga.exp.partition import create_partition, write_partition
from daeso_nl.ga.exp.part import create_parts, clean_parts
from daeso_nl.ga.exp.extract import extract
from daeso_nl.ga.exp.sample import sample
from daeso_nl.ga.exp.classify import classify
from daeso_nl.ga.exp.weight import weight
from daeso_nl.ga.exp.match import match
from daeso_nl.ga.exp.merge import merge

from daeso_nl.utils.globbing import relglob


#-------------------------------------------------------------------------------
# Experimental setting
#-------------------------------------------------------------------------------

def create_setting():
    """
    Create setting for unittest experiments
    """
    return Setting(
        validate=True,
        corpus_dir="corpora",
        features = feats.same_root + feats.same_pos,
        graph_selector = select_aligned_graph_pair,
        node_selector = select_lexical_node,
        sample=True,
        class_fracts = {"None": 0.5},
        train_sample=True)

#-------------------------------------------------------------------------------
# Partitioning step
#-------------------------------------------------------------------------------

def create_sample_partition(setting):
    """
    Create a sample partition and save as ./partition.py
    
    This assumes a sample corpus under "corpus" subdir 
    """
    corpus_fnames = relglob(setting.corpus_dir, "news/pgc/ma/2006-11/*.pgc")
    partition = create_partition(corpus_fnames, corpus_dir=setting.corpus_dir,
                                 dev_bins=4, val_bins=1)
    write_partition(*partition, out="partition.py")
    

#-------------------------------------------------------------------------------
# Parting step
#-------------------------------------------------------------------------------

def create_sample_parts(setting):
    """
    Create the parts in "./parts" subdir. 
    
    This assumes a sample corpus under the"corpus" subdir and corresponding
    partitioning in ./partition.py
    
    part_max_size is set to 1 (only 1 pgc file per part) to keep testing fast
    
    Produces part/dev001.pgc, ..., part/dev004.pgc and part/val001.pgc
    """
    # import partition.py here, because if it is imported at the module level,
    # we cannot use create_partition to create a new one
    import partition
    setting.part = True
    setting.dev_parts=partition.dev_parts
    setting.val_parts=partition.val_parts
    setting.part_max_size = 1
    create_parts(setting)
    
#-------------------------------------------------------------------------------
# Extraction step
#-------------------------------------------------------------------------------

def create_sample_instances(setting): 
    """
    Create the sample corpus instance files and the sample true pgc files in
    the ./inst and ./true subdirs respectively. 
    
    This assumes pgc part files are present in the ./part subdir. 
    
    Produces inst/dev001.inst, ..., inst/dev004.inst and
    true/dev001_true.pgc, ..., true/dev004_true.pgc
    """
    extract(setting)
    
#-------------------------------------------------------------------------------
# Sampling step
#-------------------------------------------------------------------------------

def create_sample_downsampled_instances(setting): 
    """
    Create downsampled corpus instance files 
    
    This assumes corpus instance files in de ./inst subdir
    
    
    Produces samp/dev001.inst, ..., samp/dev004.inst and samp/val001.inst
    """
    sample(setting)
    
#-------------------------------------------------------------------------------
# Classification step 
#-------------------------------------------------------------------------------

def create_sample_predictions(setting):
    """
    Classify instances using Timbl, creating output instances and log files
    
    This assumes corpus instance files in de ./inst subdir
    
    Produces clas/dev001.out, ..., clas/dev004.out and clas/val001.out
    """
    classify(setting)
    
#-------------------------------------------------------------------------------
# Weighting step 
#-------------------------------------------------------------------------------

def create_sample_weightings(setting):
    """
    Add prediction and weightings to the sample instances
    
    This assumes corpus instance files in de ./inst subdir and classifier
    output in the ./clas subdir.
    
    Fills the instance fields "pred_relation" and "pred_weight" 
    """
    weight(setting)
    
#-------------------------------------------------------------------------------
# Matching step 
#-------------------------------------------------------------------------------

def create_sample_matchings(setting):
    """
    Add matchings to the sample instances
    
    This assumes corpus instance files in de ./inst subdir
    
    Fills the instance fields "match_relation".
    """
    match(setting)

#-------------------------------------------------------------------------------
# Merging step 
#-------------------------------------------------------------------------------

def create_sample_mergings(setting):
    """
    Merge final predictions (i.e. after matching) into a new parallel graph
    corpus containing the predicted alignments.
    
    This assumes corpus instance files in the ./inst subdir and true parallel
    graph corpus files in de ./true subdir
    
    Produces pred/dev001_pred.pgc, ..., pred/dev001_pred.pgc, val001_pred.pgc
    """
    merge(setting)

#-------------------------------------------------------------------------------
# Setup test experiment
#-------------------------------------------------------------------------------
    
def setup_test_exp():
    """
    Setup sample data for running the unittests under daeso-dutch/test/ga/exp
    """
    setting = create_setting()
    create_sample_partition(setting)
    create_sample_parts(setting)
    create_sample_instances(setting)
    create_sample_downsampled_instances(setting)
    create_sample_predictions(setting)
    create_sample_weightings(setting)
    create_sample_matchings(setting)
    create_sample_mergings(setting)
    
    
    
if __name__ == '__main__':
    setup_test_exp()
    
    