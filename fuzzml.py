#!/usr/bin/env python2

import requests
import argparse
import json
import os.path
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
        return
    else:
        print "HTTP Response Status Code %s - %s" %( req.status_code, req.reason );
        end("Exiting.\n");


def make_request( url, usr_headers, content='None' ):
    http = requests.post( url, data=content, headers=usr_headers );
    http.close();
    return http;

def get_address( url ):
    if url.startswith('http://'):
        address = url.replace('http://', '', 1);
        address = address.replace('/', '_');
        time = datetime.now();
        address = address + '_' + time.strftime("%Y%m%d_%H%M.%S.%f");    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    elif url.startswith('https://'):
        address = url.replace('https://', '', 1);
        address = address.replace('/', '_');
        time = datetime.now();
        address = address + '_' + time.strftime("%Y%m%d_%H%M.%S.%f");    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    else:
        end('Malformed URL');

def save_response( request_content, response_content ):
    if not os.path.exists(path):
        os.makedirs(path);
    fp_req = open( path + url + '_req.txt', 'w+');     # requests/www.example.com_webservice.php_20141110_1822.15.059238_req.txt 
    fp_resp = open(path + url + '_resp.txt', 'w+');    # requests/www.example.com_webservice.php_20141110_1822.15.059238_resp.txt
    fp_req.write(request_content);
    fp_resp.write(response_content);
    fp_req.close();
    fp_resp.close();

def add_default_headers():
    return dict({ 'Content-Type': 'text/xml; charset=utf-8', 'User-Agent': 'FuzzML/1.0' });


def check_headers( hdr ):
    hdr = ''.join( hdr[0:1] )
    if os.path.isfile( hdr ): 
        print hdr;    
    else:
        end("It looks like you specified a file containing the headers (%s), but I'm not able to find it." %( hdr ));

check_url_syntax( args.url );
verify_url( args.url );
url = get_address( args.url ); 
#check_headers( args.header );
hr = add_default_headers();
hr.update(dict(args.header[i:i+2] for i in range(0, len(args.header), 2)));
http_resp = make_request( args.url, hr, args.data );
#save_response( args.data, http_resp.text );

