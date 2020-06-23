import time
from VendApi import *
import CsvUtil as cu
import requests
from datetime import datetime

domain = ''
token = ''

delay = 0.7

api = VendApi(domain, token)

products = api.getProducts()
prodidtoobj = api.getKeyToObjs(products, 'id')
prodtoprocess = []

csvfile = 'all'
prodids = []

if csvfile != 'all':
    prodids = cu.getColumn(csvfile, 'id')
    for pid in prodids:
        prodobj = prodidtoobj.get(pid)

        if prodobj is None:
            print(f"{pid} not found in lookup...")
            continue

        prodtoprocess.append(prodobj)
else:
    prodtoprocess = products

# get the prod objects


print(f'Found {len(prodtoprocess)} products to process...')

failed_ids = ['id']

def getImageIds(product):
    image_ids = []

    images = product['images']

    for i in images:
        currid = i['id']
        image_ids.append(currid)
    
    if len(image_ids) > 0:
        print(f"Returning {len(image_ids)} image ids for {product['id']}...")

    return image_ids


def getAllImageIds(products):
    image_ids = []

    for p in products:
        currimages = getImageIds(p)

        image_ids.extend(currimages)

    
    return image_ids


def deleteImages(image_ids):
    count = 1
    for i in image_ids:
        print(f'Deleting image with id:  {i}...{count}/{len(image_ids)}', end='...')
        resp = api.deleteProdImage(i)

        scode = resp.status_code

        print(scode)

        if scode != 204:
            print(f"Failed on {i}...")
            failed_ids.append(i)

        count += 1
        time.sleep(delay)

        

if __name__ == '__main__':

    allimageids = getAllImageIds(prodtoprocess)

    if len(allimageids) > 0:
        print(f"Starting bulk delete for {len(allimageids)} images...")

        deleteImages(allimageids)
    else:
        print("No images to delete.")

    if len(failed_ids) > 1:
        filename = cu.writeListToCSV(output=zip(failed_ids), title='failedimagedelete', prefix=domain)

        print(f"Saved {len(failed_ids)} failed image ids to {filename}.")



