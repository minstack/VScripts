# Scripts

## Python 3
Mac will have Python 2 installed but the scripts will need at least Python 3.7.
Please download and install at https://www.python.org/ftp/python/3.8.3/python-3.8.3-macosx10.9.pkg

All commands will be in the format:

  `python3 {script_name.py}`

## Install `requests`
All scripts uses the requests library. After installing python3, please install `requests`
1. Open terminal
2. `pip3 install requests`

## Hardcoding Values
Due to these scripts being written as needed with time constraints, there hasn't been any type of interface added.  Values will need to be hardcoded which will be at the top of the files.

These will be named along the lines of
- `prefix`/`domain`
- `token`
- `csv` / `csvfile`


## ReversionConsignmentProducts
This will version the consignment products that don't return on /api/2.0/consignments/{consignment_id/products due to missing versions.
- Results will be outputted in JSON format
- Exports successful payloads and Errored payloads (in the same directory)
  - This is just in case there are any issue
  - No issues have surfaced so far

### Usage
1. A CSV file with an `id` column with all the consignment_ids (**not** consignment products)
2. Open ReversionConsginmentProducts.py
  1. Update the values for `prefix`, `token` and `csvfile`
  2. Save
3. `python3 ReversionConsginmentProducts.py`

## imageupload_sm
Only to be used if vendcli is not working as expected.  This was written because Google Drive seems to respond with 403 after a certain amount of downloads (maybe number of times or total bandwidth?).
The window _seems_ to be an hour.  
- This script will sleep for an hour after it hits a 403 and resumes until finished
- The CSV format is the same as vendcli (`sku`, `handle`, `image_url`)
- Any errored skus will export a CSV to the desktop

### Usage
1. Open image_upload_sm.py
2. Update the values for `domain`, `token` and `csvfile`
3. Save
4. `python3 image_upload_sm.py`

## DeleteImages
This was built to delete images due to the loading image from a bad import.
- Delete all product images
- Delete specified product images by product ID
- Exports any failed uploads as CSV to desktop

### Usage
1. Open DeleteImages.py
2. Update the values for `domain`, `token` and `csvfile`
      - `csvfile` should either be `all` for deleting all images or the CSV filename with specified product IDs
      - The CSV file should have an `id` column with product IDs and not the image ID
      - The CSV file must be in the same directory as the script if you only provide the CSV filename
      - Fullpath is required if you don't have the file in the same directory
3. Save
4. `python3 DeleteImages.py`

## MergeCustomers
This will 'merge' customers based on duplicate **emails**. Merging in this case is to 'move' sales from one (duplicate) customer to the other by updating the customer on the sale of the duplicate customer.
- This will move the loyalty based on the sales being moved

Sales cannot be 'moved' if:
- The sale involves some gift card, store credit or loyalty transaction
- The sale is made under a deleted register
- The sale is `ONACCOUNT_CLOSED` linked to accounting (Xero, QBO etc.)

When the duplicate customer is deleted, those sales will ultimately have an "Anonymous Customer" on the sale.

**_NOTE_: Do it in batches if possible and let the script finish in order to get the failed merge CSV exported to your desktop with the details**

### Usage
**_NOTE_: ExportDupeCustomerCodes can be skipped if you already have a CSV with `merging_customer_code` and `deleting_customer_code` columns. That can be used directly on MergeCustomers.**
- `merging_customer_code` are the customer records to keep
- `deleting_customer_code` are the customer records to move the sales to the above, corresponding customer record
  - these are not deleted by the script, just a misleading name

#### ExportDupeCustomerCodes
1. Open the customer CSV
2. Filter for non-empty emails
3. Save-as another CSV
4. Sort by
      - `email` ascending
      - `year_to_date` descending
      - `loyalty_balance` descending
      - **This is because it will take the first one seen as the 'original' to keep and anything that follows to be the 'duplicate'**
5. Save 
6. Open ExportDupeCustomerCodes.py
7. Update `customercsv` to the CSV prepared in **steps 4-5**
8. Save
9. `python3 ExportDupeCustomerCodes.py`
10. CSV exports to desktop

#### MergeCustomers
1. Move exported CSV above in **step 10** to script directory
      - will need full path in **step 3** if not moved.
2. Open MergeCustomers.py
3. Update the values for `prefix`, `token` and `csvfile`
      - `csvfile` from **step 1**
4. Save
5. `python3 MergeCustomers.py`
6. Failed sales to move are exported in CSV to desktop with sale payload and status code
      - these are for reference but usually nothing can be done due to the caveat above (sc/gc/loyalty)

## Inventory Record Lookup by `product_id`
For cases where developers report that `/api/2.0/inventory` does not return inventory records for a specific product or "there are missing inventory records".  Most likely, they haven't used version pagination properly and haven't pulled all the inventory records as a result.

### Usage
1. Open `inventory_records.py`
2. Update the values for `domain`, `token` and `prod_id`
      - Where `prod_id` is the `product_id` the developers are claiming to have missing inventory records
3. Save
4. `python3 inventory_records.py`
5. The script will output 2 results that can be provided to the developer after 'prettifying' it with a JSON formatter of your choice.
    1. `OUTLET TO INVENTORY MAPPED JSON` follows with a filtered object where the outlet name and id are mapped to their current inventory levels
    2. `RAW INVENTORY RECORDS FROM THE /api/2.0/inventory ENDPOINT` follows with an array of inventory records from the inventory endpoint as-is.  It'll be what they should be seeing without any processed data from the endpoint.
