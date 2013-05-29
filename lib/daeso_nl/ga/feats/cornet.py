"""
Cornetto features
"""

# TODO:
# - document
# - create direct cornet instance 

from daeso.pair import Pair
from daeso_nl.ga.feature import Feat
from daeso_nl.cornetto.cornet import SEPERATOR
from daeso_nl.cornetto.server import DEFAULT_HOST, DEFAULT_PORT


# All global variables define feature *tuples*, 
# so it's easy to concatenate features using "+".

# A feature function (ff) is always called as:
#
# ff( n_count = Pair(source_node_count, target_node_count),
#     nodes = Pair(source_node, target_node),
#     graphs = Pair(source_graph, target_graph),
#     alignment = Graphpair )


# *********************************************************************
# Make sure that all values of string-valued features fit it the number
# of chars reserved for it in Numpy record! (e.g. "S10")
# Otherwise, they will get truncated, which is especially harmfull to 
# relation fields (e.g. pred_relation") during evaluation.
# *********************************************************************


#-------------------------------------------------------------------------------
# Cornetto server
#-------------------------------------------------------------------------------

_CORNET = None


def load_cornet(cdb_lu_fname, cdb_syn_fname):
    """
    load cornetto database directly
    """
    from daeso_nl.cornetto.cornet import DaesoCornet
    
    global _CORNET
    _CORNET = DaesoCornet(
        cdb_lu=cdb_lu_fname, 
        cdb_syn=cdb_syn_fname)


def create_cornet_server_proxy(host="", verbose=False):
    import xmlrpclib
    import socket
    
    global _CORNET
    if host.startswith("http://"):
        host = host[7:]
    
    try:
        host, port = host.split(":")[:2]
    except ValueError:
        host, port = host, None
        
    # XMP-RPC requires specification of protocol
    host = "http://" + (host or DEFAULT_HOST)
    
    try:
        port = int(port or DEFAULT_PORT)
    except ValueError:
        raise ValueError("%s is not a valid port number" % repr(port))
    
    _CORNET = xmlrpclib.ServerProxy("%s:%s" %  (host, port),
                                    encoding="utf-8",
                                    verbose=verbose)
    try:
        _CORNET.echo("test")
    except socket.error, inst:
        msg = "%s\nCornetto server not running on %s:%s ?" % (
            inst, host, port)
        raise socket.error(msg)
    

def init_cornet(value):
    """
    initialize cornetto from a custom object or proxy
    """
    from daeso_nl.cornetto.cornet import DaesoCornet
    from xmlrpclib import ServerProxy
    global _CORNET
    assert isinstance(value, DaesoCornet) or isinstance(value, ServerProxy)
    _CORNET = value
    
    
def close_cornet():
    """
    unload cornetto database or close connection to server
    """
    global _CORNET
    _CORNET = None
    

#-------------------------------------------------------------------------------
# Preprocessing functions
#-------------------------------------------------------------------------------


def pp_cornet_sim(graphs):
    """
    A preprocessing function
    
    Requires access to the Cornetto database. By default we assume a
    DaesoCornet server is running on localhost. Otherwise you have to create
    your own client by calling the function "create_cornet_server_proxy".
    Alternatively, you can load Cornetto directly by calling the function
    "load_cornet".
    """
    from_spec_list = _get_spec_list(graphs.source)
    to_spec_list = _get_spec_list(graphs.target)
    
    try:
        graphs.source.graph["cornet_sim"] = \
        cornet_sim = _CORNET.multi_semantic_sim(from_spec_list, to_spec_list)
    except AttributeError:
        # create default Cornetto server proxy, and retry
        create_cornet_server_proxy()
        graphs.source.graph["cornet_sim"] = \
        cornet_sim = _CORNET.multi_semantic_sim(from_spec_list, to_spec_list)
    

