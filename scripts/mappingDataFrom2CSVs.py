import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.files.filetools import FileTools

# Creates a dict from parts of the CSV Data, so I can search for the keys.
# Take keycolumn and valuecolumn from csvdata and make them key and value, respectively, in a dict.
def createDict(csvdata, keycolumn, valuecolumn):
    result = {}
    
    for row in csvdata:
        key = row[keycolumn].strip()
        value = row[valuecolumn].strip()
        # print('DICT: ', key, value)
        if key in result:
            raise ValueError('NB: Duplicate key: ', key)
        else:
            result[key] = value
            
    return result
    
    
if __name__ == "__main__":
    # The file containing Emil's xpaths.
    file1 = sys.argv[1]

    # The file containing my xpaths. This will be made into a dict, and then I can search for Emil's paths in it.
    file2 = sys.argv[2]
    
    ft = FileTools()
    csv1 = ft.readCSVFile(file1)
    csv2 = ft.readCSVFile(file2)

    csv2dict = createDict(csv2, 1, 0)
    
    for row in csv1:
        xpath = row[5].strip().replace('[0]', '')
        if xpath in csv2dict:
            print(csv2dict[xpath], xpath)
        else:
            print(xpath, 'not found.')
            