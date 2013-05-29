"""
updating instances
"""

from daeso_nl.ga.corpusinst import CorpusInst    
    

def update_feats(features,
                 org_inst_fns,
                 org_descriptor,
                 update_inst_fns,
                 update_descriptor):
    """
    A quick hack to facilitate second stage classification. Updates the values
    of specified features in original corpus instances with those from the
    update corpus instances. Modifies orginal files!
    
    @param features: tuple of Feat instances, which provides the names of the
    features to update
    
    @param org_inst_fns: list of orginal corpus instance filenames
    
    @param org_descriptor: feature description for original instances
    
    @param update_inst_fns: list of corpus instance filenames containing the
    updated features
    
    @param update_descriptor: feature description for update instances
    """
    assert len(org_inst_fns) == len(update_inst_fns)
    
    for org_fn, up_fn in zip(org_inst_fns, update_inst_fns):
        print "Updating %s with %s" % (org_fn, up_fn)
        org_corpus_inst = CorpusInst()
        org_corpus_inst.loadtxt(org_fn, org_descriptor.dtype)
        up_corpus_inst = CorpusInst()
        up_corpus_inst.loadtxt(up_fn, update_descriptor.dtype)
        assert len(org_corpus_inst) == len(up_corpus_inst)
        
        for org_inst, up_inst in zip(org_corpus_inst, up_corpus_inst):
            for feat in features:
                org_inst[feat.name] = up_inst[feat.name]
        
        org_corpus_inst.savetxt(org_fn)
        
        