#!/usr/bin/env python2

import sys
import requests
import argparse
import os.path
from datetime import datetime
import xml.etree.ElementTree as et
from xml.dom import minidom
import random

if ( len( sys.argv ) < 2 ):
    print "\nMissing parameters. Run \"%s -h\" for help.\n" %(sys.argv[0]);
    exit();

parser = argparse.ArgumentParser( description='SOAP web service Fuzzer' );
parser.add_argument( 'url', help='Web service URL to fuzz' );
parser.add_argument( '--no-cert-validate', action='store_true', help="Disable certificate validation" );
parser.add_argument( '--auto', action='store_true', help="Enable automatic testing" );
header_group = parser.add_mutually_exclusive_group();
header_group.add_argument( '--header', metavar='<Header>', nargs='*', help='Specify required request headers' );
header_group.add_argument( '--fheader', metavar='<Headers file>', help='Specify a file containing the required request headers' );
parser.add_argument( '--ua', metavar='<User-Agent>', help='Specify User-Agent header' );
parser.add_argument( '--ct', metavar='<Content-Type>', help='Specify Content-Type header' );
data_group = parser.add_mutually_exclusive_group();
data_group.add_argument( '--data', metavar='<POST content>', help='Data to be sent inside the request body' );
data_group.add_argument( '--fdata', metavar='<POST content file>', help='Specify a file containing the data to be sent inside the request body' );
args = parser.parse_args()


def end( reason ):
    print '[-] ' + reason;
    exit();

def check_url_syntax( url ):
    if ((url.find('http://',0,7) == -1) and (url.find('https://',0,8) == -1)):
        end('\nERROR: address not starting with http or https.\nCheck your URL and try again.\n');

def verify_url( url ):
    print('\n[+] Checking if URL is available...');
    if (args.no_cert_validate):
        req = requests.post(url, data='', verify=False);   
    else:
        req = requests.post(url, data='');   
    if (req.status_code == requests.codes.ok):
        return
    else:
        print "[+] HTTP Response Status Code %s - %s" %( req.status_code, req.reason );
        end("Exiting.\n");


def make_request( url, usr_headers, content='None' ):
    if (args.no_cert_validate):
        http = requests.post( url, data=content, headers=usr_headers, verify=False );
    else:
        http = requests.post( url, data=content, headers=usr_headers );
    http.close();
    return http;

def get_save_filename( url, clock ):
    if url.startswith( 'http://' ):
        address = url.replace( 'http://', '', 1 );
        address = address.replace( '/', '_' );
        address = address + '_' + clock;    # www.example.com_webservice.php_20141110_1822.15.059238.xml
        return address;
    elif url.startswith( 'https://' ):
        address = url.replace( 'https://', '', 1 );
        address = address.replace( '/', '_' );
        address = address + '_' + clock;    # www.example.com_webservice.php_20141110_1822.15.059238.xml
        return address;
    else:
        end('Malformed URL');

def save_data( request_content, response_content, clock ):
    path = 'requests/';     # path to write requests's response
    if not os.path.exists(path):
        os.makedirs(path);
    with open( path + get_save_filename( args.url, clock ) + '_req.xml', 'w+' ) as fp_req:     # requests/www.example.com_webservice.php_20141110_1822.15.059238_req.xml 
        fp_req.write( request_content.encode('utf-8') );    # fixing problems with unicode characters 
    with open( path + get_save_filename( args.url, clock ) + '_resp.xml', 'w+' ) as fp_resp:    # requests/www.example.com_webservice.php_20141110_1822.15.059238_resp.xml
        fp_resp.write( response_content.encode( 'utf-8' ) );  # fixing problems with unicode characters 

def add_default_headers():
    return dict({ 'Content-Type': 'text/xml; charset=ascii', 'User-Agent': 'FuzzML/1.0', 'SOAPAction': '\"\"' });


def add_header( header_dict, field_value_dict ):
    header_dict.update( field_value_dict );
    return

def add_headers( args ):
    print ( '[+] Adding headers...' );
    hr = add_default_headers();
    if ( args.header is not None ):
        add_header( hr, list2dict( args.header ) );
    if ( args.fheader is not None ):
        add_header( hr, get_headers_from_file( args.fheader ) );
    if ( args.ua is not None ):
        add_header( hr, list2dict( [ 'User-Agent', args.ua ] ) );
    if ( args.ct is not None ):
        add_header( hr, list2dict( [ 'Content-Type', args.ct ] ) );
    return hr;


def get_headers_from_file( hdr_file ):
    if (os.path.exists( hdr_file )):
        fp_hdr = open( hdr_file, 'r');
        lines = dict();
        for line in fp_hdr:
            line = replace_tabs(line);
            lines.update( list2dict( line ) );
        fp_hdr.close();
        return lines;
    else:
        end( "File not found: %s\n" %( hdr_file ) );

def list2dict( llist ):
    converted_list = list();
    for i in range( 0, len( llist ) ):
        converted_list.extend( llist[i].split(' ') );
    return dict( converted_list[i:i+2] for i in range( 0, len( converted_list ), 2) )


