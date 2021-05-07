from VendApi import *
from VendApi2 import *
import CsvUtil as cu


domain = 'sungstore'
token = 'KWDZNSo67gRgSGAU3G2vT_IMDDT611m9s40eVisq'

 #the product_id to search for in the inventory endpoint
prod_id = '2598c236-c76c-2a64-4aee-a410a54af7d2'



####################################

api = VendApi(domain, token)
api2 = VendApi2(domain, token)
inventories = api2.getInventories()
outlets = api.getOutlets()
onametoout = api.getKeyToObjs(outlets, 'name')
oidtoout = api.getKeyToObjs(outlets, 'id')

# print(oidtoout)

outtoinventory = {}
onametoinventory ={}

raw_inventory = []


#outlet to inventory record
for inv in inventories:
    curr_pid = inv['product_id']

    if curr_pid != prod_id:
        continue

    raw_inventory.append(inv)

    curr_oid = inv['outlet_id']
    curr_out_name = oidtoout[curr_oid]['name']

    # outtoinventory[f'{curr_out_name}({curr_oid})'] = inv['inventory_level']
    # onametoinventory[curr_out_name] = inv['inventory_level']
    onametoinventory[f'{curr_out_name}({curr_oid})'] = inv['inventory_level']

print("\n\n######################  OUTLET TO INVENTORY MAPPED JSON ######################\n")
print(onametoinventory)
print('\n-------------------------------------\n')
print("\n######################  RAW INVENTORY RECORDS FROM THE /api/2.0/inventory ENDPOINT ######################\n")
print(raw_inventory)
