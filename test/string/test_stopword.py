from daeso_nl.string.stopword import remove_stopwords
import unittest


class TestTfIdf(unittest.TestCase):
    
    def test_remove_stopwords(self):
        tokens = "Ik ben een zin , met weinig pretenties .".split()
        self.assertEqual(remove_stopwords(tokens),
                         "Ik zin , weinig pretenties .".split())
    
    def test_remove_stopwords_ignore_case(self):
        tokens = "Ik ben een zin , met weinig pretenties .".split()
        self.assertEqual(remove_stopwords(tokens, ignore_case=True),
                         "zin , weinig pretenties .".split())
    
    def test_remove_stopwords_punc(self):
        tokens = "Ik ben een zin , met weinig pretenties .".split()
        self.assertEqual(remove_stopwords(tokens, remove_punc=True),
                         "Ik zin weinig pretenties".split())
        
    def test_remove_stopwords_case_punc(self):
        tokens = "Ik ben een zin , met weinig pretenties .".split()
        self.assertEqual(remove_stopwords(tokens, ignore_case=True, remove_punc=True),
                         "zin weinig pretenties".split())


if __name__ == '__main__':
    unittest.main()