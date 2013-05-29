#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Partition a collection of parallel graph corpora 

A collection of parallel graph corpora is divided into a development and a
validation part. Both parts are further partitioned in a number of parts of
approximately equal size to be used in cross-validation.

Greedy binning is used to divide the corpora of different sizes over bins of
approximately equal size, where size is measured in terms of the number of
aliged node pairs. Although this is likely to correlate well with the actual
number of node pair instances produced during feature extraction, there may be
significant deviations because of graph and/or node selection (e.g. only
terminal node selection). Randomization is inherent in the greedy binning. 

One of the limitations of the current implementation is that individual
corpora are treated as atomic. This means that if you have only one corpus,
you will first have to split it into subcorpora first.

Outputs a partition map in the form of Python source code with dicts
specifying the corpus files per part.
"""

# keep this doc string in sync with that of ga/partition.py

__author__ = 'Erwin Marsi <e.marsi@gmail.com>'

__version__ = "0.1"


from os import getenv
from sys import stderr

from daeso.utils.cli import DaesoArgParser

from daeso_nl.ga.exp.partition import create_partition, write_partition
from daeso_nl.utils.globbing import relglob


corpus_dir = getenv("DAESO_CORPUS", "")

if not corpus_dir:
    stderr.write("Warning: environment variable DAESO_CORPUS not found!" )


def expand_globs(corpus_dir, globs):
    files = []

    for pattern in globs:
        files.extend(relglob(corpus_dir, pattern))

    return files


parser = DaesoArgParser(description=__doc__, version=__version__)


parser.add_argument(
    "pgc_glob", 
    nargs="+",
    help=( "glob (i.e. filename pattern) for parallel graph corpora, "
           "interpreted relative to the corpus base directory "
           "(cf. --corpus_dir)"))

parser.add_argument(
    "-c", "--corpus-dir", 
    default=corpus_dir,
    help="pgc filenames are interpreted relative to this base directory "
    "(default is '" + corpus_dir + "')")

parser.add_argument(
    "-d", "--dev-bins", 
    type=int,
    default=10,
    help="number of bins used for development data (default is 10)")

parser.add_argument(
    "-f", "--force",
    nargs="*",
    default=[],
    metavar="FILE",
    help="force parallel graph corpus file into extra validation bin")
    
parser.add_argument(
    "-o", "--val-bins", 
    type=int,
    default=2,
    help="number of bins used for validation data (default is 2)")

args = parser.parse_args()


pgc_fns = expand_globs(args.corpus_dir, args.pgc_glob)

partition = create_partition(pgc_fns, 
                             corpus_dir=args.corpus_dir,
                             dev_bins=args.dev_bins,
                             val_bins=args.val_bins,
                             forced_fns=args.force)

write_partition(*partition)