def _get_spec_list(graph):
    spec_list = []
    
    for node in graph.terminals_iter(with_punct=False, with_empty=False):
        pos = graph.node[node]["pos"]
        compounds = graph.node[node]["root"].split("_")
        
        # translation of Alpino part-of-speech tags to Cornetto categories
        # (excl. function words), plus some hacks to deal with Alpino's
        # morphological analysis
        if pos == "verb":
            cat = "verb"
            
            if len(compounds) == 2:
                # geven_aan -> aangeven
                compounds = compounds[1] + compounds[0]
        elif pos == "noun":
            # FIXME: concatanating noun compounds does not always give the
            # desired lemma. For example,  
            # student_huis -> *studenthuis (studentenhuis)
            # leven_omstandigheid -> *levenomstandigheid (levensomstandigheid)
            # klok_maker -> *klokmaker (klokkemaker) 
            # anti_Amerikaans -> *antiAmerikaans (anti-Amerikaans)
            # ANWB_lid -> *ANWBlid (ANWB-lid)
            cat = "noun"
            
            try:
                # haak_DIM -> haak
                compounds.remove("DIM")
            except ValueError:
                pass
        elif pos == "adj":
            cat = "adj"
        elif pos == "adv":
            cat = "adv"
        elif pos == "name":
            cat = "noun"
        else:
            # function word not covered in Cornetto DB
            continue
        
        lemma = "".join(compounds)
        spec_list.append(lemma + ":" + cat + SEPERATOR + node)
        
    return spec_list
            
            
        

#-------------------------------------------------------------------------------
# Cornetto similarity float
#-------------------------------------------------------------------------------

def ff_cornet_restates(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return round(graphs.source.graph["cornet_sim"][nodes][0], 1)
    except KeyError:
        return 0.0
    
cornet_restates = Feat( ff_cornet_restates, "f8", "N",
                        pp_graph_hooks=[pp_cornet_sim]),



def ff_cornet_specifies(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return round(graphs.source.graph["cornet_sim"][nodes][1], 1)
    except KeyError:
        return 0.0
    
cornet_specifies = Feat( ff_cornet_specifies, "f8", "N",
                         pp_graph_hooks=[pp_cornet_sim]),




def ff_cornet_generalizes(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return round(graphs.source.graph["cornet_sim"][nodes][2], 1)
    except KeyError:
        return 0.0
    
cornet_generalizes = Feat( ff_cornet_generalizes, "f8", "N",
                           pp_graph_hooks=[pp_cornet_sim]),



def ff_cornet_intersects(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return round(graphs.source.graph["cornet_sim"][nodes][3], 1)
    except KeyError:
        return 0.0
    
cornet_intersects = Feat( ff_cornet_intersects, "f8", "N",
                          pp_graph_hooks=[pp_cornet_sim]),



cornet_sim_float = ( cornet_restates +
                     cornet_specifies +
                     cornet_generalizes +
                     cornet_intersects )


#-------------------------------------------------------------------------------
# Cornetto similarity boolean
#-------------------------------------------------------------------------------

def ff_cornet_restates_bool(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return "T" if graphs.source.graph["cornet_sim"][nodes][0] else "F"
    except KeyError:
        return "?"
    
cornet_restates_bool = Feat( ff_cornet_restates_bool, "S1",
                             pp_graph_hooks=[pp_cornet_sim]),



def ff_cornet_specifies_bool(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return "T" if graphs.source.graph["cornet_sim"][nodes][1] else "F"
    except KeyError:
        return "?"
    
cornet_specifies_bool = Feat( ff_cornet_specifies_bool, "S1",
                              pp_graph_hooks=[pp_cornet_sim]),




def ff_cornet_generalizes_bool(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return "T" if graphs.source.graph["cornet_sim"][nodes][2] else "F"
    except KeyError:
        return "?"
    
cornet_generalizes_bool = Feat( ff_cornet_generalizes_bool, "S1",
                                pp_graph_hooks=[pp_cornet_sim]),



def ff_cornet_intersects_bool(nodes, graphs, **kwargs):
    """
    
    """
    nodes = ",".join(nodes)
    try:
        return "T" if graphs.source.graph["cornet_sim"][nodes][3] else "F"
    except KeyError:
        return "?"
    
cornet_intersects_bool = Feat( ff_cornet_intersects_bool, "S1",
                               pp_graph_hooks=[pp_cornet_sim]),



cornet_sim_bool = ( cornet_restates_bool +
                    cornet_specifies_bool +
                    cornet_generalizes_bool +
                    cornet_intersects_bool )


cornet_sim = cornet_sim_float + cornet_sim_bool


# restrict "from ... import *" to named feature tuples,
# omitting feature functions and others
__all__ = [ name 
            for name, obj in globals().items() 
            if isinstance(obj, tuple) and isinstance(obj[0], Feat) ]

__all__ +=  ["load_cornet", 
             "create_cornet_server_proxy", 
             "init_cornet", 
             "close_cornet"]



