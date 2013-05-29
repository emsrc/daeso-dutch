"""
computing semantic similarity relations between words using the Cornetto database
"""

# requires Pycornetto, the python interface to the Cornetto database

# TODO:
# - revise doc
# - logging

from cornetto.simcornet import SimCornet

# separator for joining lemma:cat and node information 
SEPERATOR = "|S|"


class DaesoCornet(SimCornet):
    
    def __init__(self, cdb_lu=None, cdb_syn=None, 
                 output_format=SimCornet._default_output_format,
                 max_depth=SimCornet._default_max_depth):
        
        SimCornet.__init__(self, cdb_lu, cdb_syn, output_format, max_depth)
        self._init_cache()
        
        
    def multi_semantic_sim(self, from_spec_list, to_spec_list):
        """
        Calculate semantic similarity scores on four of Daeso similarity
        relations - restates, specifies, generalizes and intersects - for all
        possible combinations of lexical units from the two lists. Return a
        matrix with len(from_spec_list) rows and len(to_spec_list) columns
        which stores the similarity measures, i.e. tuples of scores on each of
        the four semantic relations. Based on Lin's similarity measure.
        """
        self._clear_cache()
        cornet_sim = {}
        to_spec_list = [spec.split(SEPERATOR) for spec in to_spec_list]
        
        for from_spec in from_spec_list:
            from_spec, from_node = from_spec.split(SEPERATOR)
            
            for to_spec, to_node in to_spec_list:
                # XMLRPC requires dict keys to be strings, 
                # so we cannot use a tuple or Pair instance here
                nodes = from_node + "," + to_node
                cornet_sim[nodes] = self.semantic_sim(from_spec, to_spec)
            
        return cornet_sim
    
    
    def semantic_sim(self, from_spec, to_spec):
        # Uses Lin's similarity measure with variants for specifies and
        # generalizes.
        
        restates = specifies = generalizes = intersects = 0.0
        
        # We assume that the lexical unit specifications (from_lus/to_lus)
        # *always* contain both a lemma and a pos. The two loops below thus
        # iterate over their possible senses.
        
        # As we don't know the correct sense, we maximize scores over all
        # sense, i.e. we pick the maximum score on
        # restates/specifies/generalizes/intersects for any two senses of the
        # two specifications.
        
        for from_lu in self._get_lex_units_raw(from_spec):
            from_hyp = self._transitive_closure_lu(from_lu, "HAS_HYPERONYM")
            # IC is calculated with smoothing so it never returns None
            from_ic = self._IC(from_lu, subcount=True, smooth=True)
            
            # Note that the expensive calls below are cached, and therefore
            # not recalculated on each iteration
            for to_lu in self._get_lex_units_raw(to_spec):
                to_hyp = self._transitive_closure_lu(to_lu, "HAS_HYPERONYM")
                to_ic = self._IC(to_lu, subcount=True, smooth=True)
                
                # *** restates ***
                if from_lu == to_lu:
                    # If the two senses are identical, then its is most
                    # probably a case of "equals" (i.e. same word) or
                    # "restates" (i.e. same lemma/root). As we cannot access
                    # the word here, only the lemma (root), we pretend it is a
                    # "restates". There is no reason to abort futher search
                    # yet, because we don't know if the senses are correct.
                    restates = 1.0
                elif self._graph.has_edge(from_lu, to_lu):
                    for edge in self._graph[from_lu][to_lu].values():
                        rel_name = self._get_rel_name(edge)
                        if  rel_name == "SYNONYM":
                            restates = 1.0
                            break
                        elif rel_name == "NEAR_SYNONYM":
                            # completely arbitrary score...
                            restates = max(restates, 0.5)
            
                # *** specifies ***
                if to_lu in from_hyp:
                    # thus to_lu is LCS
                    lin_sim = (2 * to_ic) / float(from_ic  + to_ic)
                    specifies = max(specifies, lin_sim)
                    
                # *** generalizes ***
                if from_lu in to_hyp:
                    # thus from_lu is LCS
                    lin_sim = (2 * from_ic) / float(from_ic + to_ic)
                    generalizes = max(generalizes, lin_sim) 
                    
                # *** intersects *** 
                for lcs in self._least_common_subsumers_hyp(from_hyp, to_hyp):
                    lcs_ic = self._IC(lcs, subcount=True, smooth=True)
                    lin_sim = (2 * lcs_ic) / float(from_ic + to_ic)
                    intersects = max(intersects, lin_sim)
                
                # some quick & dirty data mining showed XPOS_NEAR_SYNONYM to
                # be the only relevant relation, apart from SYNONYM and
                # HAS_HYPERONYM
                if self._graph.has_edge(from_lu, to_lu):
                    for edge in self._graph[from_lu][to_lu].values():
                        if self._rel_has_name(edge, "XPOS_NEAR_SYNONYM"):
                            # completely arbitrary score...
                            intersects = max(intersects, 1.0)
                            break

        return (restates, specifies, generalizes, intersects)
            
    
    def _init_cache(self):
        self._get_lex_units_cache = {}
        self._trans_closure_cache = {}
        self._IC_cache = {}
        
        
    def _clear_cache(self):
        self._get_lex_units_cache.clear()
        self._trans_closure_cache.clear()
        self._IC_cache.clear()
        
        
    def _get_lex_units_raw(self, spec):
        # Cached version which assumes that format (e.g. "raw")
        # remains the same over one cached session
        return self._get_lex_units_cache.setdefault(
            spec,
            SimCornet.get_lex_units(self, spec, format="raw"))
            
        
    def _transitive_closure_lu(self, lu, rel_name):
        # Transitive closure for a single lu raher than a list.
        # Cached version which assumes that rel_name (e.g. "HAS_HYPERONYM")
        # remains the same over one cached session
        return self._trans_closure_cache.setdefault(
            lu, 
            SimCornet._transitive_closure(self, [lu], rel_name))
    
    
    def _IC(self, lu, subcount=False, smooth=False, cat_totals=False, base=2):
        # Cached version which assumes that keyword args remain the same over
        # one cached session
        return self._IC_cache.setdefault(
            lu,
            SimCornet._IC(self, lu, subcount, smooth, cat_totals, base))
    
    
    def _least_common_subsumers_hyp(self, from_hyp, to_hyp): 
        # calculate lcs from two sets of hyperonyms
        acs = dict()

        for lu, dist in from_hyp.items():
            try:
                sum_of_dist = dist + to_hyp[lu]
            except KeyError:
                continue
            
            acs.setdefault(sum_of_dist, []).append(lu)
            
        if acs:
            minimum = min(acs.keys())
            return acs[minimum]
        else:
            return []
            
   
# Debugging code 

# Parsing cdb takes a long time. Therefore debugging is much faster if we
# parse just once, like this:
#
# >>> import daeso_nl.cornetto.cornet as cornet
# >>> cornet._parse()
#    
# While debugging we inject the tables and graph in a Cornet instance:
# 
# >>> reload(cornet); c = cornet._get_cornet_instance()
#

if False:
    from cornetto.parse import parse_cdb_with_counts
    
    db_dir = "/Users/erwin/Projects/Daeso/trunk/software/intern/pycornetto/db/"
    
    def _parse(cdb_lu=db_dir + "cdb_lu_minimal_subcounts.xml", 
               cdb_syn=db_dir + "cdb_syn_minimal.xml"):
        global form2lu, c_lu_id2lu, c_sy_id2synset, graph, cat2counts
        form2lu, c_lu_id2lu, c_sy_id2synset, graph, cat2counts = parse_cdb_with_counts(cdb_lu, cdb_syn, verbose=True)
        
    
    def _get_cornet_instance():
        c = DaesoCornet()
        c._form2lu = form2lu
        c._c_lu_id2lu = c_lu_id2lu
        c._c_sy_id2synset =  c_sy_id2synset
        c._graph = graph
        c._cat2counts = cat2counts
        return c
    
        