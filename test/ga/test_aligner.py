"""
test core graph alignment
"""

# When testing from within WING IDE, the PATH env var must be extended with
# the path to the Timbl executable project in the Project's environment.


import unittest

from daeso.pgc.corpus import ParallelGraphCorpus

from daeso_nl.ga.classifier import TimblClassifier
from daeso_nl.ga.aligner import GraphAligner

from exp.setup import create_setting

class Test_Aligner(unittest.TestCase):
    
    def test_aligner(self):
        descriptor = create_setting().descriptor
        classifier = TimblClassifier(descriptor,
                                     "exp/inst/dev001.inst")
        aligner = GraphAligner(
            descriptor=descriptor,
            classifier=classifier)

        corpus = ParallelGraphCorpus(inf="exp/true/dev001_true.pgc")
        
        for graph_pair in corpus[:3]:
            graph_inst = aligner.align(graph_pair, clear=True)
        
       
        

if __name__ == '__main__':
    unittest.main()        

