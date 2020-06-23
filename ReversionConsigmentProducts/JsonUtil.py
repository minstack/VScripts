import json
#from pandas.io.json import json_normalize

'''
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
'''
def writeJsonToFile(data, filename):

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def loadJsonListFiles(files):
    objs= []

    for file in files:
        with open(file) as f:
            data = json.load(f)
            objs.extend(data)


    return objs

def loadJsonFile(file):
    data = None

    with open(file) as f:
        data = json.load(f)



    return data

'''
data = loadJsonFile('melbourneutdmerch_errored-sale-repostsuccess.json')[0]
flat = flatten_json(data)
normalized = json_normalize(flat)

normalized.to_csv('test.csv')
'''