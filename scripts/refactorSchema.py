import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.json.jsontools import JSONTool

def printkids(path, kids):
    print(path)
    #for k in sorted(kids, key=str.casefold):
    for k in kids:
        print('  ',k)
    print()

if __name__ == "__main__":
    filename = sys.argv[1] # Name of file containing JSON Structure.

    jt = JSONTool()
    js = jt.readJSON(filename)
    
    ps = js['definitions']['ProcessingStatus']
    del js['definitions']['ProcessingStatus']

    cd = js['definitions']['CustomsDebt']
    del js['definitions']['CustomsDebt']

    dp = js['definitions']['DeclarationPayload']
    del js['definitions']['DeclarationPayload']

    js['$defs'] = {}
    js['$defs']['ProcessingStatus'] = ps
    js['$defs']['CustomsDebt'] = cd
    js['$defs']['DeclarationPayload'] = dp
    
    print(jt.dumps(js))