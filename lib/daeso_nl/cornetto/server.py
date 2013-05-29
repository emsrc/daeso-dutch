"""
computing semantic similarity relations between words using the Cornetto database
"""

# requires Pycornetto, the python interface to the Cornetto database

from cornetto.server import CornetProxy

from daeso_nl.cornetto.cornet import DaesoCornet


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5507
            
            
class DaesoCornetProxy(CornetProxy):    
    """
    A proxy to the DaesoCornet class which exposes the methods for
    calculating Daeso similarity relations through XML-RPC. See CornetProxy
    """          
                
                
    def __init__(self, cdb_lu, cdb_sy, verbose=False, max_depth=None,
                 cornet_class=DaesoCornet):
        CornetProxy.__init__(self, cdb_lu, cdb_sy, verbose=verbose,
                             max_depth=max_depth, cornet_class=cornet_class)
        
        
    def multi_semantic_sim(self, from_spec_list, to_spec_list):
        """
        multi_semantic_sim(FROM_SPEC_LIST, TO_SPEC) --> MATRIX
        
        Calculate semantic similarity scores on four of Daeso similarity
        relations - restates, specifies, generalizes and intersects - for all
        possible combinations of lexical units from the two lists
        
        Parameters:       
        
            FROM_SPEC_LIST list: list of lexical unit specifications
            TO_SPEC_LIST list: list of lexical unit specifications
            
            MATRIX list: matrix in the form of a list of lists, 
                where each cell is a four tuple of scores on the
                Daeso similarity relations: restates, specifies,
                generalizes and intersects
        """
        return self._safe_return(
            self._cornet.multi_semantic_sim(from_spec_list, to_spec_list))
    
    
    def semantic_sim(self, from_spec, to_spec):
        return self._safe_return(
            self._cornet.semantic_sim(from_spec, to_spec))

    
    def clear_cache(self):
        return self._safe_return(
            self._cornet._clear_cache())
        
    
        
        