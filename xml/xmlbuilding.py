import xml.etree.ElementTree as etree
import datetime

# Class that can produce a XML structure.
#----------------------------------------------------------------------------------------
class XMLBuilder():
    def __init__(self, rootname):
        self.newtree = etree.ElementTree()
        self.newxml = etree.Element(rootname)
        self.newxml
        self.newtree._setroot(self.newxml)


    def writeXML(self, filename):
        #newtree.getroot().attrib['xmlns'] = targetNS
        # NB: Default namespace is NOT set, despite various attempts...
        xmlfilename = filename + '.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xml'
        self.newtree.write(xmlfilename, encoding='utf-8', xml_declaration=True)
        #newtree.write(xmlfilename, encoding="utf-8", xml_declaration=True, default_namespace=targetNS)    
        return xmlfilename
    
    def getNewXML(self):
        return self.newxml
        
    # This builds xml from a graph structure.
    # Arg. node is of type mytools.graph.graphs.Graph.
    # Arg. newxml is of type ElementTree.
    def buildXML(self, node, newxml):
        if node is None:
            return

        for child in node.getChildren():
            childxml = etree.SubElement(newxml, child.getName())
            childxml.text = ','.join(child.getAttributes())
            self.buildXML(child, childxml)