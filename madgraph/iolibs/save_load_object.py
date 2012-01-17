################################################################################
#
# Copyright (c) 2009 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################

"""Function to save any Python object to file."""

import pickle
import cPickle

from . import files as files

class SaveObjectError(Exception):
    """Exception raised if an error occurs in while trying to save an
    object to file."""
    pass

def save_to_file(filename, object):
    """Save any Python object to file filename"""

    if not isinstance(filename, str):
        raise SaveObjectError, "filename must be a string"

    files.write_to_file(filename, pickle_object, object)

    return True
    
def load_from_file(filename):
    """Save any Python object to file filename"""

    if not isinstance(filename, str):
        raise SaveObjectError, "filename must be a string"

    return files.read_from_file(filename, unpickle_object)
    
def pickle_object(fsock, object):
    """Helper routine to pickle an object to file socket fsock"""

    cPickle.dump(object, fsock, protocol=2)

class UnPickler(pickle.Unpickler):
    """Treat problem of librarie"""
    
    def find_class(self, module, name):
        """Find the correct path for the given function.
           Due to ME call via MG some libraries might be messed up on the pickle
           This routine helps to find back which one we need. 
        """

        try:
            return pickle.Unpickler.find_class(self, module, name)
        except ImportError:
            pass
        
        newmodule = 'internal.%s' % module.rsplit('.',1)[1]
        try:
            return pickle.Unpickler.find_class(self, newmodule , name)
        except:
            pass
        
        newmodule = 'madgraph.iolibs.%s' % module.rsplit('.',1)[1]
        try:
            return pickle.Unpickler.find_class(self, newmodule , name)
        except:
            pass        

        newmodule = 'madgraph.various.%s' % module.rsplit('.',1)[1]
        try:
            return pickle.Unpickler.find_class(self, newmodule , name)
        except:
            raise
    

def unpickle_object(fsock):
    """Helper routine to pickle an object to file socket fsock"""

    p = UnPickler(fsock)
    return p.load()
    #return pickle.load(fsock)

