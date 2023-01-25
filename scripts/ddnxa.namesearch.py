import sys
sys.path.insert(1, 'G:\Mine_Opgaver\kode')
from mytools.files.filetools import FileTools

# In order to find out how the IExyz message names map to the CCxyz or CDxyz,
# I made this script.
# The reason is, that the material we were given is a list of IE-messages, i.e. IE513, IE515 etc.
# The actual XSDs where we go to find the fields to incorporate in our schema have names
# such as CC513C and CD411D. If there is 
# In 2 cases, the number part is repeated, i.e. there 


if __name__ == "__main__":
    filename = sys.argv[1] # Name of file containing IE-names that we want from DDNXA.
    pathtoallfiles = sys.argv[2] # Path to the folder with all XSD files from DDNXA.
    
    ft = FileTools()

    msgnames = ft.readFilelines(filename)
    wantedmsgs = []
    for name in msgnames:
        n2 = name.strip()
        if n2.lower().startswith('ie'):
            wantedmsgs.append(n2[2:])
        else:
            wantedmsgs.append(n2)
    
    allfilenames = ft.getFiles(pathtoallfiles, '.xsd')
    allmsgs = {}
    for file in allfilenames:
        path, fname = file.split('\\')
        name,type = fname.split('.')

        if name.lower().startswith('cc') or name.lower().startswith('cd'):
            allmsgs[name[2:5]] = 1
        else:
            allmsgs[name] = 1
    
    for wm in wantedmsgs:
        if wm in allmsgs:
            print(wm, 'found.')
        else:
            print(wm, 'not found.')
    
    for m in allmsgs:
        print(m)