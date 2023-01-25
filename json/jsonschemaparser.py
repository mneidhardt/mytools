import json
import sys
import os

# Class that can parse a JSON Schema. I'm not entirely certain that this is correct,
# and furthermore, it is in some ways tailored specifically to read JSON Schemas for
# EUCDM (e.g. when finding description for a field).
class JSONSchemaParser():
    # Args:
    # filename is the name of the JSON Schema file.
    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.dirname(filename)
        self.nodeclass = None       # Node class, in case the result should be stored a node class, rather than JSON structure.
        self.fullstructure = None   # Full JSON structure.
        self.js = None              # The structure under the top level 'properties' This is what I will parse,
                                    # to avoid going into a subtree used by $ref. This might not be present, but if it is,
                                    # it should not be processed independently.
        
        self.fullstructure = self.readJSON(filename) 

        for k in self.fullstructure:
            if k == 'properties':
                self.js = self.fullstructure[k]

        self.keywords = ['enum', 'description', 'additionalProperties', 'minimum', 'maximum', 'required', 'pattern', 'maxLength', 'minLength', 'maxItems', 'minItems', 'type', 'multipleOf']

    def setNodeclass(self, nodeclass):
        self.nodeclass = nodeclass

    def readJSON(self, filename):
        with open(filename) as f:
            return json.load(f)

    def parseJSD(self):
        result = self._parseJSD(self.js)
        return result
    
    # Returns all keys in json object, with duplicates.
    # Currently this uses a json structure to record the result, but should really use a graph structure,
    # e.g. EUCDMNode.
    def _parseJSD(self, js):
        if isinstance(js, dict):
            result = {}
            
            for k in js:
                if k in ['properties', 'items']:
                    return self._parseJSD(js[k])
                elif isinstance(js[k], dict):
                    cards = self.getCardinalities(js[k])
                    descr = self.getDescription(js[k]).replace('>', '#62')
                    key = '>'.join([k]+[descr]+cards)# Primitive way of storing name, description and cardinalities as the key.
                    result[key] = self._parseJSD(js[k])
                elif k in self.keywords:
                    pass
                    #result[k] = js[k]
                elif k == '$ref':
                    refvalue = js[k].lstrip(' #')
                    if refvalue.startswith('/'):
                        refvalue = refvalue[1:]
                        # Search for reference in self.fullstructure, which is the full json structure:
                        refstruct = self.findPath(self.fullstructure, refvalue)
                        result = self._parseJSD(refstruct)
                    elif refvalue.startswith('file:'):
                        refvalue = refvalue[4:]
                        refvalue = self.path + '/' + refvalue.lstrip(':/')
                        result = self._parseJSD(self.readJSON(refvalue))
                else:
                    result[k] = self._parseJSD(js[k])
        elif isinstance(js, list):
            result = []
            for i in range(len(js)):
                result.append(self._parseJSD(js[i]))
        else:
            result = None # { js: 'Nuffink' }

        return result

        
    # Look for the given key in all of jsonstruct.
    # Returns list of all the corresponding values.
    # Intended to work with finding string values, e.g. 
    # the vlues for key '$ref'.
    def findOccurrences(self, key, jsonstruct):
        list = []

        for k in jsonstruct:
            if k == key and isinstance(jsonstruct[k], str):
                list.append(jsonstruct[k])
            elif isinstance(jsonstruct[k], dict):
                list.extend(self.findOccurrences(key, jsonstruct[k]))

        return list
    
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

    def getCardinalities(self, jsonstruct):
        mincard = 1
        maxcard = 1
        
        if 'type' in jsonstruct and jsonstruct['type'] == 'array':
            if 'minItems' in jsonstruct:
                mincard = jsonstruct['minItems']
            if 'maxItems' in jsonstruct:
                maxcard = jsonstruct['maxItems']
        return [str(mincard), str(maxcard)]

    def getDescription(self, jsonstruct):
        if 'description' in jsonstruct:
            return jsonstruct['description']
        elif '$ref' in jsonstruct:
            return self.getDescriptionInReference(jsonstruct['$ref'])
        elif 'items' in jsonstruct and '$ref' in jsonstruct['items']:
            return self.getDescriptionInReference(jsonstruct['items']['$ref'])
        else:
            return ''

    def getDescriptionInReference(self, jref):
        if jref.startswith('#/'):
            refvalue = jref[2:]
            refstruct = self.findPath(self.fullstructure, refvalue)
            if 'description' in refstruct:
                return refstruct['description']
            else:
                return ''
        else:
            return ''

if __name__ == "__main__":
    filename = sys.argv[1]

    jp = JSONSchemaParser(filename)

    res = jp.parseJSD()
    print(json.dumps(res, indent=4))
