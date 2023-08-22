# Copyright Notice:
# Copyright 2016-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Creator/blob/main/LICENSE.md

"""
Redfish Mockup Creator

File : redfishMockupCreate.py

Brief : This tool walks a service and creates a mockup from all resources
"""

import argparse
import datetime
import json
import os
import redfish
import sys
import time
import xml.etree.ElementTree as ET
import logging
import copy
import gc
from redfish import redfish_logger

# Version info
tool_version = "1.1.9"

# For Windows, there are restricted characters in folder names that could be used in URIs
disallowed_folder_characters_win = [ ":", "*", "?", "\"", "<", ">", "|" ]
folder_name_fix = False
if sys.platform == "win32" or sys.platform == "cygwin":
    folder_name_fix = True

def main():
    """
    Main entry point for the script
    """

    # Get the input arguments
    argget = argparse.ArgumentParser( description = "A tool to walk a Redfish service and create a mockup from all resources" )
    argget.add_argument( "--user", "-u", type = str, required = True, help = "The user name for authentication" )
    argget.add_argument( "--password", "-p",  type = str, required = True, help = "The password for authentication" )
    argget.add_argument( "--rhost", "-r", type = str, required = True, help = "The IP address (and port) of the Redfish service" )
    argget.add_argument( "--Dir", "-D", type = str, help = "Output directory for the mockup; defaults to 'rfMockUpDfltDir'", default = "rfMockUpDfltDir" )
    argget.add_argument( "--Secure", "-S", action = "store_true", help = "Use HTTPS for all operations" )
    argget.add_argument( "--Auth", "-A", type = str, help = "Authentication mode", choices = [ "None", "Basic", "Session" ], default = "Session" )
    argget.add_argument( "--Headers", "-H", action = "store_true", help = "Captures the response headers in the mockup" )
    argget.add_argument( "--Time", "-T", action = "store_true", help = "Capture the time of each GET in the mockup" )
    argget.add_argument( "--Copyright", "-C", type = str, help = "Copyright string to add to each resource", default = None )
    argget.add_argument( "--description", "-d", type = str, help = "Mockup description to add to the output readme file", default = "" )
    argget.add_argument( "--quiet", "-q", action = "store_true", help = "Quiet mode; progress messages suppressed" )
    argget.add_argument( "--trace", "-trace", action = "store_true", help = "Enable tracing; creates the file rf-mockup-create.log in the output directory to capture Redfish traces with the service" )
    argget.add_argument( "--maxlogentries", "-maxlogentries", type = int, help = "The maximum number of log entries to collect in each log service" )
    argget.add_argument( "--forcefolderrename", "-forcefolderrename", action = "store_true", help = "Indicates if URIs containing characters that are disallowed in Windows folder names are renamed to replace the characters with underscores" )
    args, unknown = argget.parse_known_args()

    # Convert the authentication method to something usable with the Redfish library
    # This is needed for backwards compatibility with older versions of the tool
    if args.Auth == "Session":
        args.Auth = "session"
    else:
        args.Auth = "basic"

    # Build the base URL for the service
    # More backwards compatibility
    if "://" not in args.rhost:
        if args.Secure:
            args.rhost = "https://{}".format( args.rhost )
        else:
            args.rhost = "http://{}".format( args.rhost )

    # Set up the output
    if not os.path.isdir( args.Dir ):
        # Does not exist; make the directory
        try:
            os.makedirs( args.Dir )
        except Exception as err:
            print( "ERROR: Aborting; could not create output directory '{}': {}".format( args.Dir, err ) )
            sys.exit( 1 )
    else:
        if len( os.listdir( args.Dir ) ) != 0:
            print( "ERROR: Aborting; output directory not empty..." )
            sys.exit( 1 )

    print( "Redfish Mockup Creator, Version {}".format( tool_version ) )
    print( "Address: {}".format( args.rhost ) )
    print( "Full Output Path: {}".format( os.path.abspath( args.Dir ) ) )
    print( "Description: {}".format( args.description ) )
    print( "Starting mockup creation..." )
    if args.quiet:
        print( "Quiet mode enabled; please wait..." )

    # Create the readme file
    try:
        with open( os.path.join( args.Dir, "README" ), "w" ) as readf:
            readf.write( "Redfish service captured by the Redfish Mockup Creator, Version {}\n".format( tool_version ) )
            readf.write( "Created: {}\n".format( datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" ) ) )
            readf.write( "Service: {}\n".format( args.rhost ) )
            readf.write( "User: {}\n".format( args.user ) )
            readf.write( "Description: {}\n".format( args.description ) )
    except Exception as err:
        print( "ERROR: Aborting; could not create README file in output directory: {}".format( err ) )
        sys.exit( 1 )

    # Set up the trace file if requested
    if args.trace:
        redfish_logger( os.path.join( args.Dir, "rf-mockup-create.log" ), "%(asctime)s - %(name)s - %(levelname)s - %(message)s", logging.DEBUG )

    # Set up the Redfish object
    try:
        redfish_obj = redfish.redfish_client( base_url = args.rhost, username = args.user, password = args.password )
        redfish_obj.login( auth = args.Auth )
    except Exception as err:
        print( "ERROR: Aborting; could not authenticate with the Redfish service: {}".format( err ) )
        sys.exit( 1 )

    # Scan the service
    response_times = {}
    scan_resource( redfish_obj, args, response_times, "/redfish" )
    scan_resource( redfish_obj, args, response_times, "/redfish/v1/odata" )
    scan_resource( redfish_obj, args, response_times, "/redfish/v1/$metadata", is_csdl = True )
    scan_resource( redfish_obj, args, response_times, "/redfish/v1" )
    redfish_obj.logout()

    # Add time statistics to the readme
    total_response_time = sum( response_times.values() )
    average_response_time = total_response_time / len( response_times )
    min_response_uri = min( response_times, key = response_times.get )
    max_response_uri = max( response_times, key = response_times.get )
    with open( os.path.join( args.Dir, "README" ), "a" ) as readf:
        readf.write( "Total response time: {}\n".format( total_response_time ) )
        readf.write( "Average response time: {}\n".format( average_response_time ) )
        readf.write( "Minimum response time: {}, {}\n".format( response_times[min_response_uri], min_response_uri ) )
        readf.write( "Maximum response time: {}, {}\n".format( response_times[max_response_uri], max_response_uri ) )

    print( "Completed mockup creation!" )

def scan_resource( redfish_obj, args, response_times, uri, is_csdl = False ):
    """
    Scans a resource and saves its response

    Args:
        redfish_obj: The Redfish client object with an open session
        args: The command line arguments
        response_times: The response times database
        uri: The URI to get
        is_csdl: Indicates if the resource is a CSDL file
    """

    # Check if the URI is a relative URI
    if not uri.startswith( "/" ):
        return

    # Set up the output folder
    try:
        path = uri[1:]
        if folder_name_fix or args.forcefolderrename:
            for character in disallowed_folder_characters_win:
                path = path.replace( character, "_" )
        path = os.path.join( args.Dir, path )
        if not os.path.isdir( path ):
            # Does not exist; make the directory
            os.makedirs( path )
    except Exception as err:
        print( "ERROR: Could not create directory for '{}': {}".format( uri, err ) )
        return

    # Check if the index file already exists
    index_name = "index.json"
    if is_csdl:
        index_name = "index.xml"
    index_path = os.path.join( path, index_name )
    if os.path.isfile( index_path ):
        # File exists; already scanned this resource
        return

    # Get the resource
    if not args.quiet:
        print( "Getting {}...".format( uri ) )
    try:
        start_time = time.time()
        resource = redfish_obj.get( uri, headers = { "Accept-Encoding": "*" } )
        end_time = time.time()
    except Exception as err:
        print( "ERROR: Could not get '{}': {}".format( uri, err ) )
        return

    # Save the resource and other information
    try:
        # Save the resource itself
        if is_csdl:
            with open( index_path, "w", encoding = "utf-8" ) as file:
                file.write( resource.text )
        else:
            save_dict = resource.dict

            # Prune the log entry collection if needed
            if save_dict.get( "@odata.type", None ) == "#LogEntryCollection.LogEntryCollection" and args.maxlogentries is not None:
                if args.maxlogentries < 0:
                    args.maxlogentries = 0
                if "Members@odata.nextLink" in save_dict:
                    save_dict.pop( "Members@odata.nextLink" )
                if "Members" in save_dict:
                    if isinstance( save_dict["Members"], list ):
                        for i in range( 0, len( save_dict["Members"] ) - args.maxlogentries ):
                            save_dict["Members"].pop()
                        save_dict["Members@odata.count"] = len( save_dict["Members"] )

            # The saved copy might contain URI fixes and other changes that aren't reflective of the service, but are
            # needed to ensure compatibility with the system creating the mockup
            scan_dict = copy.deepcopy( save_dict )

            # Add the copyright statement if needed
            if args.Copyright:
                save_dict["@Redfish.Copyright"] = args.Copyright

            # Update the payload's URIs if they need to be corrected based on allowable folder names for the system
            if folder_name_fix or args.forcefolderrename:
                fix_uris( save_dict )

            with open( index_path, "w", encoding = "utf-8" ) as file:
                json.dump( save_dict, file, indent = 4, separators = ( ",", ": " ) )

            # Deep copies of all payloads gets expensive; force garbage collection to avoid stack overflows
            del save_dict
            gc.collect()
    except Exception as err:
        print( "ERROR: Could not save '{}': {}".format( uri, err ) )
        print( "Attempting to save response data in error.txt..." )
        try:
            with open( os.path.join( path, "error.txt" ), "w", encoding = "utf-8" ) as file:
                file.write( "HTTP {}\n".format( resource.status ) )
                for header in resource.getheaders():
                    file.write( "{}: {}\n".format( header[0], header[1] ) )
                file.write( "\n" )
                file.write( resource.text )
        except:
            print( "Could not save response data; moving on... " )
        return

    # Save additional info
    try:
        # Save headers
        if args.Headers:
            with open( os.path.join( path, "headers.json" ), "w", encoding = "utf-8" ) as file:
                headers_dict = {}
                for header in resource.getheaders():
                    headers_dict[header[0]] = header[1]
                json.dump( { "GET": headers_dict }, file, indent = 4, separators = ( ",", ": " ) )

        # Save timing info
        response_times[uri] = end_time - start_time
        if args.Time:
            with open( os.path.join( path, "time.json" ), "w", encoding = "utf-8" ) as file:
                json.dump( { "GET_Time": "{0:.2f}".format( response_times[uri] ) }, file, indent = 4, separators = ( ",", ": " ) )
    except Exception as err:
        print( "ERROR: Could not save header or timing data for '{}': {}".format( uri, err ) )
        return

    # Scan the response to see where to go next
    try:
        if is_csdl:
            scan_csdl( redfish_obj, args, response_times, resource.text )
        else:
            scan_object( redfish_obj, args, response_times, scan_dict )
    except Exception as err:
        print( "ERROR: Could not scan '{}': {}".format( uri, err ) )
        return

def scan_object( redfish_obj, args, response_times, object ):
    """
    Scans an object or array to find links to other resources

    Args:
        redfish_obj: The Redfish client object with an open session
        args: The command line arguments
        response_times: The response times database
        object: The object to scan
    """

    for item in object:
        # If the object is a dictionary, inspect the properties found
        if isinstance( object, dict ):
            # If the item is a reference, go to the resource
            if item == "@odata.id" or item == "Uri" or item == "Members@odata.nextLink" or item == "@Redfish.ActionInfo":
                if isinstance( object[item], str ):
                    if object[item].startswith( "/" ) and "#" not in object[item]:
                        scan_resource( redfish_obj, args, response_times, object[item] )

            # If the item is an object or array, scan one level deeper
            elif isinstance( object[item], dict ) or isinstance( object[item], list ):
                scan_object( redfish_obj, args, response_times, object[item] )

        # If the object is a list, see if the member needs to be scanned
        elif isinstance( object, list ):
            if isinstance( item, dict ) or isinstance( item, list ):
                scan_object( redfish_obj, args, response_times, item )

def scan_csdl( redfish_obj, args, response_times, csdl ):
    """
    Scans a CSDL string to find links to other CSDL files

    Args:
        redfish_obj: The Redfish client object with an open session
        args: The command line arguments
        response_times: The response times database
        csdl: The CSDL string to scan
    """

    # Convert to an element tree object
    tree = ET.ElementTree( ET.fromstring( csdl ) )
    root = tree.getroot()

    # Find references
    for reference in root:
        if "reference" in str( reference.tag ).lower():
            if "Reference" not in str( reference.tag ):
                print( "Warning: Found invalid reference tag '()'; tags are case sensitive!".format( str( reference.tag ) ) )
            for tag in [ "Uri", "uri", "URI" ]:
                uri = reference.attrib.get( tag )
                if uri is not None:
                    if tag != "Uri":
                        print( "Warning: Found invalid Uri attribute '{}'; attributes are case sensitive!".format( tag ) )
                    # Scan the reference
                    scan_resource( redfish_obj, args, response_times, uri, is_csdl = True )

def fix_uris( payload ):
    """
    Updates URIs in a payload to ensure they do not conflict with local system folder name rules

    Args:
        payload: The payload to update
    """

    for item in payload:
        # If the payload is a dictionary, inspect the properties found
        if isinstance( payload, dict ):
            # If the item is a reference, go to the resource
            if item == "@odata.id" or item == "Uri" or item == "Members@odata.nextLink":
                if isinstance( payload[item], str ):
                    for character in disallowed_folder_characters_win:
                        payload[item] = payload[item].replace( character, "_" )

            # If the item is an object or array, scan one level deeper
            elif isinstance( payload[item], dict ) or isinstance( payload[item], list ):
                fix_uris( payload[item] )

        # If the object is a list, see if the member needs to be scanned
        elif isinstance( payload, list ):
            if isinstance( item, dict ) or isinstance( item, list ):
                fix_uris( item )

if __name__ == "__main__":
    sys.exit( main() )
