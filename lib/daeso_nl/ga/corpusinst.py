import codecs
import numpy


# TODO:
# - split in TextCorpusInst and BinCorpusInst?
# - use weakref for self.file?


class CorpusInst(list):
    """
    Instances for a corpus of parallel graphs
    
    A CorpusInst object is a list of graph pair instances, which are numpy
    record arrays. In addition, CorpusInst provides file IO with persistent
    load and save settings.
    """
    
    def __init__(self, sequence=[]):
        list.__init__(self, sequence)
        self.file_format = None
        
    
    def savebin(self, file=None):
        """
        save corpus instances in binary numpy format (.npy), which includes the dtype
        """
        if isinstance(file, basestring):
            # open file first, because numpy.save will automatically append a
            # ".npy" extension if file is a string
            file = open(file, "wb")
            
        numpy.save(file, numpy.concatenate(self))
        
        self.file_format = "bin"
        self.file = file
    
        
    def loadbin(self, file, split_func=None):
        """
        load corpus instances in binary numpy format (.npy), which includes the dtype
        """
        instances = numpy.load(file)
        
        split_func = split_func or self._is_graph_inst_start

        indices = [ i for i in range(1, len(instances))
                    if split_func(instances[i]) ]
        
        self[:] = numpy.array_split(instances, indices)
        
        self.file_format = "bin"
        self.split_func = split_func
        self.file = file

        
    def savetxt(self, file, fmt=None, delimiter="\t", encoding="utf-8"):
        """
        save corpus instances in text format, which does not include the dtype
        """
        # if file is file object, the encoding keyword is ignored, and the
        # file will not be closed
        if isinstance(file, basestring):
            fh = codecs.open(file, "w", encoding=encoding)
        else:
            fh = file
            
        if not fmt:
            fmt = len(self[0][0]) * ("%s",)
            
        numpy.savetxt(fh, numpy.concatenate(self), 
                      fmt=fmt, delimiter=delimiter)
        
        if isinstance(file, basestring):
            fh.close()
            
        self.file_format = "txt"
        self.file = file
        self.fmt=fmt
        self.delimiter=delimiter
        self.encoding = getattr(fh, "encoding", None)
        
        
    def loadtxt(self, file, dtype, comments='#', delimiter="\t",
                converters=None, skiprows=0, usecols=None, unpack=False, 
                split_func=None, encoding="utf-8"):
        """
        load corpus instances in text format, which requires a dtype
        """
        # if file is file object, the encodinh keyword is ignored, and the
        # file will not be closed
        if isinstance(file, basestring):
            fh = codecs.open(file, encoding=encoding)
        else:
            fh = file

        # Specify converters for unicode values.
        # This is a patch for a bug in numpy where the _getconv func in numeric.py
        # return str() as the converter for values of type unicode,
        # which results in an encoding error
        if not converters:
            converters = {}
            for i, (name, format) in enumerate(dtype.descr):
                if "U" in format:
                    converters[i] = lambda s: s
        
        if not split_func:
            split_func = self._is_graph_inst_start
            
        instances = numpy.loadtxt(fh, dtype=dtype, comments=comments,
                                  delimiter=delimiter, converters=converters, skiprows=skiprows,
                                  usecols=usecols, unpack=unpack)
        
        if isinstance(file, basestring):
            fh.close()
        
        indices = [ i for i in range(1, len(instances)) 
                    if split_func(instances[i]) ]
        
        self[:] = numpy.array_split(instances, indices)
        
        self.file_format = "txt"
        self.file = file
        self.dtype = dtype
        self.comments = comments
        self.delimiter = delimiter
        self.converters = converters
        self.skiprows = skiprows
        self.usecols = usecols
        self.unpack = unpack
        self.split_func = split_func
        self.encoding = getattr(fh, "encoding", None)
        
    def save(self):
        """
        resave using the settings from the last save operation
        """
        if self.file_format == "txt":
            try:
                fmt = self.fmt
            except AttributeError:
                # not defined is previous action was loadtxt rather than savetxt
                fmt = len(self[0][0]) * ("%s",)
            
            self.savetxt(self.file, 
                         fmt=fmt, 
                         delimiter=self.delimiter,
                         encoding=self.encoding)
        elif self.file_format == "bin":
            self.savebin(self.file)
        else:
            raise IOError("nothing loaded or saved yet; "
                          "use savetxt or savebin instead")
    
    
    def load(self):
        """
        reload using the settings from the last load operation
        """
        if self.file_format == "txt":
            self.loadtxt(self.file, self.dtype,
                         comment=self.comments,
                         delimiter=self.delimiter,
                         converters=self.converters,
                         skiprows=self.skiprows,
                         usecols=self.usecols,
                         unpack=self.unpack,
                         split_func=self.split_func,
                         encoding=self.encoding)
        elif self.file_format == "bin":
            self.loadbin(self.file, 
                         split_func=self.split_func)
        else:
            raise IOError("nothing loaded or saved yet; "
                          "use savetxt or savebin instead")
    
        
    def _is_graph_inst_start(self, inst):
        """
        test if inst is start of graph instances
        """
        return inst["source_node_count"] == 1 and inst["target_node_count"] == 1
    