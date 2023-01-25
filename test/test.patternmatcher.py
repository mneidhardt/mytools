import unittest
import re
import sys
import os
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.eucdm.patternmatcher import PatternMatcher

class TestPatternMatcher(unittest.TestCase):
    def test_getRestrictions(self):
        pm = PatternMatcher()

        # Dict where key = input and value = expected result.
        tests = {}
        tests['a1']      = [['type', 'string'], ['minLength', 1], ['maxLength', 1]]
        tests['an18']    = [['type', 'string'], ['minLength', 18], ['maxLength', 18]]
        tests['a..3']    = [['type', 'string'], ['minLength', 0], ['maxLength', 3]]
        tests['an..512'] = [['type', 'string'], ['minLength', 0], ['maxLength', 512]]
        tests['n6']      = [['type', 'integer'], ['minimum', 100000], ['maximum', 999999]]
        tests['n12']     = [['type', 'integer'], ['minimum', 100000000000], ['maximum', 999999999999]]
        tests['n6,2']    = [['type', 'number'], ['minimum', 1000], ['maximum', 999999], ['multipleOf', 0.01]]
        tests['n9,6']    = [['type', 'number'], ['minimum', 100], ['maximum', 999999999], ['multipleOf', 0.000001]]
        tests['n..3']   = [['type', 'integer'], ['minimum', 0], ['maximum', 999]]
        tests['n..16']   = [['type', 'integer'], ['minimum', 0], ['maximum', 9999999999999999]]
        tests['n..2,1'] = [['type', 'number'], ['minimum', 0], ['maximum', 99], ['multipleOf', 0.1]]
        tests['n..12,5'] = [['type', 'number'], ['minimum', 0], ['maximum', 999999999999], ['multipleOf', 0.00001]]
        tests['   ']     = []
        tests['']        = []

        for input in tests:
            res = pm.getRestrictions(input)
            for i in range(0, len(res)):
                print("<",input, ">", end='')
                print('    ', tests[input][i], res[i])
                self.assertEqual(tests[input][i], res[i])

    def test_altVersion(self):
        pm = PatternMatcher()
        ok = ['1,1', '1,12', '12,1', '12,12', '123,1', '123,12', '1234,1', '1234,12', '1', '12', '123', '1234', '12345', '123456', '']
        notok = ['12345,1', '1234,123', '12345,12', '1234567']

        for t in ok:
            self.assertTrue(pm.altVersion(t))
        for t in notok:
            self.assertFalse(pm.altVersion(t))

    def test_altVersion2(self):
        pm = PatternMatcher()
        ok = ['1', '12', '123', '1234', '12345', '123456', '']
        notok = ['1234567', '12345678']

        for t in ok:
            self.assertTrue(pm.altVersion2(t))
        for t in notok:
            self.assertFalse(pm.altVersion2(t))

    def test_generateSample(self):
        pm = PatternMatcher()
        self.assertTrue(re.match('^[a-zA-Z]{6}$', pm.generateSample('a6')))
        self.assertTrue(re.match('^[a-zA-Z]{0,6}$', pm.generateSample('a..6')))
        self.assertTrue(re.match('^[a-zA-Z0-9]{9}$', pm.generateSample('an9')))
        self.assertTrue(re.match('^[a-zA-Z0-9]{0,5}$', pm.generateSample('an..5')))

        sample = pm.generateSample('n7')
        self.assertTrue(sample >= 1000000)
        self.assertTrue(sample <= 9999999)

        for i in range(0,1000):
            sample = float(pm.generateSample('n8,2'))
            self.assertTrue(sample >= 100000.00)
            self.assertTrue(sample <= 99999999.00)

        for i in range(0,1000):
            sample = int(pm.generateSample('n..2'))
            self.assertTrue(sample >= 0)
            self.assertTrue(sample <= 99)

        for i in range(0, 1000):
            sample = float(pm.generateSample('n..9,4'))
            self.assertTrue(sample >= 0.0)
            self.assertTrue(sample <= 999999999.00)

if __name__ == '__main__':
    unittest.main()
