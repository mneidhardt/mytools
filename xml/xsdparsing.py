import os
import re
import sys
import datetime
import xml.etree.ElementTree as etree

#--------------------------------------------------------------------------------------------------
class XSDParser():

    def __init__(self, file):
        self.ns = {
            'xsd'  : '{http://www.w3.org/2001/XMLSchema}',
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
    
    # Extract namespaces from a string of xml data.
    # Returns a dict with keys = shortform and value = namespace.
    def extractNamespaces(self, data):
        p0 = re.compile('(<[^>]+>)')
        p1 = re.compile('.*xmlns="([^"]+)".*', re.IGNORECASE)
        p2 = re.compile('.*xmlns:([^=]+)="([^"]+)".*', re.IGNORECASE)
        
        result = {}
        
        m0 = p0.findall(data)
        for element in m0:
            m1 = p1.match(element)
            if m1:
                result[None] = m1.group(1)
                
            m2 = p2.findall(element)
            for hit2 in m2:
                result[hit2[0]] = hit2[1]
        return result
        
    def findNS(self):
        nsmap = {}
        for filename in self.xsdfiles:
            with open(filename) as f:
                data = f.read()
                data = data.replace('\r\n', ' ').replace('\n', ' ')
            nsmap[filename] = self.extractNamespaces(data)
                        
    def info(self):
        print('Main xsd: ', self.xsdfiles[0])
        print('All files: ', '\n'.join(self.xsdfiles))
        print('targetNS=' + self.targetNS)

    def start(self):
        self.newtree = etree.ElementTree()
        self.newxml = etree.Element(None)
        self.newtree._setroot(self.newxml)
        
        startelm = self.mainroot.findall('./' + self.NS + 'element')
        if len(startelm) > 1:
            print('Found', len(startelm), 'elements in the root. I am using the first one only:', startelm[0].attrib)
        elif len(startelm) == 1:
            print('Found 1 element in the root.')
        else:
            print('Found no elements in the root. Exiting.')
            sys.exit(0)
            
        # Handle situation where the top level element has a type but no child elements.
        # E.g. if top element looks like this:
        # <xs:element name="CC525C" type="CC525CType" />
        # Then I replace it with the type node, so that the main method (generateSample) can just go through the children.
        if len(startelm[0]) == 0 and 'type' in startelm[0].attrib and startelm[0].attrib['type'] not in self.primitivetypes:
            startnode = self.getType(self.NS, startelm[0].attrib['type'])
        else:
            startnode = startelm[0]
        
        childxml = etree.SubElement(self.newxml, startelm[0].attrib['name'])
        childxml.set('creationtime', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"))
        self.generateSample(startnode, childxml)
    
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
        # This program is not really namespace aware, so perhaps I should ignore import statements?
        
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


    # Try to find the entity (element or group) pointed to by name.
    # If 1. attempt fails, remove any namespace and try again.
    def getEntity(self, NS, entity, name):
        node = self.search4Entity(NS, entity, name)
        if node is None:
            name = name.split(':', maxsplit=1)
            if len(name) == 2:
                node = self.search4Entity(NS, entity, name[1])

        return node

    def search4Entity(self, NS, entity, name):
        # I look for an entity such as element or group.
        # I assume an entity cannot point to a type.
        for key in self.xsdroots:
            res = self.xsdroots[key].findall(NS + entity + '[@name="' + name + '"]')
            if res is not None and len(res) > 0:
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
    # There are 2 potential sources for this info, hence attribs and inheritedattribs:
    # Either it comes from the XSD node being examined, or
    # from a ref-node being replaced. The former takes precedence, so it is processed last.
    def addOccurrenceConstraints(self, xmlnode, attribs, inheritedattribs={}):
        for attr in ['minOccurs', 'maxOccurs', 'nillable']:
            if attr in inheritedattribs:
                xmlnode.set(attr, inheritedattribs[attr])
            if attr in attribs:
                xmlnode.set(attr, attribs[attr])

    def generateSample(self, node, newxml, indent='', inheritedattribs={}):
        if node is None:
            return

        # child here refers to a child node of the XSD.
        # newxml/childxml is the parent/child node of the XML being produced.
        for child in node:
            if child.tag == self.NS+'element' and 'ref' in child.attrib:
                # Replace the current node with the referenced node.
                refchild = self.getEntity(self.NS, 'element', child.attrib['ref'])
                if len(refchild) == 0:
                    print(indent, 'Fatal: Found no node reference by this name:', child.attrib['ref'], '. Could be namespace related.')
                    sys.exit(0)
                elif len(refchild) > 1:
                    print(indent, 'Fatal - found more than one node reference by this name:', child.attrib['ref'])
                    sys.exit(0)
                print(indent, 'Ref node', child.attrib['ref'], 'replaced by:', refchild[0].tag, refchild[0].attrib)
                self.generateSample(refchild, newxml, indent, child.attrib)
            elif child.tag == self.NS+'group' and 'ref' in child.attrib:
                groupdef = self.getEntity(self.NS, 'group', child.attrib['ref'])
                if len(groupdef) == 0:
                    print(indent, 'Fatal: Found no group definition.')
                    sys.exit(0)
                else:
                    childxml = etree.SubElement(newxml, child.attrib['ref'])
                    self.generateSample(groupdef, childxml, indent, child.attrib)
            elif child.tag == self.NS+'element' and 'type' in child.attrib and child.attrib['type'] in self.primitivetypes:
                childxml = etree.SubElement(newxml, child.attrib['name'])
                childxml.set('primitivetype', child.attrib['type'])
                self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                self.generateSample(child, childxml, indent+'  ')
            elif child.tag == self.NS+'element' and 'type' in child.attrib:
                typenode = self.getType(self.NS, child.attrib['type'])
                childxml = etree.SubElement(newxml, child.attrib['name'])
                self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                if typenode is not None:
                    self.generateSample(typenode, childxml, indent+'  ')
                # Even if element is defined in a complex or simple type, there may be more to parse after that.
                self.generateSample(child, childxml, indent+'  ')
            elif child.tag == self.NS+'element' and 'abstract' in child.attrib and child.attrib['abstract'].lower() == 'true':
                # If element is abstract, look for substitutions.
                print('Got ABSTRACT: inheritedattribs=', list(inheritedattribs))
                subs = self.search4Substitutions(self.NS, child.attrib['name'])
                self.generateSample(subs, newxml, indent+'  ', inheritedattribs)
                # Here, I dont want to look for minOccurs,maxOccurs etc. as the childxml is not made here.
            elif child.tag == self.NS+'element':
                childxml = etree.SubElement(newxml, child.attrib['name'])
                self.addOccurrenceConstraints(childxml, child.attrib, inheritedattribs)
                self.generateSample(child, childxml, indent+'  ')
            elif child.tag == self.NS+'restriction':
                #if 'restrictionbase' in newxml.attrib:
                #    print(indent, 'In restrictionbase, replacing ', newxml.attrib['restrictionbase'], 'with', child.attrib['base'])
                newxml.set('restrictionbase', child.attrib['base'])
                type = self.getType(self.NS, child.attrib['base'])
                if type is not None:
                    self.generateSample(type, newxml, indent+'  ')
                self.generateSample(child, newxml, indent+'  ')
            elif child.tag in [self.NS+'minLength', self.NS+'maxLength', self.NS+'pattern']:
                newxml.set(self.cleanupTag(child.tag), child.attrib['value'])
            elif child.tag == self.NSANNOT+'autocompletebox':
                print(indent, 'Got autocompletebox in', child.attrib['name'])
                newxml.set('autocompletebox', child.attrib['name'])
            elif child.tag == self.NS+'documentation':
                newxml.text = child.text
                self.generateSample(child, newxml, indent+'  ')
            elif child.tag == self.NS+'attribute' and 'name' in child.attrib:
                if 'hasAttribute' not in newxml.attrib:
                    newxml.set('hasAttribute', child.attrib['name'])
                else:
                    tmpattr = newxml.attrib['hasAttribute']
                    newxml.set('hasAttribute', tmpattr+';'+child.attrib['name'])
            else:
                self.generateSample(child, newxml, indent+'  ')

###############################

# This generates a sample XML-file with all elements given in a Schema definition.
# NB: All choices are included, so the resulting XML is not necessarily valid.
# Also handles abstract nodes, i.e. finds substitution nodes.
# Adds several bits of data as attributes, incl. minOccurs and maxOccurs to element, and the restrictions, maxlength, minlength and pattern, if any.
# I.e. given a primary XSD, which may include other XSD files, this will search for all elements and their descriptions.

# Takes 1 arg, the filename of the primary XSD file to use.
# I This will be searched for any include and import statements.
#
# Assumptions:
# At the moment, I expect all includes to refer to files in the same directory as the primary XSD.
# The primary XSD is searched for include statements, and if any found, they are searched recursively.
# The filename (without type) of the primary XSD is used as the filenameof the output file, with XML as type.
#
#
# NB: As this does not really handle namespaces, be careful when parsing composite XSDs, (i.e. ones containing 
# schemas for different namespaces). That may produce errors.
# In stead, you may be able to parse the XSDs individually.