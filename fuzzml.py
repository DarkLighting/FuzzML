#!/usr/bin/env python2

import requests
import argparse
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser(description='SOAP web service Fuzzer', fromfile_prefix_chars='@')
parser.add_argument('url', help='Web service URL to fuzz')
parser.add_argument('--header', nargs='*', help='Specify required request headers')
parser.add_argument('--data', help='Data to be sent inside the request body')
args = parser.parse_args()

#args.url = args.url.lower()  
#url = args.url;
path = 'requests/';     # path to write requests's response

def end( reason ):
    print reason;
    exit();

def check_url_syntax( url ):
    if ((url.find('http://',0,7) == -1) and (url.find('https://',0,8) == -1)):
        end('\nERROR: not starting with http or https.\nCheck your URL and try again.\n');

def verify_url( url ):
    print('\nChecking if URL is available...');
    req = requests.post(url, data='');   
    if (req.status_code == requests.codes.ok):
        print 'OK\n';
        return
    else:
        print "HTTP Response Status Code %s - %s" %(req.status_code, req.reason);
        end("Exiting.\n");


def make_request( url, http_headers={'Content-Type': 'text/xml; charset=utf-8', 'User-Agent': 'FuzzML/1.0'}, content='None' ):
    http = requests.post( url, data=content, headers=http_headers );
    return http;

def get_address( url ):
    if url.startswith('http://'):
        address = url.replace('http://', '', 1);
        address = address.replace('/', '_');
        time = datetime.now();
        address = address + '_' + time.strftime("%Y%m%d_%H%M.%S.%f") + '.txt';    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    elif url.startswith('https://'):
        address = url.replace('https://', '', 1);
        address = address.replace('/', '_');
        time = datetime.now();
        address = address + '_' + time.strftime("%Y%m%d_%H%M.%S.%f") + '.txt';    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    else:
        end('Malformed URL');


check_url_syntax( args.url );
verify_url( args.url );
url = get_address( args.url ); 
http_resp = make_request( args.url, args.header, args.data );
http_resp.close();

if not os.path.exists(path):
    os.makedirs(path);

fp = open(path + url, 'w+');    # requests/www.example.com_webservice.php_20141110_1822.15.059238.txt
fp.write(http_resp.text);


