import time
from VendApi import *
import CsvUtil as cu
import requests
import datetime


domain = ''
token = ''

csvfile = '.csv'

delay= 0.5
api = VendApi(domain, token)

products = api.getProducts()

skus = cu.getColumn(csvfile, 'sku')
handles = cu.getColumn(csvfile, 'handle')
links = cu.getColumn(csvfile, 'image_url')

failedskus = ['sku']
failedhandles = ['handle']
failedlinks = ['image_url']

def getSkuHandleToProdId(products):
    skuhandlemap = {}

    for p in products:
        sku = p['sku']
        handle = p['handle']
        pid = p['id']

        skuhandlemap[f'{sku}{handle}'] = pid

    return skuhandlemap


def getImageFromLink(link):
    return requests.get(link)

def addFailedData(sku, handle, link):
    failedskus.append(sku)
    failedhandles.append(handle)
    failedlinks.append(link)

def uploadImages(skus, handles, links):
    print(f"Starting upload...")
    skuhandletoid = getSkuHandleToProdId(products)
    
    for i in range(len(skus)):
        
        currsku = skus[i]
        currhandle = handles[i]
        currlink = links[i]
        currskuhandle = f"{currsku}{currhandle}"
        pid = skuhandletoid.get(currskuhandle)

        if pid is None:
            print(f"{pid} not found...")
            addFailedData(currsku, currhandle, currlink)
            continue

        print(f"{i + 1} - Getting image from {currlink}", end='...')
        imageresp = getImageFromLink(currlink)

        while imageresp.status_code == 403:
            print(f"Hit 403 forbidden.  Sleeping for an hour...({datetime.datetime.now()})...")
            time.sleep(3600)
            imageresp = getImageFromLink(currlink)
            

        if imageresp.status_code != 200:
            print(f"failed with {imageresp.status_code}...\n")
            addFailedData(currsku, currhandle, currlink)
            continue
        
        time.sleep(delay)

        print(f"success")
        uploadresp = api.uploadImage(pid, imageresp.content)

        if uploadresp.status_code != 201:
            print(f"Uploading image to {pid} failed with {uploadresp.status_code}...\n")
            addFailedData(currsku, currhandle, currlink)
            continue

        respdata = uploadresp.json()['data']

        print(f"Uploaded to {pid} position {respdata['position']}...{respdata['status']}\n")


uploadImages(skus,handles,links)


if len(failedskus) > 1:
    filename = cu.writeListToCSV(output=zip(failedskus, failedhandles, failedlinks), title=f'failed',prefix=domain)
        

        
        

