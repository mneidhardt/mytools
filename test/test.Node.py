import unittest
import sys
import os
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode

class TestNode(unittest.TestCase):
    def test_types1(self):
        self.assertRaises(ValueError, EUCDMNode, None, 'name', 1, 2)    # Key (arg 1) must be int.

    def test_types2(self):
        self.assertRaises(ValueError, EUCDMNode, 1, 1, 1, 2)            # Name (arg 2) must be string.

    def test_types3(self):
        self.assertRaises(ValueError, EUCDMNode, None, None, 1, 2)      # Testing both.
        
    def test_types4(self):
        self.assertRaises(ValueError, EUCDMNode, 1, 'name', '1', 2)      # MinCardinality must be an int.
        
    def test_types5(self):
        self.assertRaises(ValueError, EUCDMNode, 1, 'name', 1, '2')      # MaxCardinality must be an int.
        
    def test_types6(self):
        self.assertRaises(ValueError, EUCDMNode, 1, 'name', '1', '2')    # Both.
        
    def test_description(self):
        key = 534
        mincard = 0
        maxcard = 999
        name = 'NatureOfTransaction'
        altkey = '12 02/000 000'
        format = 'an..6'
        node = EUCDMNode(key, name, mincard, maxcard, altkey, format)
        print(str(node), ' DESCRIPTION=', node.getDescription())

        self.assertEqual(node.getDescription(), '534/12 02#47;000 000/an..6')

    def test_parseFormat1(self):
        key = 534
        mincard = 0
        maxcard = 999
        name = 'NatureOfTransaction'
        altkey = '12 02 000 000'
        format = 'an..6'
        node = EUCDMNode(key, name, mincard, maxcard, altkey, format)
        print(str(node))

        self.assertEqual(node.getKey(), key)
        self.assertEqual(node.getName(), name)
        self.assertEqual(node.getMinCardinality(), mincard)
        self.assertEqual(node.getMaxCardinality(), maxcard)
        self.assertEqual(node.getAltKey(), altkey)
        self.assertEqual(node.getFormat(), format)
        self.assertEqual(node.getCodelist(), None)

    def test_parseFormat2(self):
        key = 712
        mincard = 1
        maxcard = 9
        name = 'Buyer'
        node = EUCDMNode(key, name, mincard, maxcard)
        print(str(node))

        self.assertEqual(node.getKey(), key)
        self.assertEqual(node.getName(), name)
        self.assertEqual(node.getMinCardinality(), mincard)
        self.assertEqual(node.getMaxCardinality(), maxcard)
        self.assertEqual(node.getAltKey(), None)
        self.assertEqual(node.getFormat(), None)
        self.assertEqual(node.getCodelist(), None)

    def test_parseFormat3(self):
        key = 57
        mincard = 1
        maxcard = 9
        name = 'ExitCarrier'
        altkey = None
        format = 'a2'
        codelist = 'Y'
        node = EUCDMNode(key, name, mincard, maxcard, altkey, format, codelist)
        print(str(node))

        self.assertEqual(node.getKey(), key)
        self.assertEqual(node.getName(), name)
        self.assertEqual(node.getMinCardinality(), mincard)
        self.assertEqual(node.getMaxCardinality(), maxcard)
        self.assertEqual(node.getAltKey(), None)
        self.assertEqual(node.getFormat(), format)
        self.assertEqual(node.getCodelist(), codelist)

    def test_parseFormat4(self):
        key = 1
        name = 'Parent'
        mincard = 1
        maxcard = 99
        root = EUCDMNode(key, name, mincard, maxcard)

        c1key = 11
        c1name = 'kid_1'
        c1mincard = 0
        c1maxcard = 1
        altkey = None
        c1format = 'n10'
        c1 = EUCDMNode(c1key, c1name, c1mincard, c1maxcard, altkey, c1format)
        c1.setParent(root)

        c2key = 12
        c2name = 'kid_2'
        c2mincard = 0
        c2maxcard = 1
        c2format = 'n10'
        c2 = EUCDMNode(c2key, c2name, c2mincard, c2maxcard, c2format)
        c2.setParent(root)

        root.addChild(c1)
        root.addChild(c2)
        
        allkids = root.getChildren()
        self.assertEqual(len(allkids), 2)
        self.assertEqual(allkids[0].getName(), c1name)
        
        p1 = allkids[0].getParent()
        p2 = allkids[1].getParent()
        self.assertEqual(p1.getName(), name)
        self.assertEqual(p2.getName(), name)
        

if __name__ == '__main__':
    unittest.main()
