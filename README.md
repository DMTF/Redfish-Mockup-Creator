Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.

# redfishMockupCreator

## About
***redfishMockupCreator*** is a python34 program that creates a redfish Mockup folder structure from a real live Redfish service.

The program executes Redfish GET requests to the Redfish service and saves the response in a directory structure like what is used for all Redfish mockups.

As a result, it is a way to take a snapshot of a system

## Usage
* copy the redfishMockupCreate.py file and /redfishtoollib folder (with 2 files) into a folder and execute with Python3.4 or later.
 * Note that this program uses the redfishtool transport and serviceRoot API routines which are in the /redfishtoollib folder
 

### Options
   `redfishMockupCreate  [-VhvqS] -u<user> -p<passwd> -r<rpath> [-A<auth>] [-D<directoryPath>] -d [<descriptionString>]`
    
       -V -- prints version and exits
       -h -- help (gives syntax and usage)
       -v -- verbose (can add more than 1). -v gives addl debug printouts, -vv adds execution tracing, -vvv...,-vvvv...
       -q -- quiet (no output)
       -S -- use https for all transactions
       -u<user>  -- the username for authentication
       -p<passwd>-- the password for authentication
       -r<rpath> -- the IP and port of the remote manager:   eg 127.0.0.1:8001
       -A<auth>  -- the authentication mechanism (same as redfishtool): None, Basic, Session (dflt)
       -D<dirPath>  -- the directory path from program to where the mockup will be created (relative or absolute). 
       the program does not create theh directory. you have to do that ahead of time.
       -d<description> -- <description> is a string that is stored at the top of the mockup directory in a README file 

### Notes
* Since a real redfish service can implement any URI it wants (they don't have to start with /redfish/v1), this creates a "tall mockup".  That is, it starts creating a directory structure with everything below the IP address of the remote service---it therefore includes /redfish/v1 in the directory structure.

* Initial version: 0.9.1  provides mockup tree based on redfish 1.0 schemas.
Some new resources that were added after 1.0 are not included (eg .../Systems/<sysId>/Memory)
* This version does not walk the SPMF schema to find navigation links, but uses a couple of simple structures at the top of the program.   We will add additional navigation properties (eg Memory, Drives,...) in next release.

