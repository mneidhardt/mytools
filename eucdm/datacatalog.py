import csv
import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.files.filetools import FileTools

#
# This class is a container for the data catalog.
# The catalog is stored as a CSV file, containing the catalog.
# This class wraps it in a more user friendly and robust way.
#
# The CSV data currently contains these columns:
#   0. Primary key
#   1. Alternative identification (e.g. DENumber)
#   2. Display name
#   3. Format or regular expression
#      This is either an EUCDM style format (i.e. anX, an..X, nY, n..Y),
#      or a regex pattern. A regex must follow this: p=<regex>.
#      Example: p=^abc[0-9]{1,2}$
#      for the string abc followed by 1 or 2 digits.
#
#      I consider allowing a reference to either another field or to a base type here,
#      so that I can reuse e.g. date patterns.  NB: NOT IMPLEMENTED YET!
#      If it is a reference, this will be resolved when instantiating this.
#   4. Codelist (Y if codelist is used for the element, N if not)
#   5. Schema element name, typically a doctored version of display name
#   6. Domain (currently any combination of I, E and T, for Import, Export and Transit)
#   7. Description
#
# These data will be exposed as follows:
#
#   A dict with primary key as key, and the remaining colums as value.
#
# TODO: Find some way of having reuse of entities and groups of entities in the catalog.
# One simple application is to reuse base types such as dates.
# A less simple application is to reuse subgraphs.
# This is in order to have more manageable graphs, that can then be put together by the builder.

class DataCatalog():

    # A third argument, basetypefilename, must be added when that functionality is implemented.
    def __init__(self, datacatalogfilename):
        ft = FileTools()
        self.rawcatalog = ft.readCSVFile(datacatalogfilename)       # Read the data catalog.

        self.catalog = {}

        for row in self.rawcatalog:
            if row[0] in self.catalog:
                raise ValueError('Duplicate key found in catalog (', catalogfilename, '): ', row[0])
            else:
                value = {}
                value['altID'] = row[1]
                value['displayname'] = row[2]
                value['format'] = row[3]
                value['codelist'] = row[4]
                value['elementname'] = row[5]
                value['domain'] = row[6]
                value['description'] = row[7]
                
                self.catalog[int(row[0])] = value
    
    def lookupKey(self, key):
        if key in self.catalog:
            export = {}
            for subkey in self.catalog[key]:
                export[subkey] = self.catalog[key][subkey]
            return export
        else:
            return None
    
    def lookupAltID(self, altID):
        for row in self.rawcatalog:
            if altID == row[1]:
                return row
        return None
        