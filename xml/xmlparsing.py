import xml.etree.ElementTree as etree
import re

# Class that handles various aspects of XML parsing.
#----------------------------------------------------------------------------------------
class XMLParser():
    def __init__(self, file):
        self.NSpattern = re.compile('^\{[^}]+\}(.+)$')
        self.filename = file
        self.root = etree.parse(self.filename).getroot()
    
    def setRootname(self, newname):
        oldname = self.cleanupTag(self.root.tag)
        self.root.tag = newname
        return oldname

    def getAllPaths(self):
        result = self.dfswp(self.root, [])
        return result

    def getAllPaths_xsd(self):
        result = self.dfswp_xsd(self.root, [])
        return result

    def getAllTextContent(self):
        result = self.dfstext(self.root)
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
      
    # Does depth first traversal, with path, for XSDs.
    # The method saves the full path of every leaf,
    # and also adds info on minOccurs, maxOccurs and type.
    # Cardinalities is emitted by adding the (sub)path to result
    # if a node has those attributes and also has kids.
    # Returns a list of all levels and leaves with full path.
    def dfswp_xsd(self, node, path):
        result = []
        if node is None:
            return result
        else:
            path.append(self.cleanupTag(node.tag))

        if len(node) == 0:
            if node.text is None:
                nodetext = ''
            else:
                nodetext = node.text    # My XSD parser (parseXSD.py) puts the type information in the text.
            
            result.append('/'.join(path) + ';;' + nodetext)
        else:
            cardinality = ['1','1']
            if 'minOccurs' in node.attrib:
                cardinality[0] = node.attrib['minOccurs']
            if 'maxOccurs' in node.attrib:
                cardinality[1] = node.attrib['maxOccurs']
            result.append('/'.join(path) + ';' + '[' + '->'.join(cardinality) + ']')
            
            for child in node:
                result.extend(self.dfswp_xsd(child, path))
                path.pop()
        
        return result
      
    def findPath(self, xpath):
        return self.root.findall(xpath)
        
    # Does depth first traversal looking for text content of all nodes.
    # Only text content is returned, in a list.
    def dfstext(self, node):
        result = []
        
        if node is None:
            return result
        else:
            if node.text is not None:
                result.append(node.text)

            for child in node:
                result.extend(self.dfstext(child))
            
            return result
