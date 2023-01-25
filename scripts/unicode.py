import sys

def writeFile(data, filename,):
    with open(filename, 'w',  encoding='UTF8') as f:
        for element in data:
            f.write(element + '\n')
            
if __name__ == "__main__":
    # Som default forventes at hvert arg er et decimalt tal.
    # Hvis sys.argv[1] == -h, så opfattes alle argumenter som hextal.
    if sys.argv[1] == '-h':
        baseidx = 2
        base = 16
        subscript = chr(int('2081', 16))+chr(int('2086', 16))
    else:
        baseidx = 1
        base = 10
        subscript = chr(int('2081', 16))+chr(int('2080', 16))
        
    codepoints = []
    
    for elm in sys.argv[baseidx:]:
        codepoints.append(elm + subscript + ': ' + chr(int(elm, base)))
    writeFile(codepoints, 'utfChars.txt')