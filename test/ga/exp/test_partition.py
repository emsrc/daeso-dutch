"""
test partitioning of a collection of parallel graph corpora
"""

import unittest
import random

from daeso_nl.ga.exp.partition import ( greedy_bin, 
                                        create_partition, 
                                        write_partition )

from daeso_nl.utils.globbing import relglob

from setup import create_setting


    
class TestPartitioning(unittest.TestCase):
    
    def test_greedy_bin(self):
        """
        test greedy binning by verifying that none of the resulting bins
        deviates more than 20% from the avarage bin size
        """
        # experiments show that the error of greedy binning is at most 20%
        allowed_error_factor = 0.02
        n_obj = 100
        n_bins = 10
        interval = 1000
        iterations = 100
        verbose = False
        
        for i in range(iterations):
            objects = [ "e%d" % i for i in range(n_obj) ]
            sizes = [ random.randint(0, interval) for i in range(n_obj) ]
            bin_sizes, bins = greedy_bin(objects, sizes, n_bins)
            
            self.assertEqual(len(bin_sizes), n_bins)
            self.assertEqual(len(bins), n_bins)
            self.assertEqual(sum(bin_sizes), sum(sizes))
            
            mean_bin_size = sum(bin_sizes) / float(len(bin_sizes))
            if verbose:
                print "mean size:", mean_bin_size
            
            allowed_error = allowed_error_factor * mean_bin_size
            if verbose:
                print "allowed error:", allowed_error, "\n"
            
            for bin_size, bin in zip(bin_sizes, bins):
                error = abs(bin_size - mean_bin_size)
                if verbose:
                    print "%4d %4d %4d: %s" % (
                        bin_size,
                        error,
                        len(bin), bin)
                self.assertTrue(error < allowed_error)
                
                
    def test_create_partition(self):
        st = create_setting()
        # cannot reuse create_sample_partition because we need pgc_files 
        # for asserting
        pgc_files = relglob(st.corpus_dir, "news/pgc/ma/2006-11/*.pgc")
        self.assertTrue(pgc_files)
        
        corpus_fns, corpus_sizes, dev_parts, val_parts, dev_sizes, val_sizes = \
        create_partition(pgc_files, corpus_dir=st.corpus_dir, 
                         dev_bins=4, val_bins=1)
        
        self.assertEqual(len(dev_parts), 4)
        self.assertEqual(len(val_parts), 1)
        
        dev_fns = set( part_fname for part_list in dev_parts 
                       for part_fname in part_list )
        val_fns = set( part_fname for part_list in val_parts 
                       for part_fname in part_list )
        
        # check if no files were lost
        self.assertEqual( len(dev_fns) + len(val_fns), 
                          len(pgc_files) )
        
        # check for overlap
        self.assertTrue(dev_fns.isdisjoint(val_fns))
        
        write_partition(corpus_fns, corpus_sizes, dev_parts, val_parts,
                        dev_sizes, val_sizes)
        
        
    def test_create_partition_forced(self):
        st = create_setting()
        # cannot reuse create_sample_partition because we need pgc_files 
        # for asserting
        pgc_files = relglob(st.corpus_dir, "news/pgc/ma/2006-11/*.pgc")
        self.assertTrue(pgc_files)
        
        forced_fns = ['news/pgc/ma/2006-11/news-2006-11-aligned-part-02.pgc']
        
        corpus_fns, corpus_sizes, dev_parts, val_parts, dev_sizes, val_sizes = \
        create_partition(pgc_files, corpus_dir=st.corpus_dir, 
                         dev_bins=4, val_bins=1, forced_fns=forced_fns)
        
        write_partition(corpus_fns, corpus_sizes, dev_parts, val_parts,
                        dev_sizes, val_sizes)
        
        self.assertEqual(len(dev_parts), 4)
        self.assertEqual(len(val_parts), 1 + 1)
        
        dev_fns = set( part_fname for part_list in dev_parts 
                       for part_fname in part_list )
        val_fns = set( part_fname for part_list in val_parts 
                       for part_fname in part_list )
        
        # check if no files were lost
        self.assertEqual( len(dev_fns) + len(val_fns), 
                          len(pgc_files) )
        
        # check for overlap
        self.assertTrue(dev_fns.isdisjoint(val_fns))
        
        # check for forced files
        for forced_fname in forced_fns:
            self.assertTrue(forced_fname in val_fns)
        
        

    
if __name__ == '__main__':
    unittest.main()