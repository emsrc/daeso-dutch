"""
Classify alignment relations
"""

import logging as log
import shutil

from daeso.utils.opsys import makedirs
from daeso.utils.report import header

from daeso_nl.ga.classifier import timbl_options_string

from tt.timblfile import TimblFile

__all__ = [
    "classify",
    "clean_clas",
    "classify_file",
    "classify_file_cv"]


def classify(setting):
    """
    Classify corpus instances

    @param setting: Setting instance specifying the experimental setting
    """    
    if setting.classify:
        log.info("\n" + header("CLASSIFY STEP"))
        
        makedirs(setting.clas_dir)
        
        if setting.train_sample:
            train_inst_fns = setting.dev_samp_fns
        else:
            train_inst_fns = setting.dev_inst_fns
        
        if setting.develop:
            classify_file_cv(
                train_inst_fns,
                test_inst_fns=setting.dev_inst_fns,
                out_fns=setting.make_out_fns(setting.dev_inst_fns),
                log_fns=setting.make_log_fns(setting.dev_inst_fns),
                descriptor=setting.descriptor,
                timbl=setting.classifier,
                options=setting.timbl_opts,
                n=setting.n,
                log=setting.timbl_log)
        if setting.validate:
            classify_file(
                train_inst_fns,
                setting.val_inst_fns,
                out_fns=setting.make_out_fns(setting.val_inst_fns),
                log_fn=setting.make_log_fname(setting.val_inst_fns[0]),
                descriptor=setting.descriptor,
                timbl=setting.classifier,
                options=setting.timbl_opts,
                log=setting.timbl_log)
        
    
def clean_clas(setting):
    """
    remove directory with classifier output
    
    @param setting: Setting instance specifying the experimental setting
    """
    if setting.classify:
        shutil.rmtree(setting.clas_dir)    

    
def classify_file_cv(inst_fns,
                     test_inst_fns=None,
                     out_fns=None,
                     log_fns=None,
                     clas_dir=None,
                     descriptor=None,
                     timbl=None,
                     options="",
                     n=None,
                     log=False):
    """
    Classify instance using Timbl in a cross-validation procedure.
    
    @param inst_fns: a list of instance filenames for training; if no
    test_inst_fns is supplied, the same files will be used for testing,
    otherwise they are used for training only
    
    @keyword test_inst_fns: a list of instance filenames for testing; this
    allows for down-sampling of the training instances without affecting the
    test instances
    
    @keyword out_fns: list of classifier output files to be created
    
    @keyword log_fns: list of classifier log files to be created; 
    ignored if keyword log is false
    
    @keyword clas_dir: directory for creating classifier output files; ignored
    if out_fns is given
    
    @keyword descriptor: a Descriptor instance, required to infer the feature
    metrics for Timbl, unless a TimblFile is supplied; ignored if timbl is
    supplied
    
    @keyword timbl: a tailored TimblFile instance; notice that it must at
    least set the verbosity options +vo, +vdb, +vdi, and the -m option to
    specify that the administrative features must be ignored.
    
    @keyword options: list of additional Timbl options, excluding -f, -m, +vo,
    +vdb, +vdi
    
    @keyword n: limit on the number of cross-validations performed (by default
    equals the number of instance filenames)
    
    @keyword log: log Timbl's standard output and error streams to file
    
    @return: list of Timbl output filenames
    """
    if clas_dir:
        makedirs(clas_dir)
        
    if not timbl:
        assert descriptor
        timbl = TimblFile(default_opts=timbl_options_string(descriptor))
    else:
        # ignore descriptor
        assert isinstance(timbl, TimblFile)
        assert "+vo" in timbl.default_opts
        assert "+vdb" in timbl.default_opts
        assert "+vdi" in timbl.default_opts
        assert "-m" in timbl.default_opts
    
    return timbl.cross_validate(inst_fns, test_inst_fns=test_inst_fns,
                                out_fns=out_fns, log_fns=log_fns, options=options, n=n, log=log,
                                out_dir=clas_dir)



def classify_file(train_inst_fns,
                  test_inst_fns,
                  out_fns=None,
                  log_fn=None,
                  clas_dir=None,
                  descriptor=None,
                  timbl=None,
                  options="",
                  log=False):
    """
    Classify instances using Timbl
    
    @param train_inst_fns: a list of instance filenames for training

    @param test_inst_fns: a list of instance filenames for testing
    
    @keyword out_fns: list of classifier output files to be created
    
    @keyword log_fn: classifier log file to be created;
    ignored if keyword log is false
    
    @keyword clas_dir: directory for creating classifier output files; ignored
    if out_fns is given
    
    @keyword descriptor: a Descriptor instance, required to infer the feature
    metrics for Timbl, unless a TimblFile is supplied; ignored if timbl is
    supplied
    
    @keyword timbl: a tailored TimblFile instance; notice that it must at
    least set the verbosity options +vo, +vdb, +vdi, and the -m option to
    specify that the administrative features must be ignored.
    
    @keyword options: list of additional Timbl options, excluding -f, -m, +vo,
    +vdb, +vdi    
    
    @keyword log: log Timbl's standard output and error streams to file
    
    @return: list of Timbl output filenames
    """
    if clas_dir:
        makedirs(clas_dir)
        
    if not timbl:
        assert descriptor
        timbl = TimblFile(default_opts=timbl_options_string(descriptor))
    else:
        # ignore descriptor
        assert isinstance(timbl, TimblFile)
        assert "+vo" in timbl.default_opts
        assert "+vdb" in timbl.default_opts
        assert "+vdi" in timbl.default_opts
        assert "-m" in timbl.default_opts
    
    return timbl.train_test_multi(train_inst_fns, test_inst_fns,
                                  out_fns=out_fns, log_fn=log_fn, options=options, log=log,
                                  out_dir=clas_dir)

