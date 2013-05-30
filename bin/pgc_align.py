#!/usr/bin/env python
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
align graphs in parallel graph corpus
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'
__version__ = "0.9"


import imp

from daeso.utils.cli import DaesoArgParser
from daeso.utils.opsys import multiglob
from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.setup import set_up_corpus_aligner

parser = DaesoArgParser(description=__doc__, version=__version__)


parser.add_argument(
    "pgc_files",
    nargs="+",
    metavar="FILE",
    help="parallel graph corpus file"
    )

parser.add_argument(
    "-c", "--config",
    metavar="FILE",
    help="configuration file to set up a corpus aligner")  

parser.add_argument(
    "-x", "--clear",
    action="store_true",
    help="remove all existing alignments"
    )

parser.add_argument(
    "-i", "--in-place",
    action="store_true",
    help="modify input file(s)"
    )

args = parser.parse_args()


if args.config:
    config = imp.load_source("config", args.config)
    corpus_aligner = set_up_corpus_aligner(config)
else:
    from daeso_nl.ga.corpus import CorpusAligner
    corpus_aligner = CorpusAligner()
    

for inf in multiglob(args.pgc_files):
    corpus = ParallelGraphCorpus(inf=inf)
    corpus_aligner.align(corpus, clear=args.clear)
    
    if args.in_place:
        corpus.write(outf=inf, pprint=True)
    else:
        corpus.write(pprint=True)