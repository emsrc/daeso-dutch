"""
Sampling

This step performs downsampling on the training instances to compensate for
the heavily skewed distribution: "None", i.e. "no aligment", is by far the
majority class.
"""

# TODO:
# - quick & dirty sampling is inaccurate (can make errors of 5% or more)
# - sampling is now on Timbl instance files, but should be on CorpusInst object

import glob
import logging as log
import shutil

from daeso.utils.opsys import makedirs
from daeso.utils.report import header

import tt.sample 


__all__ = [
    "sample",
    "clean_samp",
    "sample_file"]


def sample(setting):
    """
    Sample training data
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.sample:
        log.info("\n" + header("SAMPLE STEP"))
        makedirs(setting.samp_dir)
        
        if setting.develop:
            samp_fns = setting.make_samp_fns(setting.dev_inst_fns)

            sample_file(
                setting.class_fracts,
                setting.dev_inst_fns,
                samp_fns)
        if setting.validate:
            samp_fns = setting.make_samp_fns(setting.val_inst_fns)
            
            sample_file(
                setting.class_fracts,
                setting.val_inst_fns,
                samp_fns)
    
            
def clean_samp(setting):
    """
    remove directory with sampled instances
    
    @param setting: Setting instance specifying the experimental setting
    """
    shutil.rmtree(setting.samp_dir)

    

def sample_file(class_fracts,
                inst_fns,
                samp_fns):
    """
    Sample-down original instances and save to new corpus instance files.
    These can then be used for training only, while the originals are used for
    testing.
    
    @param class_fraction: a dict with class labels (strings) as keys and
    fractions (floats between 0.0. and 1.0) as values.
    
    @param inst_fns: a list of corpus instance files
    
    @param samp_fns: a list of down-sampled corpus instances files
    """
    assert class_fracts
    assert len(inst_fns) == len(samp_fns) > 0
    
    for inst_fn, samp_fn in zip(inst_fns, samp_fns):
        log.info("saving sample file {0}".format(samp_fn))
        tt.sample.sample_down(inst_fn, class_fracts, outf=samp_fn)
        
            