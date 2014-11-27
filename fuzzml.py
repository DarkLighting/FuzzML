#!/usr/bin/env python2

import sys
import requests
import argparse
import os.path
from datetime import datetime
import xml.etree.ElementTree as et
from xml.dom import minidom
import unicodedata

parser = argparse.ArgumentParser( description='SOAP web service Fuzzer' );
parser.add_argument( 'url', help='Web service URL to fuzz' );
parser.add_argument( '--no-cert-validate', action='store_true', help="Disable certificates validation" );
parser.add_argument( '--auto', action='store_true', help="Enable automatic testing" );
parser.add_argument( '--header', nargs='*', help='Specify required request headers' );
parser.add_argument( '--fheader', help='Specify a file containing the required request headers' );
parser.add_argument( '--ua', help='Specify User-Agent header' );
parser.add_argument( '--ct', help='Specify Content-Type header' );
parser.add_argument( '--data', help='Data to be sent inside the request body' );
parser.add_argument( '--fdata', help='Specify a file containing the data to be sent inside the request body' );
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
    if (args.no_cert_validate):
        req = requests.post(url, data='', verify=False);   
    else:
        req = requests.post(url, data='');   
    if (req.status_code == requests.codes.ok):
        return
    else:
        print "HTTP Response Status Code %s - %s" %( req.status_code, req.reason );
        end("Exiting.\n");


def make_request( url, usr_headers, content='None' ):
    if (args.no_cert_validate):
        http = requests.post( url, data=content, headers=usr_headers, verify=False );
    else:
        http = requests.post( url, data=content, headers=usr_headers );
    http.close();
    return http;

def get_address( url ):
    if url.startswith( 'http://' ):
        address = url.replace( 'http://', '', 1 );
        address = address.replace( '/', '_' );
        time = datetime.now();
        address = address + '_' + time.strftime( "%Y%m%d_%H%M.%S.%f" );    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    elif url.startswith( 'https://' ):
        address = url.replace( 'https://', '', 1 );
        address = address.replace( '/', '_' );
        time = datetime.now();
        address = address + '_' + time.strftime( "%Y%m%d_%H%M.%S.%f" );    # www.example.com_webservice.php_20141110_1822.15.059238.txt
        return address;
    else:
        end('Malformed URL');

def save_response( request_content, response_content ):
    if not os.path.exists(path):
        os.makedirs(path);
    with open( path + url + '_req.txt', 'w+' ) as fp_req:     # requests/www.example.com_webservice.php_20141110_1822.15.059238_req.txt 
        fp_req.write( request_content );
    with open( path + url + '_resp.txt', 'w+' ) as fp_resp:    # requests/www.example.com_webservice.php_20141110_1822.15.059238_resp.txt
        fp_resp.write( response_content );

def add_default_headers():
    return dict({ 'Content-Type': 'text/xml; charset=ascii', 'User-Agent': 'FuzzML/1.0' });


def add_header( header_dict, field_value_dict ):
    header_dict.update( field_value_dict );
    return

def add_headers( args ):
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
        end("File not found: %s\n" %( hdr_file ));

def list2dict( llist ):
    return dict( llist[i:i+2] for i in range( 0, len( llist ), 2) )


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

        
def parse_xml_resp( xml_data ):
    if ( ( not isinstance( xml_data, str ) ) and ( not isinstance( xml_data, et.Element ) ) ):
        end( 'Unrecognized xml data.' );
    if ( isinstance( xml_data, str ) ):
        root = et.fromstring( xml_data );
    elif ( isinstance( xml_data, et.Element ) ):
        root = xml_data;
    for child in root.iter():
        if ( '}' in child.tag ):
            print child.tag.split('}')[1], child.attrib, '-' + child.text.strip();  # transforms '{scope}TAG' in 'TAG'

'''
def fuzzml_element_duplication( root ):
    xml_nodes = get_nodes_list( root );
    #xml_nodes = root;
    print ( len(xml_nodes));
    for i in range( 1, len(xml_nodes) ):
        nodes_list = list( xml_nodes );
        #tree = et.Element(xml_nodes[0]);
        tree = reconstruct_xml_tree( xml_nodes );
        #nodes_list =  xml_nodes;
        #nodes_list = et.Element() ;
        #tree = 
        print type(nodes_list);
        if ( len( nodes_list ) > 1 ):
            duplicate_node( i, nodes_list );
            print 'list - ',nodes_list[i];
        print 'root - ',root[0];
        #et.dump( nodes_list[0] );
        et.tostring( root[0] );
        print '\n';
    et.tostring( xml_nodes[1] );
    #print xml_nodes;
'''

def fuzzml_element_duplication( root ):
    new_tree = copy_tree ( root );
    comparison_node_list = list();
    tree_root = new_tree.getroot();
    vnode = get_leaf_parent( tree_root );
    for i in range( len( get_children( vnode ) ) ):
        duplicate_children_node( vnode, i, comparison_node_list );
        print "%s %s" %(vnode, '\n');
        et.dump(tree_root);
    #get_left_leaf( tree_root );
    #print tree;


def get_nodes_list( node ):
    return list( node.iter() );


def duplicate_children_node( visited_node, i, comparison_node_list ):
    children = get_children( visited_node );    # get list of children
    visited_node.append( children[i] );     # appends the i-th child
    comparison_node_list.append( children[i] );
    print comparison_node_list;




def copy_tree( tree_root ):
    return et.ElementTree( tree_root );        


def get_children( node ):
    return list( node );


def get_left_leaf( node ):
    children = get_children( node );
    if ( not children ):
        return node;
    get_left_leaf( children[0] );


def get_leaf_parent( node, parent=None ):
    children = get_children( node );
    while ( children ):
        parent = node;
        node = children[0];
        children = get_children( node );  
        print 'node - ', node;
        print 'parent - ', parent;
    if ( parent is not None ):
        print 'parent final - ', parent;
        return parent;
    else:   # it is a one node tree
        print 'node final - ', node;
        return node;




if __name__ == '__main__':
    check_url_syntax( args.url );
    if args.auto:
        verify_url( args.url );
    url = get_address( args.url ); 
    hr = add_headers( args );
    content = set_req_body( args.data, args.fdata );
    print '\nContent:\n';
    #print content;
    xml_root = parse_xml_req( content );
    fuzzml_element_duplication( xml_root );
    #http_resp = make_request( args.url, hr, content );
    #save_response( args.data, http_resp.text );
    #print '\nResponse:\n';
    #response_converted = unicodedata.normalize( 'NFKD', http_resp.text ).encode( 'ascii', 'ignore' );
    #print response_converted;
    #parse_xml_resp( response_converted );


