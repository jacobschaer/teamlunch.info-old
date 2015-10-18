import json
import pprint
import sys
import urllib
import urllib2

import oauth2

class YelpAPI:    
    """ Stolen Shamelessy from https://github.com/Yelp/yelp-api/blob/master/v2/python/sample.py"""
    def __init__(self, credentials_dict):
        self.CONSUMER_KEY = credentials_dict['consumer_key']
        self.CONSUMER_SECRET = credentials_dict['consumer_secret']
        self.TOKEN = credentials_dict['token']
        self.TOKEN_SECRET = credentials_dict['token_secret']
        self.API_HOST = 'api.yelp.com'
        self.SEARCH_LIMIT = 3
        self.SEARCH_PATH = '/v2/search/'
        self.BUSINESS_PATH = '/v2/business/'


    def request(self, host, path, url_params=None):
        """Prepares OAuth authentication and sends the request to the API.
        Args:
            host (str): The domain host of the API.
            path (str): The path of the API after the domain.
            url_params (dict): An optional set of query parameters in the request.
        Returns:
            dict: The JSON response from the request.
        Raises:
            urllib2.HTTPError: An error occurs from the HTTP request.
        """
        url_params = url_params or {}
        url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

        consumer = oauth2.Consumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': self.TOKEN,
                'oauth_consumer_key': self.CONSUMER_KEY
            }
        )
        token = oauth2.Token(self.TOKEN, self.TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()
        
        print u'Querying {0} ...'.format(url)

        conn = urllib2.urlopen(signed_url, None) 

        try:
            response = json.loads(conn.read())
        finally:
            conn.close()

        return response

    def search(self, term, location):
        """Query the Search API by a search term and location.
        Args:
            term (str): The search term passed to the API.
            location (str): The search location passed to the API.
        Returns:
            dict: The JSON response from the request.
        """
        
        url_params = {
            'term': term.replace(' ', '+'),
            'location': location.replace(' ', '+'),
            'limit': self.SEARCH_LIMIT
        }
        return self.request(self.API_HOST, self.SEARCH_PATH, url_params=url_params)

    def get_business(self, business_id):
        """Query the Business API by a business ID.
        Args:
            business_id (str): The ID of the business to query.
        Returns:
            dict: The JSON response from the request.
        """
        business_path = self.BUSINESS_PATH + business_id

        return self.request(self.API_HOST, business_path)

    def query_api(self, term, location):
        """Queries the API by the input values from the user.
        Args:
            term (str): The search term to query.
            location (str): The location of the business to query.
        """
        print term, location
        response = self.search(term, location)

        businesses = response.get('businesses')

        if not businesses:
            print u'No businesses for {0} in {1} found.'.format(term, location)
            return

        results = list()
        for business in businesses:
            business_id = business['id']
            results.append(self.get_business(business_id))

        return results