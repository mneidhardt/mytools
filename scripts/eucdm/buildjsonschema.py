import sys
import datetime
import io
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.graph.graphs import EUCDMNode, Graph
from mytools.json.jsontools import EUCDMJSONTool
from mytools.eucdm.patternmatcher import PatternMatcher
from mytools.eucdm.datacatalog import DataCatalog
from mytools.files.filetools import FileTools

def syntax():
    txt = []
    txt.append(sys.argv[0] + ' sg de op')
    txt.append('  sg is the filename containing the serialied graph.')
    txt.append('  de is the filename containing the data elements, their names and formats.')
    txt.append('  op is the prefix for the output file.')
    return "\n".join(txt)

def annotateNodes(nodes, catalog):
    enrichednodes = []
        
    for node in nodes:
        if node[0] == '!':
            enrichednodes.append(node[0])
        else:
            extra = catalog.lookupKey(int(node[0]))
            if extra is None:
                raise ValueError('No node in catalog with key', node[0])
            else:
                enrichednodes.append(EUCDMNode(int(node[0]), extra['elementname'], node[1], node[2], extra['altID'], extra['format'], extra['codelist']))
    return enrichednodes

if __name__ == "__main__":

    try:
        sgfilename = sys.argv[1] # Name of file containing serialised graph.
        datacatalogfilename = sys.argv[2] # Name of file containing the data catalog.
        outputprefix = sys.argv[3] # Prefix for output filename.

        ft = FileTools()
        gtool = Graph()
        jtool = EUCDMJSONTool()
        jtool.setPatternMatcher(PatternMatcher())
    
        nodes = gtool.readSerialisedGraph(sgfilename)       # Read the basic serialised graph.
        catalog = DataCatalog(datacatalogfilename)          # Get the data catalog.
        annotatednodes = annotateNodes(nodes, catalog)  # Annotate nodes with information from the catalog.
        
        graf = gtool.deserialiseGraphLoop(annotatednodes)

        gtool.showGraph(graf)
        
        generatedschema = jtool.buildJSONSchema(graf)
        version = [2,2,0]

        schema = {}
        schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
        version = [str(e) for e in version] # Convert version numbers to strings.
        schema['schemaVersion'] = '.'.join(version)
        schema['title'] = 'DeclarationPayload'
        schema['description'] = 'Created ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        schema['type'] = 'object'
        schema['additionalProperties'] = False
        
        # The generated schema has only basic keys in the root, and I want the ones above here,
        # and I want them at the top, hence the above assignments, and hence I only take 'properties' from the generated schema.
        schema['properties'] = generatedschema['properties']
        
        schemafilename = outputprefix + '.schema.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.json'
        with io.open(schemafilename, 'w', encoding='utf8') as fh:
            fh.write(jtool.dumps(schema))

    except (IndexError, ValueError, NameError) as err:
    # except Exception as err:
        print(str(err))
        print(syntax())
