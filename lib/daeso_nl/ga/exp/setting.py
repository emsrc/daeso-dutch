"""
Setting for alignment experiment
"""

import inspect
import logging as log
import os
import tempfile
from os.path import join, basename, splitext

from daeso.pgc.evaluate import AlignEval
from daeso.utils.opsys import glob 

from daeso_nl.ga.descriptor import Descriptor
from daeso_nl.ga.extractor import ( Extractor, select_visible_node,
                                    select_aligned_graph_pair )
from daeso_nl.ga.classifier import timbl_options_string
from daeso_nl.ga.matcher import Matcher
from daeso_nl.ga.merger import Merger

from daeso_nl.ga.exp.weight import entropy_weight

from tt.timblfile import TimblFile

    

class Setting(object):
    """
    A Setting object defines all the parameters for an alignment experiment.
    Different steps in the experimental process are performed by functions,
    all of which read a Setting object. 
    
    
    General
    =======
    
    @kwarg name: name of experiment
    @type: str := ''
    
    @kwarg doc: experiment documentation string
    @type doc: str := ''
    
    @kwarg exp_dir: base dir for experiment; defaults to experiment name                
    @type exp_dir: str := name
    
    @kwarg develop: perform cross-validation experiment on development data
    @type develop: bool := True
    
    @kwarg n: limit to n iterations during cross-validation
    @type n: int := None
    
    @kwarg validate: perform experiment on validation data               
    @type validation: bool := False    
    
    @kwarg log: log progress
    @type log: bool := False    

    
    Parting step
    ============
    
    @kwarg part: perform parting step
    @type part: bool := False
    
    @kwarg corpus_dir: base directory for all corpus; filename paths of the
    original corpus files must be relative to corpus_dir
    @type corpus_dir: str := value of environment var DAESO_CORPUS

    @kwarg dev_parts: a dictionary where each key specifies the filename for
    the development part and each value a sequence of parallel graph corpora
    filenames merged into the development part; required for parting step    
    @type dev_parts: dict := {}
    
    @kwarg val_parts: a dictionary where each key specifies the filename for
    the validation part and each value a sequence of parallel graph corpora
    filenames merged into the validation part; required for parting step    
    @type val_parts: dict := {}
    
    @kwarg part_dir: destination directory for parts, which will be created if
    it does not exist; defaults to exp_dir + part_subdir
    @type part_dir: str := 'part'
    
    @kwarg part_subdir: subdir of exp_dir for part files
    @type part_subdir: str := 'part'
    
    @kwarg dev_part_glob: glob pattern for development part files        
    @type dev_part_glob: str := 'dev*.pgc'
    
    @kwarg val_part_glob: glob pattern for validation part files        
    @type val_part_glob: str := 'val*.pgc'
        
    @kwarg part_max_size: limits the maximal number of corpus files per part,
    which is sometimes useful for try-out experiments with only a small number
    of corpus files.
    @type part_max_size: int := None
    
    Dynamically derived properties: 
        - dev_part_fns: list of development part files; 
          glob on part_dir + dev_part_glob     
        - val_part_fns: list of validation part files; 
          glob on part_dir + val_part_glob       
    
    
    Extraction step
    ===============

    @kwarg extract: perform extraction step
    @type extract: bool := True
        
    @kwarg extractor: object responsible for feature extraction
    @type extrcator: daeso_nl.ga.extractor.Extractor instance
    
    @kwarg graph_selector: function for selecting graph pairs        
    @type graph_selector: function := daeso_nl.ga.extractor.select_aligned_graph_pair
        
    @kwarg node_selector: function for selecting nodes          
    @type node_selector: function := daeso_nl.ga.extractor.select_visible_node
    
    @kwarg features: features as tuple of Feat instances               
    @type features: tuple := ()
    
    @kwarg descriptor: feature discription
    @type descriptor: Descriptor := Descriptor(self.features)
    
    @kwarg true_subdir: subdir of exp_dir for true corpora
    @type true_subdir: str = 'true'
    
    @kwarg true_dir: destination dir for true corpora
    @type true_dir: str := exp_dir + true_subdir
    
    @kwarg dev_true_glob: glob pattern for true development corpora
    @type true_pred_glob: str :='dev*_true.pgc'
    
    @kwarg val_true_glob: glob pattern for true validation corpora
    @type val_true_glob: str :='val*_true.pgc'    
    
    @kwarg inst_subdir: destination subdir for instance files
    @type inst_subdir: str := 'inst'
        
    @kwarg inst_dir: destination dir for instance files
    @type inst_dir: str := exp_dir + inst_subdir
    
    @kwarg dev_inst_glob: glob pattern for development instance files
    @type dev_inst_glob: str := 'dev*.inst'
    
    @kwarg val_inst_glob: glob pattern for validation instance files
    @type val_inst_glob: str := 'val*.inst'
    
    @kwarg binary: save corpus instances in binary rather than text format    
    @type binary: bool := True
    
    Dynamically derived properties:
        - dev_true_fns: development alignment truei files;
          glob on true_dir + dev_true_glob 
        - val_true_fns: validation alignment true files;
          glob on true_dir + val_true_glob 
        - dev_inst_fns: list of development instance files;
          derived from basenames of development part_fns and inst_dir
        - val_inst_fns: list of validation instance files;
          derived from basenames of validation part_fns and inst_dir
    
    
    Sampling step
    =============
        
    @kwarg sample:  perform sampling step
    @type sample: bool := True
    
    @kwarg class_fracts: a dict with class labels (strings) as keys and
    fractions (floats between 0.0. and 1.0) as values
    @type class_fracts: dict := {}
    
    @kwarg samp_subdir: subdir of exp_dir for sampling output files
    @type samp_subdir: str := 'samp'
    
    @kwarg samp_dir: destination dir for sampling output files
    @type samp_dir: str := exp_dir + samp_subdir
    
    Dynamically derived properties: 
        - dev_samp_fns: list of development sampling output files;
          defaults to glob on samp_dir +  dev_inst_glob
        - val_samp_fns: list of validation sampling output files;
          defaults to glob on samp_dir +  val_inst_glob
    
    
    Classification step
    ===================
    
    @kwarg classify: perform classification step
    @type classify: bool := True
    
    @kwarg train_sample: train on sampled instances instead of orginals
    @type train_sample: bool := False
    
    @kwarg classifier: normally self.classifier will be None, and a TimblFile
    instance with appropriate settings will be created on the fly; if you want
    to set a classifier explicitly, notice that it must at least set the
    verbosity options +vo, +vdb, +vdi, the -f option to specify the instances
    file, and the -m options to specify that the administrative features must
    be ignored. classify: True perform classification step during experiment
    @type classifier: TimblFile := Noneclas_subdir
    
    @kwarg timbl_log: log Timbl's standard output and error streams to file
    @type timbl_log: bool := True
    
    @keyword feat_weight_graphs: produce feature weight graphs:
    requires setting of timbl_log
    
    @kwarg timbl_opts: list of additional Timbl options, excluding -f, -m, +vo,
    +vdb, +vdi             
    @type timbl_opts: str := ""

    @kwarg clas_subdir: default name of subdirectory of exp_dir for creating
    classifier output files
    @type clas_subdir: str := 'clas'
    
    @kwarg clas_dir: directory for creating classifier output files; ignored
    if out_fns is given
    @type clas_dir: str := exp_dir + clas_subdir
    
    @kwarg dev_clas_glob: glob pattern for development classification output files        
    @type dev_clas_glob: str := 'dev*.out'
    
    @kwarg val_clas_glob: glob pattern for validation classification output files        
    @type val_clas_glob: str := 'val*.out'
    
    @kwarg dev_log_glob: glob pattern for development classification log files        
    @type dev_log_glob: str := 'dev*.log'
    
    @kwarg val_log_glob: glob pattern for validation classification log files        
    @type val_clog_glob: str := 'val*.log'
    
    Dynamically derived properties: 
        - dev_clas_fns: list of development classification output files;
          defaults to glob on clas_dir +  dev_clas_glob
        - val_clas_fns: list of validation classification output files;
          defaults to glob on clas_dir +  val_clas_glob
        - dev_log_fns: list of development classification log files;
          defaults to glob on clas_dir +  dev_log_glob
        - val_log_fns: list of validation classification log files;
          defaults to glob on clas_dir +  val_log_glob
    
    
    Weighting step
    ==============
    
    @kwarg weight: perform weighting step                 
    @type weight: bool := True
    
    @kwarg weight_func: weighting function
    @type weight_func: function := daeso_nl.ga.exp.weight.entropy_weight
    
    
    Matching step
    =============
    
    @kwarg match: perform matching step                 
    @type match: bool := True
    
    @kwarg matcher: object responsible for matching                
    @type matcher: daeso_nl.ga.matcher.Matcher instance
    
    
    Merging step
    ============
    
    @kwarg merge: perform merging step
    @type merge: bool := True
    
    @kwarg merger: object responsible for merging                 
    @type merger: daeso_nl.ga.merger.Merger instance
    
    @kwarg pred_subdir: subdir of exp_dir for predicted corpora
    @type pred_subdir: str = 'pred'
    
    @kwarg pred_dir: destination dir for predicted corpora
    @type pred_dir: str := exp_dir + pred_subdir
    
    @kwarg dev_pred_glob: glob pattern for predicted development corpora
    @type dev_pred_glob: str :='dev*_pred.pgc'
    
    @kwarg val_pred_glob: glob pattern for predicted validation corpora
    @type val_pred_glob: str :='val*_pred.pgc'

    Dynamically derived properties:
        - dev_pred_fns: development alignment prediction files;
          glob on pred_dir + dev_pred_glob 
        - val_pred_fns: validation alignment prediction files;
          glob on pred_dir + val_pred_glob 
        
        
    Evaluation step
    ===============
        
    @kwarg evaluate: perform evaluation step
    @type evaluate: bool := True
    
    @kwarg evaluator: object responsible for evaluation 
    @type evaluator: AlignEval instance with default alignment relations
        
    @kwarg eval_subdir: subdir of exp_dir for evaluation reports
    @type eval_subdir: str := 'eval'

    @kwarg eval_dir: destination dir for evaluation reports
    @type eval_dir: str := exp_dir + eval_subdir

    @kwarg dev_eval_basename: file basename (i.e. without dirs) for evaluation
    report on development data
    @type dev_eval_basename: str := 'dev_eval.txt'
    
    @kwarg val_eval_basename: file basename (i.e. without dirs) for evaluation
    report on validation data
    @type val_eval_basename: str := 'val_eval.txt'

    @kwarg dev_eval_fname: filename for evaluation report on development data
    @type dev_eval_fname: str := eval_dir + dev_eval_basename
    
    @kwarg val_eval_fname: filename for evaluation report on validation data
    @type val_eval_fname: str := eval_dir + val_eval_basename
    
    
    Pickling step
    =============
    
    @kwarg pickle: perform pickling step
    @type pickle: bool := False
    
    @kwarg pickle_subdir: subdir of exp_dir for pickle files
    @type pickle_subdir: str := 'pickle'

    @kwarg pickle_dir: destination dir for pickle files;
    @type pickle_dir: str := exp_dir + pickle_subdir
    
    @kwarg pickle_basename: file basename (i.e. without dirs) for pickle
    @type pickle_basename := 'pickle.pkl'
    
    @kwarg pickle_fname: pickle filename
    @type pickle_fname: str := pickle_dir + pickle_basename
    
    """
    
    def __init__(self, **kwargs):
        # set the defaut values
        self.init_info()
        self.init_procs()
        self.init_dirs()
        self.init_files()
        
        # overrule default values according to keyword arguments
        for attr, val in kwargs.items():
            setattr(self, attr, val)
            
        if self.log:
            log.basicConfig(level=log.INFO)
        
    def __str__(self):
        lines = []
        
        for attr_str in dir(self):
            if not attr_str.startswith("_"):
                attr = getattr(self, attr_str)
                # anything except methods of Setting class
                if not inspect.ismethod(attr):
                    line = "{0:24}{1!r}".format(attr_str + ": ", attr)
                    lines.append(line)
                
        return "\n".join(lines)
    
    def init_info(self):
        self.name = ""
        self.doc = ""
        self.log = False
    
    def init_procs(self):
        self.develop = True
        self.validate = False
        
        # parting
        self.part = False
        self.dev_parts = {}
        self.val_parts = {}
        self.part_max_size = None
        
        # feature description
        self.features = ()
        
        # feature extraction
        self.extract = True
        self.graph_selector = select_aligned_graph_pair
        self.node_selector = select_visible_node
        self.binary = False
        
        # sampling
        self.sample = False
        self.class_fracts = {}
        #self.sampler =  None

        # classification
        self.classify = True
        # Normally self.classifier will be None, and a TimblFile instance with
        # appropriate settings will be created on the fly. If you want to set
        # a classifier explicitly, notice that it must at least set the
        # verbosity options +vo, +vdb, +vdi, the -f option to specify the
        # instances file, and the -m options to specify that the
        # administrative features must be ignored.
        self.classifier = None
        self.timbl_opts = ""
        self.timbl_log = True
        self.feat_weight_graphs = False
        self.train_sample = False 
        
        # weighting
        self.weight = True
        self.weight_func = entropy_weight
        
        # matching
        self.match = True
        self.matcher = Matcher()
        
        # merging
        self.merge = True
        self.merger = Merger()
        
        # evaluation
        self.evaluate = True
        self.evaluator = AlignEval()
        # AlignEval instances for develop and validation exps,
        # which are saved in a pickled seting 
        self.dev_eval = None
        self.val_eval = None
        
        # iteraration limit during cross-validation 
        self.n = None
        
        # store settings including evaluation as a pickle
        self.pickle = False
        
    # dynamic attributes for processors that depend on the setting of other
    # attributes

    @property
    def descriptor(self):
        try:
            return self._descriptor
        except AttributeError:
            self._descriptor = Descriptor(self.features)
            return self._descriptor
    
    @descriptor.setter
    def descriptor(self, descriptor):
        # when setting a descriptor, modify features and extractor accordingly!
        assert isinstance(descriptor, Descriptor)
        self._descriptor = descriptor
        
    @descriptor.deleter
    def descriptor(self):
        del self._descriptor
        
        
    @property
    def extractor(self):
        try:
            return self._extractor
        except AttributeError:
            self._extractor = Extractor(self.descriptor, self.node_selector)
            return self._extractor
    
    @extractor.setter
    def extractor(self, extractor):
        # When setting an extractor, modify features and descriptor accordingly
        assert isinstance(extractor, Extractor)
        self._extractor = extractor
        
    @extractor.deleter
    def extractor(self):
        del self._extractor
    

    #-------------------------------------------------------------------------
    # directories    
    #-------------------------------------------------------------------------
        
    def init_dirs(self):
        # base dir for orginal corpus files
        self.corpus_dir= os.getenv("DAESO_CORPUS")
        
        # parallel graph corpora constituting the parts for training and testing  
        self.part_subdir = "part"
        
        # parallel graph corpora with true alignments
        self.true_subdir = "true"
        
        # instances
        self.inst_subdir = "inst"
        
        # instance samples
        self.samp_subdir = "samp"
        
        # classifier output
        self.clas_subdir = "clas"
        
        # parallel graph corpora with predicted alignments
        self.pred_subdir = "pred"
        
        # evaluation output
        self.eval_subdir = "eval"
        
        # pickle output
        self.pickle_subdir = "pickle"
        
    # The properties below will provide a default value derived from
    # self.exp_dir and a subdir, unless a specific directory was set using the
    # setter. Deletion of the property using the deleter causes a return to
    # the default value. This mechanism allows relocating individual
    # directories without affecting the other ones.
    
    @property
    def exp_dir(self):
        try:
            return self._exp_dir
        except AttributeError:
            return self.name
    
    @exp_dir.setter
    def exp_dir(self, path):
        self._exp_dir = path
        
    @exp_dir.deleter
    def exp_dir(self):
        del self._exp_dir

        
    @property
    def part_dir(self):
        try:
            return self._part_dir
        except AttributeError:
            return join(self.exp_dir, self.part_subdir)
    
    @part_dir.setter
    def part_dir(self, path):
        self._part_dir = path
        
    @part_dir.deleter
    def part_dir(self):
        del self._part_dir
    
    
    @property
    def true_dir(self):
        try:
            return self._true_dir
        except AttributeError:
            return join(self.exp_dir, self.true_subdir)
    
    @true_dir.setter
    def true_dir(self, path):
        self._true_dir = path
        
    @true_dir.deleter
    def true_dir(self):
        del self._true_dir

    
    @property
    def inst_dir(self):
        try:
            return self._inst_dir
        except AttributeError:
            return join(self.exp_dir, self.inst_subdir)
    
    @inst_dir.setter
    def inst_dir(self, path):
        self._inst_dir = path
        
    @inst_dir.deleter
    def inst_dir(self):
        del self._inst_dir

    
    @property
    def samp_dir(self):
        try:
            return self._samp_dir
        except AttributeError:
            return join(self.exp_dir, self.samp_subdir)
    
    @samp_dir.setter
    def samp_dir(self, path):
        self._samp_dir = path
        
    @samp_dir.deleter
    def samp_dir(self):
        del self._samp_dir

    
    @property
    def clas_dir(self):
        try:
            return self._clas_dir
        except AttributeError:
            return join(self.exp_dir, self.clas_subdir)
    
    @clas_dir.setter
    def clas_dir(self, path):
        self._clas_dir = path
        
    @clas_dir.deleter
    def clas_dir(self):
        del self._clas_dir
    

    @property
    def pred_dir(self):
        try:
            return self._pred_dir
        except AttributeError:
            return join(self.exp_dir, self.pred_subdir)
    
    @pred_dir.setter
    def pred_dir(self, path):
        self._pred_dir = path
        
    @pred_dir.deleter
    def pred_dir(self):
        del self._pred_dir
    
        
    @property
    def eval_dir(self):
        try:
            return self._eval_dir
        except AttributeError:
            return join(self.exp_dir, self.eval_subdir)
    
    @eval_dir.setter
    def eval_dir(self, path):
        self._eval_dir = path
        
    @eval_dir.deleter
    def eval_dir(self):
        del self._eval_dir
    
        
    @property
    def pickle_dir(self):
        try:
            return self._pickle_dir
        except AttributeError:
            return join(self.exp_dir, self.pickle_subdir)
    
    @pickle_dir.setter
    def pickle_dir(self, path):
        self._pickle_dir = path
        
    @pickle_dir.deleter
    def pickle_dir(self):
        del self._pickle_dir
    
    #-------------------------------------------------------------------------
    # files    
    #-------------------------------------------------------------------------
    
    def init_files(self):
        # development
        
        # source parallel graph corpora for development
        self.dev_part_glob = "dev*.pgc"
        
        # development instances
        self.dev_inst_glob = "dev*.inst"
        
        # development parallel graph corpora with true alignments
        self.dev_true_glob= "dev*_true.pgc"
        
        # development parallel graph corpora with predicted alignments
        self.dev_pred_glob = "dev*_pred.pgc"
        
        # development classifier output 
        self.dev_clas_glob = "dev*.out"
        
        # development classifier log
        self.dev_log_glob = "dev*.log"
        
        # validation
        
        # source parallel graph corpora for validation
        self.val_part_glob = "val*.pgc"
        
        # validation instances
        self.val_inst_glob = "val*.inst"
        
        # validation parallel graph corpora with true alignments
        self.val_true_glob= "val*_true.pgc"
        
        # validation parallel graph corpora with predicted alignments
        self.val_pred_glob = "val*_pred.pgc"
        
        # validation classifier output 
        self.val_clas_glob = "val*.out"
        
        # validation classifier log 
        self.val_log_glob = "val*.log"
        
        
    # development globs

    @property    
    def dev_part_fns(self): 
        return glob(join(self.part_dir, self.dev_part_glob))
    
    @property    
    def dev_inst_fns(self): 
        return glob(join(self.inst_dir, self.dev_inst_glob))
    
    @property    
    def dev_samp_fns(self): 
        return glob(join(self.samp_dir, self.dev_inst_glob))
    
    @property    
    def dev_true_fns(self): 
        return glob(join(self.true_dir, self.dev_true_glob))
    
    @property    
    def dev_pred_fns(self): 
        return glob(join(self.pred_dir, self.dev_pred_glob))
    
    @property    
    def dev_clas_fns(self): 
        return glob(join(self.clas_dir, self.dev_clas_glob))
    
    @property    
    def dev_log_fns(self): 
        return glob(join(self.clas_dir, self.dev_log_glob))
    
    # validation globs
    
    @property    
    def val_part_fns(self): 
        return glob(join(self.part_dir, self.val_part_glob))
    
    @property    
    def val_inst_fns(self): 
        return glob(join(self.inst_dir, self.val_inst_glob))
    
    @property    
    def val_samp_fns(self): 
        return glob(join(self.samp_dir, self.val_inst_glob))
    
    @property    
    def val_true_fns(self): 
        return glob(join(self.true_dir, self.val_true_glob))
    
    @property    
    def val_pred_fns(self): 
        return glob(join(self.pred_dir, self.val_pred_glob))
    
    @property    
    def val_clas_fns(self): 
        return glob(join(self.clas_dir, self.val_clas_glob))
    
    @property    
    def val_log_fns(self): 
        return glob(join(self.clas_dir, self.val_log_glob))
    
    # evaluation reports
    
    @property
    def dev_eval_basename(self):
        """
        basename for develop evaluation file
        """
        try:
            return self._dev_eval_basename
        except AttributeError:
            return "dev_eval.txt"
    
    @dev_eval_basename.setter
    def dev_eval_basename(self, basename):
        self._dev_eval_basename = basename
        
    @dev_eval_basename.deleter
    def dev_eval_basename(self, basename):
        del self._dev_eval_basename
        
    @property    
    def dev_eval_fname(self): 
        """
        filename for develop evaluation report
        """
        return join(self.eval_dir, self.dev_eval_basename)
        
    
    @property
    def val_eval_basename(self):
        """
        basename for validation evaluation file
        """
        try:
            return self._val_eval_basename
        except AttributeError:
            return "val_eval.txt"
    
    @val_eval_basename.setter
    def val_eval_basename(self, basename):
        self._val_eval_basename = basename
        
    @val_eval_basename.deleter
    def val_eval_basename(self, basename):
        del self._val_eval_basename
        
    @property    
    def val_eval_fname(self): 
        """
        filename for validation evaluation report
        """
        return join(self.eval_dir, self.val_eval_basename)
    
    # pickle
    
    @property
    def pickle_basename(self):
        """
        basename for pickle file
        """
        try:
            return self._pickle_basename
        except AttributeError:
            return (self.name or "pickle") + ".pkl"
    
    @pickle_basename.setter
    def pickle_basename(self, basename):
        self._pickle_basename = basename
        
    @pickle_basename.deleter
    def pickle_basename(self, basename):
        del self._pickle_basename
        
    @property
    def pickle_fname(self):
        """
        filename for pickle
        """
        return join(self.pickle_dir, self.pickle_basename)
    
    # creating new filenames
    
    def make_inst_fname(self, part_fname):
        """
        Derive file path for corpus instances from that of the part corpus
        """
        base_fname = splitext(basename(part_fname))[0]
        return join(self.inst_dir, base_fname + ".inst")
        
    def make_inst_fns(self, part_fns):
        """
        Derive file paths for new corpus instances from those of the corpus
        parts
        """
        return [ self.make_inst_fname(part_fname)
                 for part_fname in part_fns]
    
        
    def make_samp_fname(self, inst_fname):
        """
        Derive file path for sampled instances from that of the orginal
        instances
        """
        base_fname = splitext(basename(inst_fname))[0]
        return join(self.samp_dir, base_fname + ".inst")
        
    def make_samp_fns(self, inst_fns):
        """
        Derive file paths for new sampled instances from those of the original
        instances 
        """
        return [ self.make_samp_fname(inst_fname)
                 for inst_fname in inst_fns]
    
    
    def make_true_fname(self, part_fname):
        """
        Derive file path for the true corpus from that of the part corpus
        """
        base_fname, ext = splitext(basename(part_fname))
        return join(self.true_dir, base_fname + "_true" + ext)
        
    def make_true_fns(self, part_fns):
        """
        Derive file paths for new true corpora from those of the corpus parts
        """
        return [ self.make_true_fname(part_fname)
                 for part_fname in part_fns]
    

    def make_out_fname(self, inst_fname):
        """
        Derive file path for classifier output from that of the corpus
        instances
        """
        base_fname = splitext(basename(inst_fname))[0]
        return join(self.clas_dir, base_fname + ".out")
        
    def make_out_fns(self, inst_fns):
        """
        Derive file paths for new classifier output from those of the corpus
        instances
        """
        return [ self.make_out_fname(inst_fname)
                 for inst_fname in inst_fns]
    

    def make_log_fname(self, inst_fname):
        """
        Derive file path for classifier log from that of the corpus
        instances
        """
        base_fname = splitext(basename(inst_fname))[0]
        return join(self.clas_dir, base_fname + ".log")
        
    def make_log_fns(self, inst_fns):
        """
        Derive file paths for classifier log from those of the corpus
        instances
        """
        return [ self.make_log_fname(inst_fname)
                 for inst_fname in inst_fns]
    
    
    def make_pred_fname(self, true_fname):
        """
        Derive file path for a new predicted corpus from that of the true
        corpus
        """
        assert "_true" in true_fname 
        return join(self.pred_dir,
                    basename(true_fname).replace("_true", "_pred"))    
    
    def make_pred_fns(self, true_fns):
        """
        Derive file paths for new predicted corpora from those of the true
        corpora
        """
        return [ self.make_pred_fname(true_fname)
                 for true_fname in true_fns ]
    
    # utilities
    
    def make_tmp_dir(self):
        """
        return a new temporary directory
        """
        return tempfile.mkdtemp()
    

