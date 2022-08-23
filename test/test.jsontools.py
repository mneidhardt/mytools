import unittest
import sys
import os
import json
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode
from mytools.json.jsontools import EUCDMJSONTool
from mytools.eucdm.patternmatcher import PatternMatcher

class TestJSONTool(unittest.TestCase):

    def test_convertName(self):
        strings = ['Hi stranger', 'So you thought it was over, huh?', 'noNeed', '', ' ', 'Reference Number/UCR']
        results = ['Hi_stranger', 'So_you_thought_it_was_over,_huh?', 'noNeed', '', '_', 'Reference_Number/UCR']

        jt = EUCDMJSONTool()

        for i in range(0, len(strings)):
            cc = jt.convertName(strings[i])
            self.assertEqual(results[i], cc)

    def test_buildJSONSchema(self):
        jt = EUCDMJSONTool()
        jt.setPatternMatcher(PatternMatcher())

        key = '01 01'
        cardinality = 1
        name = 'Declaration'
        format = 'an10'
        root = EUCDMNode(key, cardinality, name, format)
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertTrue(schema[name]['description'].startswith(key))
        self.assertTrue(schema[name]['type'] == 'string')
        self.assertTrue(schema[name]['pattern'] == '^[a-åA-Å0-9]{10}$')

        key = '02 01'
        cardinality = 9
        name = 'Declaration'
        format = 'a6'
        root = EUCDMNode(key, cardinality, name, format)
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertTrue(schema[name]['description'].startswith(key))
        self.assertTrue(schema[name]['type'] == 'array')
        self.assertTrue(schema[name]['maxItems'] == cardinality)
        self.assertTrue('items' in schema[name])
        self.assertTrue(schema[name]['items']['type'] == 'string')
        self.assertTrue(schema[name]['items']['pattern'] == '^[a-åA-Å]{6}$')

        key = '03 01'
        cardinality = 9
        name = 'Declaration'
        root = EUCDMNode(key, cardinality, name, None)
        childkey = '03 02'
        childcardinality = 2
        childname = 'LRN'
        childformat = 'n10'
        root.addChild(EUCDMNode(childkey, childcardinality, childname, childformat))
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertTrue(schema[name]['description'].startswith(key))
        self.assertTrue(schema[name]['type'] == 'array')
        self.assertTrue(schema[name]['maxItems'] == cardinality)
        self.assertTrue('items' in schema[name])
        self.assertTrue('type' in schema[name]['items'])
        self.assertTrue('additionalProperties' in schema[name]['items'])
        self.assertTrue('properties' in schema[name]['items'])
        self.assertTrue(schema[name]['items']['type'] == 'object')
        self.assertTrue(schema[name]['items']['additionalProperties'] is False)
        self.assertTrue(childname in schema[name]['items']['properties'])

        key = '04 01'
        cardinality = 1
        name = 'Declaration'
        root = EUCDMNode(key, cardinality, name, None)
        childkey = '04 02'
        childcardinality = 1
        childname = 'LRN'
        childformat = 'n10'
        root.addChild(EUCDMNode(childkey, childcardinality, childname, childformat))
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertTrue(schema[name]['description'].startswith(key))
        self.assertTrue(schema[name]['type'] == 'object')
        self.assertTrue(childname in schema[name]['properties'])
        self.assertTrue(schema[name]['properties'][childname]['type'] == 'integer')

        #print(json.dumps(schema, indent=4))



if __name__ == '__main__':
    unittest.main()
