import xml.etree.ElementTree as etree
import re

# Class that handles various aspects of XML parsing.
#----------------------------------------------------------------------------------------
class XMLParser():
    def __init__(self, file):
        self.NSpattern = None
        self.filename = file
        self.root = etree.parse(self.filename).getroot()
    
    def setRootname(self, newname):
        oldname = self.root.tag
        self.root.tag = newname
        return oldname

    def getAllPaths(self):
        self.NSpattern = re.compile('^\{[^}]+\}(.+)$')
        result = self.dfswp(self.root, [])
        return result

    # Remove NS string.
    def cleanupTag(self, tag):
        match = self.NSpattern.match(tag)
        if match:
            return match.group(1)
        else:
            return tag

    # Does depth first traversal, with path.
    # This means that the method saves the full path of every leaf.
    # Returns a list of all leaves with full path.
    def dfswp(self, node, path):
        result = []
        if node is None:
            return result
        else:
            path.append(self.cleanupTag(node.tag))

        if len(node) == 0:
            result.append('/'.join(path))
        else:
            for child in node:
                result.extend(self.dfswp(child, path))
                path.pop()
        
        return result
