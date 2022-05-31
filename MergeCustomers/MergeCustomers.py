import CsvUtil as cu
from VendApi import *
import time
import JsonUtil as ju
import datetime as dt
import sys, getopt


prefix = ''
token = ''

mergecsv = '.csv'

deletecusts = cu.getColumn(mergecsv, "deleting_customer_code")
mergingcusts = cu.getColumn(mergecsv, "merging_customer_code")

delay = .8

api = VendApi(prefix, token)

print(f"Retrieving customers for {prefix}.vendhq.com...")
customers = api.getCustomers()

custToId = {}

failed_ids = ['customer_id']
failed_sales = ['sale']
failed_codes = ['status_code']
failed_response = ['response']

registers = api.getRegisters('true')
regidlookup = {}

SALE_KEYS_REMOVE = [
    'complete_open_sequence_id',
    'accounts_transaction_id',
    'has_unsynced_on_account_payments'
]

def isDeletedRegister(register_id):
    reg = regidlookup.get(register_id)

    return reg['deleted_at'] is not None

def updateCustomerOnSales(sales, cust_id):

    for s in sales:
        s['register_sale_products'] = s.pop("line_items")
        s['register_sale_payments'] = s.pop("payments")

        s['customer_id'] = cust_id

        print(f"\t...on sale : {s['id']}...", end='\t')

        time.sleep(delay)

        if isDeletedRegister(s['register_id']):
            failed_ids.append(cust_id)
            failed_sales.append(s)
            failed_codes.append('deleted register')
            failed_response.append('cannot merge')
            print("Failed: Deleted register")
            continue
            
        for key in SALE_KEYS_REMOVE:
            s.pop(key)

        resp = api.postSale(s)

        print(resp.status_code)
        # print(resp.json())

        if resp.status_code != 200 and resp.status_code != 201:
            # print(resp.status_code)
            failed_ids.append(cust_id)
            failed_sales.append(s)
            failed_codes.append(resp.status_code)

            response = 'store credit / gift card sale'

            if resp.status_code != 500:
                response = resp.json()
            
            failed_response.append(response)

def mergeCustomers(deleting, merging): 
    
    if len(deleting) != len(merging):
        print("Columns deleting_customer_code and merging_customer_code must be equal.")
        return

    print(f"Merging {len(deleting)} customers...")
    i = 0

    while i < len(deleting):
        delete = deleting[i].strip()
        merge = merging[i].strip()

        print(f"Merging {delete} into {merge} - on {i + 1} / {len(deleting)}...")

        delete_id = custToId.get(delete, None)
        merge_id = custToId.get(merge, None)

        if delete_id is None:
            failed_ids.append(delete)
            failed_sales.append('-')
            failed_codes.append('-')
            failed_response.append(f'Customer with customer_code {delete} does not exist.')

            print(f"{delete} does not exist in {prefix}.")
            i+=1
            continue

        if merge_id is None:
            failed_ids.append(merge)
            failed_sales.append('-')
            failed_codes.append('-')
            failed_response.append(f'Customer with customer_code {merge} does not exist.')

            print(f"{merge} does not exist in {prefix}.")
            i+=1
            continue

        deleteSales = api.getCustomerSales(delete_id)

        updateCustomerOnSales(deleteSales, merge_id)

        i += 1

def createCustToId(custs):
    print(f"Creating code to id lookup for {len(custs)} customers...")
    for c in custs:
        cust_code = c['customer_code']
        cust_id = c['id']

        custToId[cust_code] = cust_id

def createRegIdtoReg(registers):

    for r in registers:
        reg_id = r['id']
        regidlookup[reg_id] = r


if __name__ == '__main__':

    createCustToId(customers)
    createRegIdtoReg(registers)
    mergeCustomers(deletecusts, mergingcusts)

    if len(failed_codes) > 1:
        filename = cu.writeListToCSV(output=zip(failed_ids, failed_sales, failed_codes, failed_response), title="failed_merge", prefix=prefix)
        print(f"Failed merge saved to {filename}.")

