import io
import re
import os
import pathlib

class FileTools():

    # Get a list of files in a given directory, whose names end with the given string.
    def getFilesByType(self, startpath, filenameEndsWith):
        files = []
        for p in pathlib.Path(startpath).iterdir():
            if p.is_file() and str(p).lower().endswith(filenameEndsWith.lower()):
                files.append(str(p))
        return files

    # Read a file line by line.
    def readFilelines(self, filename):
        result = []
        with open(filename) as f:
            for line in f:
                result.append(line)
        return result

    def isFile(self, name):
        return os.path.isfile(name)
        
    def isDir(self, name):
        return os.path.isdir(name)
