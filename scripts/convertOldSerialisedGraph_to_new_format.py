import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.eucdm.datacatalog import DataCatalog
from mytools.files.filetools import FileTools


# In the early versions of the schema builder, I stored the serialised graph as
# a list of DE numbers. The new format uses keys that refer to elements in the datacatalog.
# This script reads an old style serialised graph, converts the DE number to the correct key, and prints
# it, along with any cardinality; it also prints the end-of-child markers, of course.
if __name__ == "__main__":

    inputfilename = sys.argv[1] # Name of file containing old style serialised graph.
    catalogfilename = sys.argv[2]
    dc = DataCatalog(catalogfilename)
    ft = FileTools()
    inputdata = ft.readFilelines(inputfilename)
    
    for row in inputdata:
        if row.strip() == '!':
            print(row, end='')
        else:
            parts = row.strip().split('/')
            data = dc.lookupAltID(parts[0]) # DENumber is first, possibly followed by '/' and a cardinality.
            if data is None:
                print(row, 'has no key!!!')
            else:
                if len(parts) == 1:
                    print(data[0])
                elif len(parts) == 2:
                    print(data[0] + '/1/' + parts[1]) # Append the max.cardinality. Fix min.cardinality by hand.
                else:
                    print('???: parts=', parts)
