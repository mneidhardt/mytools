import json

class JSONTool():

    def loads(self, string):
        return(json.loads(string))

    def dumps(self, jsonstructure):
        return(json.dumps(jsonstructure, indent=4))

    def readJSON(self, filename):
        with open(filename) as f:
            return json.load(f)

    # Returns all keys in json object, with duplicates.
    def allKeys(self, json):
        list = []

        for k in json:
            list.append(k)
            if isinstance(json[k], dict):
                list.extend(self.allKeys(json[k]))

        return list

    # Get all elements in JSON structure js.
    # This adds number of grand children if any,
    # and type (of the json element) if none.
    def getChildren(self, js):
        result = []
        for k in js:
            if isinstance(js[k], dict) or isinstance(js[k], list):
                size = str(len(js[k]))
            else:
                size = type(js[k]).__name__
            result.append(k + ' (' + size + ')')
        return result

    # Like findpath, but using recursion.
    # Example path: ['Root', 'Elem2', 'elem3']
    # Returns the structure at json['Root']['Elem2']['Elem3'],
    # if each part of the path is found in json.
    def findPathRecursive(self, json, path):
        if len(path) == 0:
            return json
        elif path[0] in json:
            key = path.pop(0)
            return self.findPathRecursive(json[key], path)
        else:
            return None

    # Similar to findElement, but takes a path as input.
    # Example path: Root/Elem2/elem3
    # Returns the structure at json['Root']['Elem2']['Elem3'],
    # if each part of the path is found in json.
    def findPath(self, json, path):
        names = path.split('/')
        for name in names:
            if name in json:
                json = json[name]
            else:
                return None
        return json

    # Find the dict element(s) with the given name, anywhere in json.
    # elmentname must be a single key in the JSON structure.
    # Returns the structure rooted at that key, if found.
    def findElement(self, json, elementname):
        result = []
        for k in json:
            if isinstance(json[k], dict):
                if k == elementname and 'type' in json[k] and json[k]['type'] == 'object':
                    result.append(json[k])
                    result.extend(self.findElement(json[k], elementname))
                elif k == elementname and 'type' in json[k]:
                    result.append(json[k])
                else:
                    result.extend(self.findElement(json[k], elementname))

        return result

    # Print out all immediate children of a given element in a Schema.
    def printKids(self, sysargv):
        schemafile = sysargv[1]
        parent = sysargv[2]
        jsonobject = self.readJsonfile(schemafile)
        parentobj = self.findElement(jsonobject, parent)
        if parentobj is not None:
            kids = self.getChildren(parentobj)
            print('\n'.join(kids))
        else:
            print('Not found.')


class EUCDMXMLJSONMapperTool(JSONTool):
    # Class specifically made for analysing IExxx vs EUCDM.
    # We were asked to analyse how to merge 'extra' fields from IExxx (described in DDNXA)
    # into the EUCDM, to have a general model.
    # So i'm trying to do that by trying to map each xpath (IExxx is XSD, and EUCDM in our
    # version is JSON) to a path in EUCDM.
    #----------------------------------------------------------------------------
    
    def __init__(self):
        self.namemap = {}
        self.namemap['GoodsItem'] = 'GovernmentAgencyGoodsItem'

    def convDict(self, json):
        result = {}
        for w in json:
            result[self.convert(w)] = w
        return result

    # Normalise words. IExxx use one form and EUCDM another, this hopefully
    # makes it possible to compare/match.
    def convert(self, word):
        return word.rstrip().lower().replace('_', '').replace('-', '').replace('/', '')

    # Similar to findPath, but takes into account that you can meet an array.
    # Example path: [Root, Elem2, Elem3]
    # Returns the structure at json['Root']['Elem2']['Elem3'],
    # if each part of the path is found in json.
    # Args:
    #   json: JSON document (not a Schema)
    #   path: List of elements that form a path, e.g. an XPath.
    def findAnypath(self, json, path):
        for name in path:
            # Get first element, in case current json is a list.
            if isinstance(json, list):
                json = json[0]
                
            if name in self.namemap:
                name = self.namemap[name]
            #if name == 'GoodsItem':
            #    name = 'Government_Agency_Goods_Item'
            
            # Convert keys on this level of the JSON object.
            # Problem example: EUCDM says Goods_Shipment, and IEXXX says GoodsShipment.
            # This tries to solve that.
            convnames = self.convDict(json)
            
            #print('>> ', name, ' in ', list(convnames))
            
            if self.convert(name) in convnames:
                #print('    1 Got', name)
                json = json[convnames[self.convert(name)]]
            elif name in json:
                #print('    2 Got', name)
                json = json[name]
            else:
                return None
                
        return json

        
    # Looks for a given path in a JSON Schema.
    # Takes a string as input, which must use '/' as separator.
    # Example path: Root/Elem2/elem3
    # Returns the structure at json['Root']['Elem2']['Elem3'],
    # if each part of the path is found in json.
    # NB: Not successful. When I overwrite json object as I descend, I'm unable to get back up, e.g. to #/definitions.
    def findSchemapath(self, json, path):
        names = path.split('/')
        for name in names:
            if name not in json:
                if 'type' in json and json['type'] == 'object' and 'properties' in json:
                    if name in json['properties']:
                        print('  Found ', name, 'in properties.')
                        json = json['properties'][name]
                    else:
                        return None
                elif '$ref' in json:
                    refpath = json['$ref'].lstrip('#/').split('/')
                    print(refpath)
                else:
                    return None
            else:
                print('  Found ', name)
                json = json[name]
        return json

