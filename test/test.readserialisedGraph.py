
import unittest
import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph

class TestGraph(unittest.TestCase):

    filename = ''

    def test_reader(self):
        gtool = Graph()
        sgraf = gtool.readSerialisedGraph(self.filename)

        for node in sgraf:
            self.assertTrue(len(node) == 3)
            print(node)

if __name__ == '__main__':
    TestGraph.filename = sys.argv.pop()
    unittest.main()
