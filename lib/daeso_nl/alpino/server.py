
"""
basic socket server exposing the Alpino parser through XML-RPC
"""

import sys
import os
import os.path
import tempfile
import time
from SimpleXMLRPCServer import SimpleXMLRPCServer

from daeso.thirdparty import pexpect
from daeso.thirdparty.GenericCache import GenericCache

# TODO:
# - bettter way to handle timeout of alpino and pexepect
# - choice to use cachee or not, cache settings
# - is it faster to return the parse as base 64 encoded binary?

from exceptions import Exception


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 5506


class AlpinoException(Exception):
    pass


class AlpinoParser(object):
    """
    A thin Python wrapper around the Alpino parser for Dutch.
    The input must be a tokenized Dutch sentence in unicode.
    The output is a parse tree in xml format in unicode.
    Relies on Pexpect for running Alpino as a subprocess and providing
    non-blocking communication through a pipe.
    Requires a local copy of the Alpino parser binary and an appropriate 
    setting of the ALPINO_HOME environment variable.
    """
    
    def __init__(self, command=None, out_dir=None, verbose=False):
        self.out_dir = out_dir or tempfile.gettempdir()
        self.verbose = verbose
        
        if not command:
            home = os.getenv("ALPINO_HOME")
            
            if not home:
                raise NameError("environment variable ALPINO_HOME "
                                "is not defined")

            # even if pexpect is timed out, 
            # the parsing process will happely continue forever,
            # so a corresponding user_max flag is required
            command = ( home + "/bin/Alpino "
                        "end_hook=xml "
                        "root_of_verb_uses_inf=on "
                        "demo=off "
                        "user_max=30000 "
                        "-flag treebank %s " % self.out_dir +
                        "-notk "
                        "-parse ")

            
        self._log("Starting parser with command:\n", command)
        
        # Alpino should start within 30 secs,
        # otherwise a TIMEOUT exception will be raised
        self.child = pexpect.spawn(command)
        self.child.expect("\* ")
        
    
    def _log(self, *msg):
        # assume log is also iso-8859-1 encoded
        if self.verbose:
            print >>sys.stderr, " ".join(msg)
        
        
    def parse(self, sentence, ident="last", timeout=30):
        out_file = self.out_dir + "/" + ident + ".xml"
        
        # remove old output (if any)
        if os.path.exists(out_file):
            os.remove(out_file)
                
        # Sentence will be of type unicode if the original sentence passed to
        # the server proxy (client) contained any non-ascii chars, but will
        # be of type str otherwise. Alpino needs utf-8 input.
        sentence_str = sentence.encode("utf-8")

        sentence_str = ident + "|" + sentence_str.strip()

        self._log("Parser input:\n", sentence_str)
        
        self.child.sendline(sentence_str)
        
        # may raise a TIMEOUT exception
        try:
            self.child.expect("\n\* ", timeout=timeout)
        except pexpect.TIMEOUT:
            raise AlpinoException("Parser timeout (%ds) exceeded" % timeout)

        # wait for the parser to write its output to file
        output = None
        start_time = time.time()
        max_time = 10

        while not output:
            try:
                output = open(out_file).read()
            except IOError, inst:
                if getattr(inst, "errno") == 2:
                    # IOError: [Errno 2] No such file or directory
                    if time.time() - start_time < max_time:
                        time.sleep(0.1)
                    else:
                        self._log("No parser output")
                        raise AlpinoException("No parser output")
                else:
                    self._log("Unknown error:", inst)
                    raise
            
        self._log("Parser output:\n", output)
        
        # Return unicode. Even though Alpino declares the encoding of its XML
        # output to be ISO-8859-1, it is in fact UTF-8.
        return output.decode("utf-8")
    
    

class CachedAlpinoParser(AlpinoParser):
    
    def __init__(self, command=None, out_dir=None, verbose=False,
                 maxsize=2500, expiry=None):
        AlpinoParser.__init__(self, command, out_dir, verbose)
        # default_fail must be true for setdefault to work
        self.cache = GenericCache(maxsize=maxsize, expiry=expiry, default_fail=True)
        self._log("Init cache with maxsize", str(maxsize))
        
    
    def parse(self, sentence, ident="last", timeout=300):
        # Sentence will be of type unicode if the original sentence passed to
        # the Alpino server proxy (client) contained any non-ascii chars, but
        # will be of type str otherwise.
        
        # The cache converts the key to a string, using str(),
        # in order to use it for hashing.
        # This causes an encoding error when the sentence is a unicode
        # string derived from a non-ascii input sentence.
        # Hence we need to encode it explicitly (also for logging)
        sentence_str = sentence.encode("utf-8")

        try:
            parse = self.cache[sentence_str]
        except KeyError:
            parse = AlpinoParser.parse(self, sentence, ident, timeout)
            self.cache[sentence_str] = parse
            self._log("Caching parse for:\n", sentence_str)
        else:
            self._log("Retrieved parse from cache for:\n", sentence_str)
        
        return parse
        
    

def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT, log=None,
                 command=None, out_dir=None, verbose=False,
                 cache_size=0):   
    """
    main function to start the Alpino XMLRPC server
    
    @keyword host: host to listen on
    @type host: string
    
    @keyword port: port to listen on
    @type port: int
    
    @keyword log: log requests  
    @type log: bool

    @keyword command: command line to start Alpino parser
    @type command: string
    
    @keyword out_dir: directory to store temporary files (parses)
    @type command: string
    
    @keyword verbose: verbose output during parsing    
    @type verbose: bool
    """
    if cache_size:
        parser = CachedAlpinoParser(command, out_dir, verbose, maxsize=cache_size)
    else:
        parser = AlpinoParser(command, out_dir, verbose)
        
    # encoding for transport stays the default, utf-8,
    # no relation to the iso-88591-1 encoding of the server proxy  
    server = SimpleXMLRPCServer((host, port), logRequests=log)
    server.register_introspection_functions()
    server.register_instance(parser)
    
    print >>sys.stderr, "Alpino server listening on %s:%d" % (host, port)
    server.serve_forever()
    
    


    
    
