import requests, json

class VendApi:
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
        "products" : "api/2.0/products",
        "delProd" : "api/products",
        "registers" : "api/2.0/registers",
        "stockorders" : "api/consignment",
        "cons_products" : "api/consignment_product"
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

    def getConsigmentProducts(self, cid):
        url = f"{self.__domain}{self.__ENDPOINTS['cons_products']}"
        params = {
            "consignment_id" : cid.strip()
        }
        print(cid)
        return self.__getRequestv09__(url=url, params=params, data='consignment_products')

    def reversionConsigmentProducts(self, getPayload):
        id = getPayload['id']
        cid = getPayload['consignment_id']
        pid = getPayload['product_id']
        count = getPayload['count']

        minPayload = {
            'consignment_id' : cid,
            'product_id' : pid,
            'count' : count
        }

        url = f"{self.__domain}{self.__ENDPOINTS['cons_products']}/{id}"

        return requests.put(url, data=json.dumps(minPayload), headers=self.__headers)


    def deleteCustomer(self, id):
        """
            Deletes a customer based on the provided ID. Returns the status code
            of the response.

            204: Successfully deleted
            500: Could not delete because of customer attached to open sale(s)
            404: No such customer exists to delete.
        """
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['cust'], id), headers=self.__headers).status_code

    def deleteProduct(self, id):
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['delProd'], id), headers=self.__headers).json()

    def getRegisters(self):
        response = requests.request("GET", '{0}/{1}'.format(self.__domain, self.__ENDPOINTS['registers'] + "?deleted=false"), headers=self.__headers)
        print(response)
        print('{0}/{1}'.format(self.__domain, self.__ENDPOINTS['registers'] + "?deleted=false"))
        return requests.request("GET", '{0}{1}'.format(self.__domain, self.__ENDPOINTS['registers'] + "?deleted=false"), headers=self.__headers).json()

    def getCustomers(self):
        """
            Returns array of customer objects of this store.
        """
        #return self.__getRequest__(self.__domain + self.__ENDPOINTS['cust'] + "?deleted=" + str(False))
        return self.__getSearch__(url=self.__domain + self.__ENDPOINTS['search'], type='customers')

    def getOnAccountSales(self):
        """
            Returns array of on-account sales for this store.
        """

        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=onaccount')
        return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='sales', status='onaccount')

    def getLaybySales(self):
        """
            Returns array of layby sales for this store.
        """
        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=layby')
        return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='sales', status='layby')

    def getOutlets(self):
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['outlets'])

    def getProducts(self):
        return self.__getRequest__(self.__domain + self.__ENDPOINTS['products'] + '?deleted=false')
        #return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'], type='products')
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

    def getOpenSales(self):
        """
            Returns an array of all open sales of this store.  Layby and
            on-account sales.
        """

        tempOpenSales = []
        tempOpenSales.extend(self.getOnAccountSales())
        tempOpenSales.extend(self.getLaybySales())

        print(tempOpenSales)
        return tempOpenSales

    def getPrefix(self):
        """
            Returns this store's domain prefix.
        """
        return self.__prefix

    def __getRequest__(self, url):
        """
            Base method for regular API calls. Returns the 'data' array of the
            corresponding objects. Returns None if the request is unsuccessful.
            Will get all results based on the pagination, max version.
        """
        response = requests.request("GET", url, headers = self.__headers)

        if response.status_code != 200:
            return None

        # gotta check if the url already has params for search
        # no ternary in python?
        if "?" in url:
            cursorParam = "&after={0}"
        else:
            cursorParam = "?after={0}"

        tempDataList = []
        tempJson = response.json()
        version = tempJson['version']['min']

        while version is not None:
            tempDataList.extend(tempJson['data'])

            if tempJson['version']['max'] is None:
                break;

            version = tempJson['version']['max']

            tempJson = requests.request("GET", url + cursorParam.format(version), headers = self.__headers).json()

        return tempDataList

    def __getRequestv09__(self, url, data='products', params=None):
        response = requests.request("GET", url, headers = self.__headers, params=params)
        print(response)
        if response.status_code != 200:
            return None

        tempJson = response.json()

        pagination = tempJson.get('pagination', None)

        if pagination is None:
            return tempJson[data]

        currPage = pagination['page']
        pages = pagination['pages']

        tempData = []

        while currPage <= pages:
            tempData.extend(tempJson[data])

            params['page'] = currPage + 1
            currPage = currPage + 1

            tempJson = requests.request("GET", url, headers = self.__headers, params=params).json()

        return tempData
