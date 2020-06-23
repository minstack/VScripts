import CsvUtil as cu
import time
import JsonUtil as ju
import datetime as dt
import sys, getopt



customercsv = '.csv'

emailtocodeLookup = {}

code_to_keep = ['merging_customer_code']
code_to_delete = ['deleting_customer_code']

emails = cu.getColumn(customercsv, "email")
cust_codes = cu.getColumn(customercsv, "customer_code")

i = 0

while i < len(emails):
    curr_email = emails[i].lower()
    curr_code = cust_codes[i]

    lookupcode = emailtocodeLookup.get(curr_email)

    if lookupcode is None:
        emailtocodeLookup[curr_email] = curr_code
        i += 1
        continue

    print(f"{lookupcode} to keep, {curr_code} to delete - matched on {curr_email}... {i+1} / {len(emails)}...")
    code_to_keep.append(lookupcode)
    code_to_delete.append(curr_code)

    i+=1


if len(code_to_delete) > 1:
    filename = cu.writeListToCSV(output=zip(code_to_keep, code_to_delete), title=f"mergingcustomer", prefix='')
    print(f"Exported to {filename}.")