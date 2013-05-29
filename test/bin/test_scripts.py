"""
test Daeso Dutch command line scripts
"""

# If tests fail, make sure to manually kill server processes! 

# Assumes that all executables are in PATH

import pprint
import socket
import subprocess
import time
import unittest
import xmlrpclib



class Test_graph_align_server(unittest.TestCase):

    def setUp(self):
        pass
    
    def test1_help(self):
        print 
        subprocess.check_call(("graph_align_server.py", "-h"))
        
    def test2_ga0(self):
        print 
        proc = subprocess.Popen(["graph_align_server.py", 
                                 "../../config/ga0/ga0_cfg.py"])
        server_proxy = xmlrpclib.ServerProxy("http://localhost:5508", 
                                             encoding="utf-8")
        for i in range(12):
            try:
                result = server_proxy.align("test", "test")
            except socket.error, inst:
                print inst
            else:
                break

            time.sleep(5)

        pprint.pprint(result)
        proc.kill()
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()