def replace_tabs( string ):
    return string.split();


def set_req_body( cmdline_data, file_data ):
    if ( ( cmdline_data is not None ) and ( file_data is None ) ):      # if the user defined data through command line
        return cmdline_data;
    elif ( ( cmdline_data is None ) and (file_data is not None ) ):     # if the user defined data through a file
        if os.path.exists( file_data ):
            with open( file_data, 'r' ) as f:
                body = f.read( 20 * 1024 );    # read at most 20 KB from file
            return body;
    elif ( ( cmdline_data is not None ) and ( file_data is not None ) ):
        end( 'You cannot specify BOTH parameters: --data AND --fdata. Choose only one.\n' );


def parse_xml_req( xml_data ):
    if ( ( not isinstance( xml_data, str ) ) and ( not isinstance( xml_data, et.Element ) ) ):
        end( 'Unrecognized xml data.' );
    if ( isinstance( xml_data, str ) ):
        root = et.fromstring( xml_data );
    elif ( isinstance( xml_data, et.Element ) ):
        root = xml_data;
    return root;


def fuzzml_element_duplication( root, url, hr ):
    new_tree = copy_tree ( root );
    tree_root = new_tree.getroot();
    nodes_to_duplicate = get_nodes_list( tree_root );
    if ( nodes_to_duplicate ):
        print( '[+] Fuzzing elements (by duplication) and saving responses...' );
        for node in nodes_to_duplicate:
            children = get_children( node );
            for child in children:
                child_tree = copy_tree( child );
                child_dup = child_tree.getroot();
                node.insert( get_children( node ).index( child ), child_dup );  # places the duplicated node side-by-side with the original node
                keep_information( et.tostring( tree_root ), url, hr );
                node.remove( child_dup );
    else:
        end( 'Tree has only one Element\n' );


def fuzzml_element_omission( root, url, hr ):
    new_tree = copy_tree ( root );
    tree_root = new_tree.getroot();
    nodes_to_remove = get_nodes_list( tree_root );
    if ( nodes_to_remove ):
        print( '[+] Fuzzing elements (by omission) and saving responses...' );
        for node in nodes_to_remove:
            children = get_children( node );
            for child in children:
                index = get_children( node ).index( child );    # remember element position
                node.remove( child );
                keep_information( et.tostring( tree_root ), url, hr );
                node.insert( index, child );  # places the removed node back into place
    else:
        end( 'Tree has only one Element\n' );


def fuzzml_element_tag_malforming( root, url, hr ):
    new_tree = copy_tree ( root );
    tree_root = new_tree.getroot();
    nodes_to_remove = get_nodes_list( tree_root );
    if ( nodes_to_remove ):
        print( '[+] Fuzzing elements (by tag malformation) and saving responses...' );
        xml_allowed_chars = sum( list( ( range(65,90),[95],range(97,122) ) ), [] );     # creating list of acceptable chars in an xml tag
        for node in nodes_to_remove:
            children = get_children( node );
            for child in children:
                if ( '}' in child.tag ):
                    namespace = child.tag.split('}')[0];
                    tag = child.tag.split('}')[1];
                else:
                    tag = str( child.tag );
                element_position = get_children( node ).index( child );    # remember element position
                char_index = random.choice(range(0, len( tag )));  # choosing a random char to strip from tag
                if (namespace):
                    child.tag = namespace + '}' + tag.replace( tag[ char_index ], '' );       # stripping char from tag
                else:
                    child.tag = tag.replace( tag[ char_index ], '' );       # stripping char from tag
                child.tag = child.tag + chr(random.choice( xml_allowed_chars ) ) ;     # adding a random ascii char suffix
                keep_information( et.tostring( tree_root ), url, hr );
                if (namespace):
                    child.tag = namespace + '}' + tag ;
                else:
                    child.tag = tag ;   # putting everything back to normal
    else:
        end( 'Tree has only one Element\n' );



def keep_information( fuzzed_xml, url, hr ):
    fuzzed_xml_request = minidom.parseString( fuzzed_xml );
    fuzzed_xml_response = make_request( url, hr, fuzzed_xml_request.toprettyxml() );
    fuzzed_xml_response = minidom.parseString( fuzzed_xml_response.text.encode( 'utf-8' ) );
    save_data( fuzzed_xml_request.toprettyxml(), fuzzed_xml_response.toxml(), datetime.now().strftime( "%Y%m%d_%H%M.%S.%f" ) );
    

def get_nodes_list( node ):
    return list( node.iter() );


def copy_tree( tree_root ):
    return et.ElementTree( tree_root );        


def get_children( node ):
    return list( node );


def main():
    check_url_syntax( args.url );
    if args.auto:
        verify_url( args.url );
    hr = add_headers( args );
    content = set_req_body( args.data, args.fdata );
    print( '[+] Parsing...' );
    xml_root = parse_xml_req( content );
    fuzzml_element_duplication( xml_root, args.url, hr );
    fuzzml_element_omission( xml_root, args.url, hr );
    fuzzml_element_tag_malforming( xml_root, args.url, hr );



if __name__ == '__main__':
    main();

