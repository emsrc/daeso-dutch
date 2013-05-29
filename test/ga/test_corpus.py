"""
test corpus aligner
"""

import unittest

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.extractor import select_parsed_graph_pair
from daeso_nl.ga.classifier import TimblClassifier
from daeso_nl.ga.aligner import GraphAligner
from daeso_nl.ga.corpus import CorpusAligner    

from exp.setup import create_setting


class Test_CorpusAligner(unittest.TestCase):

    def test_align(self):
        # create graph aligner
        descriptor = create_setting().descriptor
        classifier = TimblClassifier(descriptor,
                                     "exp/inst/dev001.inst")
        graph_aligner = GraphAligner(
            descriptor=descriptor,
            classifier=classifier)
        
        # create corpus aligner
        corpus_aligner = CorpusAligner(
            graph_aligner=graph_aligner,
            graph_selector=select_parsed_graph_pair)
        
        # align part of corpus
        corpus = ParallelGraphCorpus(inf="exp/true/dev001_true.pgc")[:3]
        corpus_aligner.align(corpus[:3], clear=True)
        #corpus.write(pprint=True)

        self.assertTrue(
            corpus[0].alignments() or
            corpus[1].alignments() or
            corpus[2].alignments())
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()