"""
filename globbing relative to a base directory 
"""

import os
import glob


def relglob(basedir, pattern):
    """
    glob for filenames matching pattern relative to basedir
    """
    cwd = os.getcwd()
    os.chdir(basedir)
    paths = glob.glob(pattern)
    os.chdir(cwd)
    return paths

    