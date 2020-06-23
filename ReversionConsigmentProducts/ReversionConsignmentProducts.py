import CsvUtil as cu
from VendApi import *
import time
import JsonUtil as ju
import datetime as dt


prefix = ''
token = ''
csvFile = '.csv'
column = 'id'

consignments = cu.getColumn(csvFile, column)
api = VendApi(prefix, token)

errored = []
errored_response = []

def getConsignmentProducts(id):
    result = api.getConsigmentProducts(id)
    #print(result)
    
    return result

def reversion(getObj):
    return api.reversionConsigmentProducts(getObj)

def reversionsProducts(cons_prods, results, errored):

    for cp in cons_prods:
        #print(cp)
        result = reversion(cp)
        print(result)

        status = result.status_code

        if status != 200:
            errored.append(result.json())
            continue
        
        results.append(result.json())

def outputResultsToJson(results, prefixtitle):
    if len(results) == 0:
        return
        
    currdate = dt.datetime.now()
    outputdate = currdate.strftime('%Y-%m-%dT%H:%M:%S')
    ju.writeJsonToFile(results, f'{prefixtitle}-{prefix}{outputdate}.json')


cons_prods = []
#print(consignments, cons_prods)
for c in consignments:
    cons_prods.extend(getConsignmentProducts(c))

outputResultsToJson(cons_prods, 'original')

print(len(cons_prods))
results = []
errored = []

reversionsProducts(cons_prods, results, errored)

outputResultsToJson(results, 'success')
outputResultsToJson(errored, 'errored')