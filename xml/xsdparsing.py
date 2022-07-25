import os
import re
import sys
import datetime
import xml.etree.ElementTree as etree

#--------------------------------------------------------------------------------------------------
class XSDParser():

    def __init__(self, file):
        self.ns = {
            'default'  : '{http://www.w3.org/2001/XMLSchema}',
            'COAISW01' : 'http://ra.eurodyn.com/importview/COAISW01'
        }
        self.NS = '{http://www.w3.org/2001/XMLSchema}'
        self.NSANNOT = '{http://ra.eurodyn.com/importview/annotations_iv}'
        self.NSSHORT = 'xs'

        # Use the filename without type and spaces as root element name.
        self.rootelementname = os.path.basename(file).split('.')[0]
        self.rootelementname = self.rootelementname.replace(' ', '')

        self.xsdfiles = [file]
        basepath = os.path.dirname(file)
        if len(basepath) == 0:
            basepath = '.'
        self.search4Imports(self.xsdfiles, os.path.basename(file), [basepath])

        # Parse the xsd files, and store their respective roots
        # under the filename.
        self.xsdroots = {}
        for file in self.xsdfiles:
            self.xsdroots[file] = etree.parse(file).getroot()

        self.mainroot = self.xsdroots[self.xsdfiles[0]]

        self.primitivetypes = [self.NSSHORT+':'+x for x in ['string', 'boolean', 'decimal', 'integer', 'float', 'double', 'duration', 'dateTime', 'time', 'date', 'token']]
        self.targetNS = None
        if self.mainroot.tag == self.NS+'schema' and 'targetNamespace' in self.mainroot.attrib:
            self.targetNS = self.mainroot.attrib['targetNamespace']

        etree.register_namespace('', self.targetNS)
    
    def findNS(self):
        for rootkey in self.xsdroots:
            print('XSD:', rootkey)
            for key in self.xsdroots[rootkey].attrib:         # 'key' is the root of the xsd file, and hence has attrib with namespace info.
                print(key, '=', self.xsdroots[rootkey].attrib[key])
            print()
            
    def info(self):
        print('Main xsd: ', self.xsdfiles[0])
        print('All files: ', '\n'.join(self.xsdfiles))
        print('targetNS=' + self.targetNS)

    def start(self):
        self.newtree = etree.ElementTree()
        self.newxml = etree.Element(None)
        self.newtree._setroot(self.newxml)
        
        startelm = self.mainroot.findall('./' + self.NS + 'element')
        print('Found', len(startelm), 'elements in the root. I am using the first one only:', startelm[0].attrib)
        
        childxml = etree.SubElement(self.newxml, startelm[0].attrib['name'])
        childxml.set('creationtime', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"))
        self.parsefile(startelm[0], childxml)
    
    def writeXML(self):
        #newtree.getroot().attrib['xmlns'] = targetNS
        # NB: Default namespace is NOT set, despite various attempts...
        xmlfilename = self.rootelementname + '.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xml'
        self.newtree.write(xmlfilename, encoding='utf-8', xml_declaration=True)
        #newtree.write(xmlfilename, encoding="utf-8", xml_declaration=True, default_namespace=targetNS)
        return xmlfilename

    # This removes namespace part of a tag:
    def cleanupTag(self, tag):
        NSpattern = re.compile('^\{[^}]+\}(.+)$')
        match = NSpattern.match(tag)
        if match:
            return match.group(1)
        else:
            return tag

    # Will replace search4Includes - given 1 file, search for include and import statements,
    # recursively.
    def search4Imports(self, result, file, path=['.']):
        root = etree.parse('/'.join(path + [file])).getroot()
        includes = root.findall('.//' + self.NS + 'include')
        includes += root.findall('.//' + self.NS + 'import')
        
        for inc in includes:
            filefound = inc.attrib['schemaLocation']
            dirnam = os.path.dirname(filefound)
            filenam = os.path.basename(filefound)
            
            fullfname = '/'.join(path+[filefound])
            if fullfname not in result:
                result.append(fullfname)
                if len(os.path.dirname(filefound)) == 0:
                    self.search4Imports(result, filenam, path)
                else:
                    self.search4Imports(result, filenam, path+[dirnam])

    def getType(self, NS, typename):
        typenode = self.search4Type(NS, typename)

        if typenode is None:
            typename = typename.split(':')
            if len(typename) == 2:
                typenode = self.search4Type(NS, typename[1])

        # print('Typename=', typename, typenode)
        return typenode
        
    # Search include files for a given type name.
    # Should I check for duplicate definitions?
    # I use find i.s.o. findall, because the return value suits me:
    # When iterating over this result, I get the children of the found node, where as
    # iterating over the result of findall first goes through the found node itself.
    def search4Type(self, NS, typename):
        for key in self.xsdroots:
            res = self.xsdroots[key].find(NS + 'complexType[@name="' + typename + '"]')
            if res is not None:
                return res
            res = self.xsdroots[key].find(NS + 'simpleType[@name="' + typename + '"]')
            if res is not None:
                return res

        return None

    # Try to find the element pointed to by refname.
    # If 1. attempt fails, remove any namespace and try again.
    def getReference(self, NS, refname):
        refnode = self.search4Reference(NS, refname)
        if refnode is None:
            refname = refname.split(':', maxsplit=1)
            if len(refname) == 2:
                refnode = self.search4Reference(NS, refname[1])

        # print('Refname=', refname, refnode)
        return refnode

    def search4Reference(self, NS, refname):
        # I look for a reference.
        # I assume a ref cannot point to a type, so here I only search for element.
        for key in self.xsdroots:
            res = self.xsdroots[key].findall(NS + 'element[@name="' + refname + '"]')
            if res is not None:
                return res

        return None

    def search4Substitutions(self, NS, groupname):
        # I look for substitution groups.
        for key in self.xsdroots:
            res = self.xsdroots[key].findall('.//' + NS + 'element[@substitutionGroup="' + groupname + '"]')
            if res is not None:
                return res

        return None


    # Just display the root tags:
    def showrootelements(self, node):
        if node is None:
            return

        for child in node:
            if 'name' not in child.attrib:
                if 'ref' not in child.attrib:
                    displayname = 'No name, no ref.'
                else:
                    displayname = child.attrib['ref']
            else:
                displayname = child.attrib['name']
            print(' ---> ' + displayname + ', ' + child.tag)

    # This adds one or more of three constraints as attributes to the XML I'm creating.
    # There are 2 potential sources for this info, hence attribsA and attribsB:
    # Either it comes from the XSD node being examined, or
    # from a ref-node being replaced.
    def addOccurrenceConstraints(self, xmlnode, attribs, inheritedattribs={}):
        for attr in ['minOccurs', 'maxOccurs', 'nillable']:
            if attr in attribs:
                xmlnode.set(attr, attribs[attr])
            if attr in inheritedattribs:    # Unsure whether to use if or elif here.
                xmlnode.set(attr, inheritedattribs[attr])

    def parsefile(self, node, newxml, indent='', inheritedattribs={}):
        if node is None:
            return

        # child here refers to a child node of the XSD.
        # childxml below is the current node of the XML being produced.
        for child in node:
            if child.tag == self.NS+'element' and 'ref' in child.attrib:
                # Replace the current node with the referenced node.
                refchild = self.getReference(self.NS, child.attrib['ref'])
                if len(refchild) > 1:
                    print(indent, 'Found more than one node reference by this name:', child.attrib['ref'])
                    sys.exit(0)
                print(indent, 'Ref node', child.attrib['ref'], 'replaced by:', refchild[0].tag, refchild[0].attrib)
                self.parsefile(refchild, newxml, indent, child.attrib)
            elif child.tag == self.NS+'element':
                if 'name' not in child.attrib and 'ref' not in child.attrib:
                    print(child.tag, child.attrib, '"name" and "ref" missing.')
                    continue
                
                if 'type' in child.attrib and child.attrib['type'] in self.primitivetypes:
                    childxml = etree.SubElement(newxml, child.attrib['name'])
                    childxml.set('primitivetype', child.attrib['type'])
                    self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                elif 'type' in child.attrib:
                    typenode = self.getType(self.NS, child.attrib['type'])
                    childxml = etree.SubElement(newxml, child.attrib['name'])
                    self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                        
                    if typenode is not None:
                        self.parsefile(typenode, childxml, indent+'  ')

                    # Even if element is defined in a complex or simple type, there may be more to parse after that.
                    self.parsefile(child, childxml, indent+'  ')
                elif 'abstract' in child.attrib and child.attrib['abstract'].lower() == 'true':
                    # If element is abstract, look for substitutions.
                    subs = self.search4Substitutions(self.NS, child.attrib['name'])
                    self.parsefile(subs, newxml, indent+'  ')
                    # Here, I dont want to look for minOccurs,maxOccurs etc. as the childxml is not made here.
                else:
                    childxml = etree.SubElement(newxml, child.attrib['name'])
                    self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                    self.parsefile(child, childxml, indent+'  ')

            elif child.tag == self.NS+'restriction':
                if 'restrictionbase' in newxml.attrib:
                    print('In restrictionbase, replacing ', newxml.attrib['restrictionbase'], 'with', child.attrib['base'])
                newxml.set('restrictionbase', child.attrib['base'])
                type = self.getType(self.NS, child.attrib['base'])
                if type is not None:
                    self.parsefile(type, newxml, indent+'  ')
                self.parsefile(child, newxml, indent+'  ')
            elif child.tag in [self.NS+'minLength', self.NS+'maxLength', self.NS+'pattern']:
                newxml.set(self.cleanupTag(child.tag), child.attrib['value'])
            elif child.tag == self.NSANNOT+'autocompletebox':
                print(indent, 'Got autocompletebox in', child.attrib['name'])
                newxml.set('autocompletebox', child.attrib['name'])
            elif child.tag == self.NS+'documentation':
                newxml.text = child.text
                self.parsefile(child, newxml, indent+'  ')
            elif child.tag == self.NS+'attribute' and 'name' in child.attrib:
                newxml.set('hasAttribute', child.attrib['name'])
            else:
                self.parsefile(child, newxml, indent+'  ')

###############################

# This produces a full XML-file with all elements given in a Schema definition.
# NB: All choices are included, so the resulting XML is not necessarily valid.
# Also handles abstract nodes, i.e. finds substitution nodes.
# Adds several bits of data as attributes, incl. minOccurs and maxOccurs to element, and the restrictions, maxlength, minlength and pattern, if any.
# I.e. given a primary XSD, which may include other XSD files, this will search for all elements and their descriptions.

# Takes 1 arg, the filename of the primary XSD file to use.
# I This will be searched for any other include statements.
#
# Assumptions:
# At the moment, I expect all includes to refer to files in the same directory as the primary XSD.
# The primary XSD is searched for include statements, and if any found, they are searched recursively.
# The filename (without type) of the primary XSD is used as the filenameof the output file, with XML as type.
#
#
# NB: As this does not really handle namespaces, be careful when parsing composite XSDs, (i.e. ones containing 
# schemas for different namespaces). That may produce errors.
# In stead, parse the XSDs individually.