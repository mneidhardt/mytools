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
    
    kids = jt.getChildren(js['Declaration'])
    printkids('Declaration:', kids)
    
    kids = jt.getChildren(js['Declaration']['GoodsShipment'])
    printkids('Declaration/GoodsShipment:', kids)
    
    kids = jt.getChildren(js['Declaration']['GoodsShipment']['GovernmentAgencyGoodsItem'][0])
    printkids('Declaration/GoodsShipment/GovernmentAgencyGoodsItem:', kids)

    kids = jt.getChildren(js['Declaration']['MasterConsignment'])
    printkids('Declaration/MasterConsignment:', kids)

    kids = jt.getChildren(js['Declaration']['MasterConsignment']['HouseConsignment'][0])
    printkids('Declaration/MasterConsignment/HouseConsignment:', kids)
    
    kids = jt.getChildren(js['Declaration']['MasterConsignment']['HouseConsignment'][0]['HouseConsignmentItem'][0])
    printkids('Declaration/MasterConsignment/HouseConsignment/HouseConsignmentItem:', kids)
    
    kids = jt.getChildren(js['Declaration']['MasterConsignment']['MasterConsignmentItem'][0])
    printkids('Declaration/MasterConsignment/MasterConsignmentItem:', kids)
    
