import json
import sys


# Some tools for JSON Schema.
#-------------------------------------------------------------------------
class JSONSearchTools():

    def readJsonfile(self, filename):
        with open(filename) as f:
            return json.load(f)

        
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


if __name__ == "__main__":
    jt = JSONSearchTools()
    jt.printKids(sys.argv)
    #jsonobject = jt.readJsonfile(sys.argv[1])
    #elem = jt.findPath(jsonobject, sys.argv[2])
    #if elem is None:
    #    print('Not found.')
    #else:
    #    for key in elem:
    #        print(key)