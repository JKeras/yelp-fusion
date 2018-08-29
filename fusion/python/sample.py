from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import csv

try:
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


API_KEY= 'rPdAbVnVvftpnh1OU6yImPDziFNqyVQ2F-G_FGWrJ0s9zxc7qH70y9Cbic5y-12sphIuAxso2D-C7qHyH_dH1C9PyS0pmCrIEs9jZucW5Ky0IGlPkfrzC7Tw6k90W3Yx' 

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'

DEFAULT_CATEGORIES = 'beautysvc,all'
DEFAULT_LOCATION = 'minneapolis, mn'
SEARCH_LIMIT = 50
SEARCH_OFFSET = 1000


def request(host, path, api_key, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, categories, location):
    url_params = {
        'categories': categories.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': SEARCH_OFFSET
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(categories, location):
    response = search(API_KEY, categories, location)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(categories, location))
        return

    results={}
    results['businesses']=[]

    for b in businesses:
        r = get_business(API_KEY, b['id'])
        if r['location']['city'] =='Minneapolis':
        #if r['location']['city'] =='Edina':
        #if r['location']['city'] =='Saint Paul':
            name = r['name'].encode('ascii', 'ignore').decode('ascii')
            phone = r['display_phone']
            if r['location']['zip_code']==None or r['location']['zip_code']=='':
                add=r['location']['city']+", "+r['location']['state']
            elif r['location']['address1']==None:
                add=r['location']['city']+", "+r['location']['state']+" "+r['location']['zip_code']
            elif r['location']['address2']==None:
                add=r['location']['address1']+", "+r['location']['city']+", "+r['location']['state']+" "+r['location']['zip_code']
            else:
                add=r['location']['address1']+" "+r['location']['address2']+", "+r['location']['city']+", "+r['location']['state']+" "+r['location']['zip_code']
            url = r['url']
            results['businesses'].append({'name':name,'phone':phone,'address':add,'yelpURL':url})


    with open('yelpresults_mn_20.csv',mode='w') as f:
        fieldnames = ['name','phone','address','yelpURL']
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        for i in results['businesses']:
            writer.writerow(i)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--categories', dest='categories', default=DEFAULT_CATEGORIES,
                        type=str, help='Search categories (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.categories, input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
