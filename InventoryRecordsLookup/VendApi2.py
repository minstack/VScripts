import requests, json, uuid, time

class VendApi2:
    """
        Basic VendApi Class that has the functionality to call and return
        the objects of the corresponding types (customers, sales).
        Will need to add on to the class for others if needed.

        Author: Sung Min Yoon
    """

    __BASE_URL = "https://{0}.vendhq.com/"
    __ENDPOINTS = {
        "cust" : "api/2.0/customers",
        "search" : "api/2.0/search",
        "sales" : "api/2.0/sales",
        "outlets" : "api/2.0/outlets",
        "products2.0" : "api/2.0/products",
        "products0.9" : "api/products",
        "delProd" : "api/products",
        "registers" : "api/2.0/registers",
        "stockorders" : "api/consignment",
        "consignmentProduct" : "api/consignment_product",
        "channels" : "api/2.0/channels",
        "inventory" : "api/2.0/inventory",
        "tags" : "api/2.0/tags",
        "getSuppliers" : "api/2.0/suppliers",
        "postSupplier" : "api/supplier",
        "register_sales" : "api/register_sales",
        "oldcust" : "api/customers",
        "storecreditlist" : "api/2.0/store_credits"
    }

    __domain = ''
    __headers = {"Authorization" : "", "User-Agent" : "Python 3.7/Vend-Support-Tool"}
    __prefix = ''

    def __init__(self, prefix, token):
        """
            Constructor to set the provided prefix and token of the store to
            work with.
        """
        self.__domain = self.__BASE_URL.format(prefix)
        self.__headers["Authorization"] = "Bearer " + token
        self.__prefix = prefix

    def deleteStockOrder(self, id):
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['stockorders'], id), headers=self.__headers)

    def createStoreCreditTransaction(self, cust_id, trans_type, amount, notes=None, user_id=None):
        url = f"{self.__domain}{self.__ENDPOINTS['storecreditlist']}/{cust_id}/transactions"

        client_id = str(uuid.uuid1())

        payload = {
            "amount" : float(amount),
            "type" : trans_type,
            "notes" : notes,
            "user_id" : user_id,
            "client_id" : client_id
        }

        headers = {"Content-Type" : "application/json"}

        headers.update(self.__headers)

        # print(payload)
        resp = requests.post(url, headers=headers, data=json.dumps(payload))

        return resp

    def createCustomer(self, payload):
        url = f"{self.__domain}{self.__ENDPOINTS['cust']}"
        # print(url)

        return requests.post(url, headers=self.__headers, data=json.dumps(payload))

    def reverseStoreCredit(self, cust_id, amount, notes=None, user_id=None):
        return self.createStoreCreditTransaction(cust_id, "REVERSE", -amount, notes, user_id)

    def issueStoreCredit(self, cust_id, amount, notes=None, user_id=None):
        return self.createStoreCreditTransaction(cust_id, "ISSUE", amount, notes, user_id)

    def redeemStoreCredit(self, cust_id, amount, notes=None, user_id=None):
        return self.createStoreCreditTransaction(cust_id, "REDEMPTION", -amount, notes, user_id)
    

    def getStoreCreditList(self):
        url = f"{self.__domain}{self.__ENDPOINTS['storecreditlist']}"
        resp = requests.get(url, headers=self.__headers)

        # print(resp.json())

        if resp.status_code != 200:
            return None

        return resp.json()['data']

    def postOldCustomers(self, payload):
        url = f"{self.__domain}{self.__ENDPOINTS['oldcust']}"
        resp = requests.post(url, data=json.dumps(payload), headers=self.__headers)

        return resp

    def adjustCustomerLoyalty(self, id, value):
        payload = {
            "id" : id,
            "loyalty_adjustment" : value
        }

        return self.postOldCustomers(payload)

    def deleteCustomer(self, id):
        """
            Deletes a customer based on the provided ID. Returns the status code
            of the response.

            204: Successfully deleted
            500: Could not delete because of customer attached to open sale(s)
            404: No such customer exists to delete.
        """
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['cust'], id), headers=self.__headers)

    def getSale2(self, id):
        url = f"{self.__domain}{self.__ENDPOINTS['sales']}/{id}"
        resp = requests.request("GET", url, headers=self.__headers)

        return resp

    def getSale09(self, id):
        url = f"{self.__domain}{self.__ENDPOINTS['register_sales']}/{id}"
        resp = requests.request("GET", url, headers=self.__headers)

        return resp

    def postSale(self, payload):
        url = f"{self.__domain}{self.__ENDPOINTS['register_sales']}"

        resp = requests.post(url, data=json.dumps(payload), headers=self.__headers)

        return resp

    def getAllTags(self):
        return self.__getRequest__(url=f"{self.__domain}{self.__ENDPOINTS['tags']}")

    def getAllSuppliers(self, deleted=False):
        return self.__getRequest__(url=f"{self.__domain}{self.__ENDPOINTS['getSuppliers']}", params={"deleted": deleted})

    def createUpdateSupplier(self, payload):
        url = f"{self.__domain}{self.__ENDPOINTS['postSupplier']}"
        return requests.post(url, data=json.dumps(payload), headers=self.__headers)

        
    def addConsignmentProductReceived(self, consignmentId, productId, count, cost):
        url = f"{self.__domain}{self.__ENDPOINTS['consignmentProduct']}"
        payload = {
            "consignment_id" : consignmentId,
            "product_id" : productId,
            "count" : count,
            "received" : count,
            "cost" : cost
        }

        return requests.post(url, data=json.dumps(payload), headers=self.__headers)

    def createStockOrder(self, outletid, name):
        url = f"{self.__domain}{self.__ENDPOINTS['stockorders']}"
        payload = {
            "name" : name,
            "outlet_id" : outletid,
            "status" : "OPEN",
            "type" : "SUPPLIER"
        }

        return requests.post(url, data=json.dumps(payload), headers=self.__headers)

    def updateConsignment(self, consignmentObj):
        url = f"{self.__domain}{self.__ENDPOINTS['stockorders']}/{consignmentObj['id']}"

        consignmentObj['status'] = "RECEIVED"

        return requests.put(url, data=json.dumps(consignmentObj), headers=self.__headers)


    def deleteProduct(self, id):
        #return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['delProd'], id), headers=self.__headers).json()
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['delProd'], id), headers=self.__headers)

    def getRegisters(self, deleted='false'):

        return requests.request("GET", '{0}{1}'.format(self.__domain, self.__ENDPOINTS['registers'] + f"?deleted={deleted}"), headers=self.__headers).json()['data']

    def getCustomers(self):
        """
            Returns array of customer objects of this store.
        """
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['cust'], params={"deleted": False})
        #return self.__getSearch__(url=self.__domain + self.__ENDPOINTS['search'], type='customers')

    def getChannels(self):
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['channels'])

    def getChannelEvents(self, id, params=None):
        return self.__getRequest__(f"{self.__domain}{self.__ENDPOINTS['channels']}/{id}/events", params=params)

    def getOnAccountSales(self):
        """
            Returns array of on-account sales for this store.
        """



        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=onaccount')
        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='sales', status='onaccount')

    def getLaybySales(self):
        """
            Returns array of layby sales for this store.
        """
        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=layby')
        return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='sales', status='layby')

    def getOutlets(self):
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['outlets'], params={'deleted':False})
        #return requests.request("GET", self.__domain + self.__ENDPOINTS['outlets'], headers=self.__headers, params={'deleted':False,'page_size':2000}).json()['data']

    def uploadImage(self, pid, image):
        
        url = f"{self.__domain}{self.__ENDPOINTS['products']}/{pid}/actions/image_upload"
        payload = {
            'image' : image
        }
        return requests.post(url, headers=self.__headers, files=payload)
        

    def getProducts(self, endpointVersion='2.0'):
        if endpointVersion == '2.0':
            #print('in 2.0')
            prods = self.__getRequest__(self.__domain + self.__ENDPOINTS['products'+ endpointVersion])
            print(f"in 2.0 prod returned: {len(prods)}")
            return prods

        params = {
            "deleted" : False,
            "page_size" : 200
        }

        return self.__getRequestv09__(self.__domain + self.__ENDPOINTS['products'+ endpointVersion], params=params)
        #return self.__getRequest__(self.__domain + self.__ENDPOINTS['products'] + '?deleted=false')
        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='products')

    def getProducts2(self):
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['products2.0'], params={'deleted':False})

    def updateProductInventory(self, id, inventory):
        url = self.__domain + self.__ENDPOINTS['products0.9']

        payload = {
            "id" : id,
            "inventory" : inventory
        }

        #print(payload)

        response = requests.post(url, data=json.dumps(payload), headers=self.__headers)

        return response

    def getInventories(self):
        url = self.__domain + self.__ENDPOINTS['inventory']
        data = self.__getRequest__(url)
        print(f'getInventories: {len(data)}')
        return data

    def getCustomerSales(self, customer_id):

        url = self.__domain + self.__ENDPOINTS['search']

        params = {
            "page_size" : 10000,
            "deleted" : False,
            "type" : "sales",
            "customer_id" : customer_id
        }
        
        resp = requests.get(url, params=params, headers=self.__headers)
        # print(url, customer_id)
        #print(resp.json())
        payload = resp.json()
        # print(len(payload['data']))

        return payload['data']

    def __getSearch__(self, url, type='', deleted='false', offset='', pageSize='10000', status=''):
        """
            Base method for search API calls. Returns the 'data' array of the
            corresponding objects. Returns None if the request is unsuccessful.
            Currently, the regular customers endpoint doesn't work properly
            with deleted flag; this will have to do at the moment.
        """

        search = "{0}?type={1}&deleted={2}&page_size={3}&offset={4}"
        endpoint = search.format(url, type, deleted, pageSize, offset)

        print(type)
        if type == 'sales':
            search = "{0}?type={1}&status={2}&page_size={3}&offset={4}"
            endpoint = search.format(url, type, status, pageSize, offset)

        response = requests.request("GET", endpoint, headers = self.__headers)

        print(endpoint)
        print(response)
        print(response.json())

        if response.status_code != 200:
            return None

        data = []
        tempJson = response.json()['data']
        offset = 0

        while len(tempJson) > 0:
            data.extend(tempJson)
            offset += 10000

            if type == 'sales':
                endpoint = search.format(url, type, status, pageSize, offset)
            else:
                endpoint = search.format(url, type, deleted, pageSize, offset)

            #print(endpoint)

            request = requests.request("GET", endpoint, headers = self.__headers)

            print(request)

            if request.status_code == 500:
                break

            tempJson = request.json()['data']
            #print(len(tempJson))
            #print(len(data))

        return data

    def getAllSales(self):
        return self.__getRequest__('{0}{1}'.format(self.__domain, self.__ENDPOINTS['sales']))

    def filterOpenSales(self, sales):
        opensales = []
        for s in sales:
            if s['status'] == 'ONACCOUNT' or s['status'] == 'LAYBY' or s['status'] == 'SAVED':
                opensales.append(s)

        return opensales

    def getOpenSales(self):
        """
            Returns an array of all open sales of this store.  Layby and
            on-account sales.
        """

        allSales = self.getAllSales()

        opensales = self.filterOpenSales(allSales)

        print(f'allsales: {len(allSales)}  -  opensales: {len(opensales)}')

        '''
        tempOpenSales = []
        tempOpenSales.extend(self.getOnAccountSales())
        tempOpenSales.extend(self.getLaybySales())
        print(tempOpenSales)
        return tempOpenSales'''

        return opensales

    def getPrefix(self):
        """
            Returns this store's domain prefix.
        """
        return self.__prefix

    def __getRequestv09__(self, url, data='products', params=None):
        response = requests.request("GET", url, headers = self.__headers, params=params)

        if response.status_code != 200:
            return None

        tempJson = response.json()

        pagination = tempJson.get('pagination', None)

        if pagination is None:
            return tempJson['products']

        currPage = pagination['page']
        pages = pagination['pages']

        tempData = []

        while currPage <= pages:
            tempData.extend(tempJson[data])

            params['page'] = currPage + 1
            currPage = currPage + 1

            tempJson = requests.request("GET", url, headers = self.__headers, params=params).json()

        return tempData

    def __getRequest__(self, url, params={}):
        """
            Base method for regular API calls. Returns the 'data' array of the
            corresponding objects. Returns None if the request is unsuccessful.
            Will get all results based on the pagination, max version.
        """

        #reset
        response = None
        tempDataList = None
        tempJson = None
        version = None

        if params.get('page_size', None) is None:
            params['page_size'] = 5000

        response = requests.get(url, headers = self.__headers, params=params)
        print(f"{url} response: {response.status_code}...")
        if response.status_code != 200:
            return None

        #print(url)
        # gotta check if the url already has params for search
        # no ternary in python?
        '''if "?" in url:
            cursorParam = "&after={0}"
        else:
            cursorParam = "?after={0}"'''

        tempDataList = []
        tempJson = response.json()

        # print(tempJson)

        #print(tempJson.get('version', None))

        if tempJson.get('version', None) is None:
            print("in tempJson version check initial")
            return tempJson['data']

        version = tempJson['version']['min']

        # print(f"min version initial {version}...")
        # print(f"min version initial {tempJson['version']}...")

        while version is not None:
            #print(url)
            tempDataList.extend(tempJson['data'])
            #print(len(tempDataList))

            # print(f"{len(tempDataList)} prods, response: {response.status_code}")

            if tempJson['version']['max'] is None:
                break

            version = tempJson['version']['max']

            params['after'] = version
            time.sleep(0.5)
            #tempJson = requests.request("GET", url + cursorParam.format(version), headers = self.__headers).json()
            tempJson = requests.get(url , headers = self.__headers, params=params).json()

        print(f"{url}: {len(tempDataList)}")
        return tempDataList.copy()

    def connectSuccessful(self, obj):
        return (obj is not None)

    def getKeyToObjs(self, thatobjs, key):
        idtoobj = {}

        for o in thatobjs:
            id = o.get(key, None)

            if id is None:
                return None

            idtoobj[id] = o

        return idtoobj
