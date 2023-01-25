import io
import re
import os
import csv
import pathlib

class FileTools():

    # Get a list of files in a given directory.
    # If filenameEndsWith is *not* None, returns only files whose names end with the given string.
    # If recursive is True, recurse through sub folders.
    def getFiles(self, startpath, filenameEndsWith=None, recursive=False):
        result = []
        for p in pathlib.Path(startpath).iterdir():
            if p.is_file() and filenameEndsWith is None:
                result.append(str(p))
            elif p.is_file() and str(p).lower().endswith(filenameEndsWith.lower()):
                result.append(str(p))
            elif p.is_dir() and recursive:
                result.extend(self.getFiles(str(p), filenameEndsWith, recursive))
        return result

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

    def readCSVFile(self, filename, delim=';'):
        result = []

        with open(filename) as csvfile:
            crdr = csv.reader(csvfile, delimiter=delim)
            for row in crdr:
                result.append(row)

        return result

    def writeCSVFile(self, csvdata, filename, delim=';'):
        with open(filename, 'w', newline='') as csvfile:
            mywriter = csv.writer(csvfile, delimiter=delim,
                                    quotechar='|')
            for row in csvdata:
                mywriter.writerow(row)
