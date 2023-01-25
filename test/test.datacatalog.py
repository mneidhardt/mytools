import unittest
import sys
import os
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.eucdm.datacatalog import DataCatalog
from mytools.files.filetools import FileTools

class TestDataCatalog(unittest.TestCase):
    def test_datacatalog(self):
        dc = DataCatalog(self.filename)
        
        row = dc.lookupKey(1)
        self.assertEqual(row['displayname'], 'Declaration')

        
        row = dc.lookupKey(9)
        self.assertEqual(row['altID'], '11 01 001 000')
        self.assertEqual(row['displayname'], 'Declaration type')
        self.assertEqual(row['format'], 'p=^.{1,5}$')
        self.assertEqual(row['codelist'], 'Y')
        self.assertEqual(row['elementname'], 'declarationType')
        self.assertEqual(row['domain'], 'IE')
        self.assertEqual(row['description'], '')

        row = dc.lookupKey(10)
        self.assertEqual(row, None)

    def test_altID(self):
        dc = DataCatalog(self.filename)
        row = dc.lookupAltID('1')
        self.assertEqual(row[2], 'Declaration')
        
        row = dc.lookupAltID('xyz')
        self.assertEqual(row, None)
        
        row = dc.lookupAltID('11 01 000 000')
        self.assertEqual(row[2], 'Arrival Date And Time')
        
if __name__ == '__main__':
    TestDataCatalog.filename = sys.argv.pop()
    unittest.main()
