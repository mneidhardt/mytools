import json
import sys

class JSONSchemaParser():
    # Args:
    # filename is the name of the JSON Schema file.
    # refname is the name used as root key for the elements that make up the definitions.
    # I.e. the ones that you can refer to using $ref.
    # Leave empty if your schema does not use $ref.
    def __init__(self, filename):
        self.fullstructure = None   # Full JSON structure.
        self.js = None              # The structure under the top level 'properties'
                                    # This is what I will parse, to avoid going into a possible definition subtree used by $ref.
        
        self.fullstructure = self.readJSON(filename) 
        for k in self.fullstructure:
            if k == 'properties':
                self.js = self.fullstructure[k]

    def readJSON(self, filename):
        with open(filename) as f:
            return json.load(f)

    def parseJSD(self):
        result = self._parseJSD(self.js)
        print(json.dumps(result, indent=4))
    
    # Returns all keys in json object, with duplicates.
    # Currently this uses a json structure to record the result, but should really use a graph structure,
    # e.g. EUCDMNode.
    def _parseJSD(self, js):
        result = {}
        
        for k in js:
            if k == 'properties':
                return self._parseJSD(js[k])
            elif k == 'items':
                return self._parseJSD(js[k])
            elif k in ['description', 'additionalProperties', 'minimum', 'maximum', 'required', 'pattern', 'maxLength', 'minLength', 'maxItems', 'minItems', 'type', 'multipleOf']:
                pass
            elif isinstance(js[k], dict):
                cardinalities = self.getCardinalities(js[k])
                key = k + '/' + str(cardinalities[0]) + '/' + str(cardinalities[1]) # Primitive way of storing cardinalities with the node name.
                result[key] = self._parseJSD(js[k])
            elif k == '$ref':
                refvalue = js[k]
                if refvalue.startswith('#/'):
                    refvalue = refvalue[2:]
                elif refvalue.startswith('/'):
                    refvalue = refvalue[1:]
                    
                # Search for reference in self.fullstructure, which is the full json structure:
                refstruct = self.findPath(self.fullstructure, refvalue)
                return self._parseJSD(refstruct)
            else:
                # I'm not really sure what this is, so just store it with an asterisk.
                result[k] = '*'

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
        return(mincard, maxcard)
        
filename = sys.argv[1]

jp = JSONSchemaParser(filename)

res = jp.parseJSD()

#refvalues = jp.findOccurrences('$ref', jp.js)
#refvalues.sort()
#refvalues = list(set(refvalues))
#refvalues.sort()
#print('\n'.join(refvalues))