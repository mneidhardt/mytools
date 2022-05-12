import sys
from jsontools import JSONTool

jt = JSONTool()
jsonobj = jt.readJSON(sys.argv[1])
keys = jt.allKeys(jsonobj)

print(len(keys), len(set(keys)))

for key in keys:
    print(key)
