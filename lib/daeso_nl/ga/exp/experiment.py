# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by Erwin Marsi and TST-Centrale
#
# This file is part of the DAESO Framework.
#
# The DAESO Framework is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The DAESO Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Top-level functions for running alignment experiments
"""

# TODO:
# - cleaning

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import logging as log
import os
from pickle import dump
import StringIO

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE
from daeso.utils.opsys import makedirs
from daeso.utils.report import header

from daeso_nl.ga.corpusinst import CorpusInst
from daeso_nl.ga.exp.part import create_parts, clean_parts
from daeso_nl.ga.exp.extract import extract, clean_inst
from daeso_nl.ga.exp.sample import sample, clean_samp
from daeso_nl.ga.exp.classify import classify, clean_clas
from daeso_nl.ga.exp.weight import weight, weight_corpus
from daeso_nl.ga.exp.match import match, match_corpus
from daeso_nl.ga.exp.merge import merge, merge_corpus
from daeso_nl.ga.exp.evaluate import evaluate

from tt.outparser import parse_timbl_output
from tt.featgraph import parse_feat_weights, graph_table, print_table


__all__ = [
    "exp",    
    "exp_dev_fast"
    ]


def exp(setting):
    """
    perform alignment experiment
    """
    exp_init(setting) 
    create_parts(setting)
    extract(setting)
    sample(setting)
    classify(setting) 
    weight(setting)
    match(setting)
    merge(setting)
    evaluate(setting)
    exp_exit(setting)
    
    
def exp_init(setting):
    log.info("\n" + header("INIT"))
    log.info("Setting at start:\n" + str(setting) + "\n")
    buf = StringIO.StringIO()
    buf.write("feature description:\n")
    setting.descriptor.pprint(buf)
    log.info(buf.getvalue())


def exp_exit(setting):
    log.info("\n" + header("EXIT"))
    pickle(setting)
    feat_weight_graphs(setting)
    log.info("Setting at end:\n" + str(setting) + "\n")
    
    
def pickle(setting):
    if setting.pickle:
        makedirs(setting.pickle_dir)
        log.info("saving pickled setting {0}".format(setting.pickle_fname))
        pkl_file = open(setting.pickle_fname, "wb")
        dump(setting, pkl_file)
        
        
        
def feat_weight_graphs(setting):
    if setting.feat_weight_graphs:
        feat_names = [feat.name for feat in setting.descriptor]
        
        for log_fname in setting.dev_log_fns + setting.val_log_fns:
            out_fname = os.path.splitext(log_fname)[0] + ".fwg"
            outf = open(out_fname, "w")
            field_names, table = parse_feat_weights(log_fname, feat_names)    
            graph_table(field_names, table, outf)
            print_table(field_names, table, outf)
        

def exp_dev_fast(setting):
    """
    perform a fast alignment experiment on development data
    
    Weighting, matching and merging takes place per test corpus without
    writing intermediary results to a file.
    """
    assert setting.develop and not setting.validate
    
    exp_init(setting)
    
    create_parts(setting)
    
    # It's impossible to do extraction one corpus a time, because in order to
    # classify a test corpus you need instances for all the other training
    # corpora! Moreover, since Timbl classification is file-based, we need to
    # write the corpus instance files to disk. These files can be huge and
    # keeping all of them in memory seems to offer little benefit.
    extract(setting)
    
    sample(setting)
        
    # Timbl writes its output to a file, which then needs to be parsed in
    # order to insert the class predictions and weights into the corpus
    # instances. That means there is no advantage to doing classification
    # one corpus a time.
    classify(setting)
     
    log.info("\n" + header("WEIGHT/MATCH/MERGE STEP"))   
    # reset evaluator
    if setting.evaluate: setting.evaluator.__init__()
        
    scope = zip(setting.dev_inst_fns, 
                setting.dev_clas_fns,
                setting.dev_true_fns)[:setting.n]
    
    for inst_fname, out_fname, true_fname in scope:
        log.info("reading corpus instances {0}".format(inst_fname))
        corpus_inst = CorpusInst()
        corpus_inst.loadtxt(inst_fname, setting.descriptor.dtype)
        
        if setting.weight:
            log.info("reading classifier output {0}".format(out_fname))
            timbl_out = parse_timbl_output(open(out_fname))
            log.info("weighting...")
            weight_corpus(corpus_inst, timbl_out, setting.weight_func)
            
        if setting.match:
            log.info("matching...")
            match_corpus(corpus_inst, setting.matcher)
            
        if setting.merge:
            log.info("reading true corpus {0}".format(true_fname))
            true_corpus = ParallelGraphCorpus(inf=true_fname,
                                              graph_loading=LOAD_NONE)
            log.info("merging...")
            pred_corpus = merge_corpus(corpus_inst, true_corpus,
                                       setting.merger)

        if setting.evaluate:
            name = os.path.basename(true_fname).split("_")[0]
            setting.evaluator.add(true_corpus, pred_corpus, name) 
        
    if setting.evaluate: 
        log.info("evaluting...")
        setting.evaluator.run_eval()
        log.info("saving evaluation {0}".format(setting.dev_eval_fname))
        makedirs(setting.eval_dir)
        setting.evaluator.write(setting.dev_eval_fname)
        
    exp_exit(setting)

        
        