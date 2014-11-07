#!/usr/bin/env python2

import requests
import argparse
#import re

parser = argparse.ArgumentParser(description='SOAP web service Fuzzer')
parser.add_argument("url", help="Web service URL to fuzz")
args = parser.parse_args()

#args.url = args.url.lower()  
#url = args.url;

def end( reason ):
    print reason;
    exit();

def check_url( url ):
if ((url.find('http://',0,7) == -1) and (url.find('https://',0,8) == -1)):
    end('\nERROR: not starting with http or https.\nCheck your URL and try again.\n');


check_url( args.url )

print('Checking if URL is available:\n');
r = requests.post(url, data=, headers=)   
