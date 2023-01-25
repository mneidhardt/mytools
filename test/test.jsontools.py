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

    def test_buildJSONSchema1(self):
        jt = EUCDMJSONTool()
        jt.setPatternMatcher(PatternMatcher())

        key = 1
        name = 'Declaration'
        mincard = 1
        maxcard = 1
        altkey = 'alternativekey'
        format = 'an10'
        root = EUCDMNode(key, name, mincard, maxcard, altkey, format)
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertEqual(schema[name]['description'], root.getDescription())
        self.assertTrue(schema[name]['type'] == 'string')
        self.assertTrue(schema[name]['minLength'] == 10)
        self.assertTrue(schema[name]['maxLength'] == 10)

    def test_buildJSONSchema2(self):
        jt = EUCDMJSONTool()
        jt.setPatternMatcher(PatternMatcher())

        key = 2
        name = 'Declaration'
        mincard=0
        maxcard=9
        altkey = None
        format = 'a6'
        codelist = 'Y'
        root = EUCDMNode(key, name, mincard, maxcard, altkey, format, codelist)
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertEqual(schema[name]['description'], root.getDescription())
        self.assertTrue(schema[name]['type'] == 'array')
        self.assertTrue(schema[name]['minItems'] == mincard)
        self.assertTrue(schema[name]['maxItems'] == maxcard)
        self.assertTrue('items' in schema[name])
        self.assertTrue(schema[name]['items']['type'] == 'string')
        self.assertTrue(schema[name]['items']['minLength'] == 6)
        self.assertTrue(schema[name]['items']['maxLength'] == 6)

    def test_buildJSONSchema3(self):
        jt = EUCDMJSONTool()
        jt.setPatternMatcher(PatternMatcher())

        key = 3
        name = 'Declaration'
        mincard = 1
        maxcard = 99
        root = EUCDMNode(key, name, mincard, maxcard)

        childkey = 31
        childname = 'LRN'
        childmincard = 0
        childmaxcard = 1
        childaltkey = 'alternativekey'
        childformat = 'n10'
        root.addChild(EUCDMNode(childkey, childname, childmincard, childmaxcard, childaltkey, childformat))
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertEqual(schema[name]['description'], root.getDescription())
        self.assertTrue(schema[name]['type'] == 'array')
        self.assertTrue(schema[name]['minItems'] == mincard)
        self.assertTrue(schema[name]['maxItems'] == maxcard)
        self.assertTrue('items' in schema[name])
        self.assertTrue('type' in schema[name]['items'])
        self.assertTrue('additionalProperties' in schema[name]['items'])
        self.assertTrue('properties' in schema[name]['items'])
        self.assertTrue(schema[name]['items']['type'] == 'object')
        self.assertTrue(schema[name]['items']['additionalProperties'] is False)
        self.assertTrue(childname in schema[name]['items']['properties'])

        #print(json.dumps(schema, indent=4))

    def test_buildJSONSchema4(self):
        jt = EUCDMJSONTool()
        jt.setPatternMatcher(PatternMatcher())

        key = 4
        name = 'ExitCarrier'
        mincard = 1
        maxcard = 1
        root = EUCDMNode(key, name, mincard, maxcard)
        childkey = 41
        childname = 'LRN'
        childmincard = 1
        childmaxcard = 1
        childaltkey = None
        childformat = 'n10'
        root.addChild(EUCDMNode(childkey, childname, childmincard, childmaxcard, childaltkey, childformat))
        schema = {}
        schema[jt.convertName(root.getName())] = jt.buildJSONSchema(root)
        self.assertTrue(name in schema)
        self.assertEqual(schema[name]['description'], root.getDescription())
        self.assertTrue(schema[name]['type'] == 'object')
        self.assertTrue(childname in schema[name]['properties'])
        self.assertTrue('type' in schema[name]['properties'][childname])
        self.assertTrue(schema[name]['properties'][childname]['type'] == 'integer')

        #print(json.dumps(schema, indent=4))



if __name__ == '__main__':
    unittest.main()