class EUCDMJSONTool(JSONTool):

    def __init__(self):
        self.pm = None
        self.setrequired = False    # False if no fields are required, true if all are.

    def setPatternMatcher(self, patternmatcher):
        self.pm = patternmatcher

    #def toCamelCase(self, name):
    #    if name.strip() == '':
    #        return name
    #    if ' ' not in name:
    #        return name
    #    else:
    #        elements = name.split()
    #        result = elements.pop(0).lower()
    #        for e in elements:
    #            result += e.title()
    #        return result

    # I am not sure how to convert all the different names to camel case, consistently,
    # so for the time being, I do this.
    def convertName(self, name):
        return name.replace(' ', '_')

    def buildJSONSchema(self, node):
        if node.getFormat():   # if there is a format, this is not an object.
            restrictions = self.pm.getRestrictions(node.getFormat())

            if node.getMaxCardinality() > 1:
                jsstruct = {}
                jsstruct['description'] = node.getDescription()
                jsstruct['type'] = 'array'
                jsstruct['minItems'] = node.getMinCardinality()
                jsstruct['maxItems'] = node.getMaxCardinality()
                jsstruct['items'] = {}
                for r in restrictions:
                    jsstruct['items'][r[0]] = r[1]
                return jsstruct
            else:
                jsstruct = {}
                jsstruct['description'] = node.getDescription()
                for r in restrictions:
                    jsstruct[r[0]] = r[1]
                return jsstruct
        else:
            if node.getMaxCardinality() > 1:
                jsstruct = {}
                jsstruct['description'] = node.getDescription()
                jsstruct['type'] = 'array'
                jsstruct['minItems'] = node.getMinCardinality()
                jsstruct['maxItems'] = node.getMaxCardinality()
                jsstruct['items'] = {}
                jsstruct['items'] = {}
                jsstruct['items']['type'] = 'object'
                jsstruct['items']['additionalProperties'] = False
                jsstruct['items']['properties'] = {}
                for kid in node.getChildren():
                    jsstruct['items']['properties'][self.convertName(kid.getName())] =  self.buildJSONSchema(kid)

                    if self.setrequired:
                        if 'required' not in jsstruct['items']:
                            jsstruct['items']['required'] = []
                        jsstruct['items']['required'].append(self.convertName(kid.getName()))
                return jsstruct
            else:
                jsstruct = {}
                jsstruct['description'] = node.getDescription()
                jsstruct['type'] = 'object'
                jsstruct['additionalProperties'] = False
                jsstruct['properties'] = {}
                for kid in node.getChildren():
                    jsstruct['properties'][self.convertName(kid.getName())] =  self.buildJSONSchema(kid)

                    if self.setrequired:
                        if 'required' not in jsstruct:
                            jsstruct['required'] = []
                        jsstruct['required'].append(self.convertName(kid.getName()))
                return jsstruct
        
    def buildJSONInstance(self, node):
        if node.getFormat():   # if there is a format, this is not an object.
            restrictions = self.pm.getRestrictions(node.getFormat())

            if node.getMaxCardinality() > 1:
                jsstruct = []
                for i in range(0, min(node.getMaxCardinality(), 2)):
                    jsstruct.append(self.pm.generateSample(node.getFormat()))
                return jsstruct
            else:
                return self.pm.generateSample(node.getFormat())
        else:
            if node.getMaxCardinality() > 1:
                children = {}
                for kid in node.getChildren():
                    children[self.convertName(kid.getName())] = self.buildJSONInstance(kid)
                jsstruct = []
                jsstruct.append(children)
                return jsstruct
            else:
                jsstruct = {}
                for kid in node.getChildren():
                    childobj = self.buildJSONInstance(kid)
                    jsstruct[self.convertName(kid.getName())] = childobj
                return jsstruct
