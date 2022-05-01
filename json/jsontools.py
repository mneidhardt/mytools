import json
import re
import datetime

class JSONTool():

    def dumps(self, jsonstructure):
        return(json.dumps(jsonstructure))

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

    # Get all elements under a specific key, e.g. 'definitions'.
    def getChildren(self, json):
        result = []
        for k in json:
            result.append(k)
        return result

    # Similar to findElement, but takes a path as input.
    # Example path: Root/Elem2/elem3
    # Returns the structure at json['Root']['Elem2']['Elem3'],
    # if each part of the path is found in json.
    def findPath(self, json, path):
        names = path.split('/')
        for name in names:
            if name not in json:
                return None
            else:
                json = json[name]
        return json

    # Find the element with the given name, anywhere in json.
    # elmentname must be a single key in the JSON structure.
    # Returns the structure rooted at that key, if found.
    def findElement(self, json, elementname):
        element = None
        for k in json:
            if k == elementname and 'type' in json[k] and json[k]['type'] == 'object':
                return json[k]['properties']
            elif isinstance(json[k], dict):
                element = self.findElement(json[k], elementname)
        return element

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

class EUCDMJSONTool(JSONTool):

    def __init__(self):
        self.pm = None

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

            if node.getCardinality() > 1:
                json = {}
                json['description'] = str(node.getKey()) + '. EUCDM format=' + node.getFormat()
                json['type'] = 'array'
                json['maxItems'] = node.getCardinality()
                json['items'] = {}
                for r in restrictions:
                    json['items'][r[0]] = r[1]
                return json
            else:
                json = {}
                json['description'] = str(node.getKey()) + '. EUCDM format=' + node.getFormat()
                for r in restrictions:
                    json[r[0]] = r[1]
                return json
        else:
            if node.getCardinality() > 1:
                json = {}
                json['description'] = str(node.getKey())
                json['type'] = 'array'
                json['maxItems'] = node.getCardinality()
                json['items'] = {}
                json['items'] = {}
                json['items']['type'] = 'object'
                json['items']['additionalProperties'] = False
                json['items']['properties'] = {}
                for kid in node.getChildren():
                    json['items']['properties'][self.convertName(kid.getName())] =  self.buildJSONSchema(kid)
                    if 'required' not in json['items']:
                        json['items']['required'] = []
                    json['items']['required'].append(self.convertName(kid.getName()))
                return json
            else:
                json = {}
                json['description'] = str(node.getKey())
                json['type'] = 'object'
                json['additionalProperties'] = False
                json['properties'] = {}
                for kid in node.getChildren():
                    json['properties'][self.convertName(kid.getName())] =  self.buildJSONSchema(kid)
                    if 'required' not in json:
                        json['required'] = []
                    json['required'].append(self.convertName(kid.getName()))
                return json
        
    def buildJSONInstance(self, node):
        if node.getFormat():   # if there is a format, this is not an object.
            restrictions = self.pm.getRestrictions(node.getFormat())

            if node.getCardinality() > 1:
                json = []
                for i in range(0, min(node.getCardinality(), 2)):
                    json.append(self.pm.generateSample(node.getFormat()))
                return json
            else:
                return self.pm.generateSample(node.getFormat())
        else:
            if node.getCardinality() > 1:
                children = {}
                for kid in node.getChildren():
                    children[self.convertName(kid.getName())] = self.buildJSONInstance(kid)
                json = []
                json.append(children)
                return json
            else:
                json = {}
                for kid in node.getChildren():
                    childobj = self.buildJSONInstance(kid)
                    json[self.convertName(kid.getName())] = childobj
                return json
