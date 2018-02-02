Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.

# redfishMockupCreator

## About

***redfishMockupCreator*** is a python34 program that creates a redfish Mockup folder structure from a real live Redfish service.  This folder structure can then be mounted under the Redfish-Mockup-Server tool.

The program executes Redfish GET requests to the Redfish service and saves the response in a directory structure like what is used for all Redfish mockups.

As a result, it is a way to take a snapshot of a system

## Usage

* copy the redfishMockupCreate.py file and /redfishtoollib folder (with 2 files) into a folder and execute with Python3.4 or later.
* Note that this program uses the redfishtool transport and serviceRoot API routines which are in the /redfishtoollib folder

### Options

```
   redfishMockupCreate  [-VhvqS] -u<user> -p<passwd> -r<rpath> [-A<auth>] [-D<directoryPath>] -d [<descriptionString>]
   -V,          --version             -- show redfishMockupCreate version, and exit
   -h,          --help                -- show Usage, Options
   -v,          --verbose             -- verbose level, can repeat up to 4 times for more verbose output
   -q,          --quiet               -- quiet mode. no progress messages are displayed
   --custom                           -- custom mode. use static nav structure instead of recursive algorithm
   -C <string>, --Copyright=<string>  -- Add Copyright message. The specified Copyright will be added to each resource
   -H,          --Headers             -- Headers mode. An additional headers property will be added to each resource
   -T,          --Time                -- Time mode. Retrieval time of each GET will be captured
   -S,          --Secure              -- use HTTPS for all gets.   otherwise HTTP is used
   -u <user>,   --user=<usernm>       -- username used for remote redfish authentication
   -p <passwd>, --password=<passwd>   -- password used for remote redfish authentication
   -r <rhost>,  --rhost=<rhost>       -- remote redfish service hostname or IP:port
   -A <Auth>,   --Auth=<auth>         -- auth method ot use: None, Basic(dflt), Session
   -M           --ScrapeMetadata      -- Scrape XML stored locally on the server 
   -D <directory>,--Dir=<directory>   -- output mockup to directory path <directory>
   -d <description> --description=<d> -- text description that is put in README. ex: -d "mockup of Contoso 1U"
```

##  Python Requirement

**The `requests` package is required.**

- On Windows, navigate to your Python folder via CMD.

    `cd C:\Python36\`

- run the command line

    `python -m pip install requests`

##  Example

### Create a directory that is the name of the mockup you are creating

* fyi-mockup-creator wont create the directory, if the dir doesn’t exist, it exits with error
* fyi-also, it won’t over-write the data in an existing directory--if you want to re-run and store the mockup in the same directory, you have to remove all of the files under the dir so make the directory under mymockups

`cd $HOME/mymockups && mkdir C6320mockup9`

### Now run the creator

* Assuming you downloaded the Redfish-Mockup-Creator to $HOME/redfishtools/Redfish-Mockup-Creator

`cd $HOME/redfishtools/Redfish-Mockup-Creator`

* Make sure you have python3.4 or later in your path
* Set the IP address of the Redfish server you are going to get the mockup from
    * MYC6320IP=129.168.0.9  #ex

`python3.4 ./redfishMockupCreate.py -r $MYC6320IP -u root -p calvin -S -A Basic -D "$HOME/mymockups/C6320mockup9" \
          -d "this is my mockup of a real C6320 in rack33" -C "Copyright 2016 Contoso.com Inc. All rights reserved."`

     -r <ip> is the ip address of the server you are pulling the mockup from
     -u, -p is user/password
     -S   (it’s a capital S) tells it to use HTTPS for everything---powerEdge requires HTTPS.
     -A Basic    says use basic auth (I think that’s the default, the man page says Session is dflt ,but just specify Basic to be sure)
     -D <dir>   tells it the directory to put it in.---must be empty and must already exist
     -d <descriptionString>   is a short description you can add that it appends to the READ file  at the top of the mockup.`

## Notes

* Since a real redfish service can implement any URI it wants (they don't have to start with /redfish/v1), this creates a "tall mockup".  That is, it starts creating a directory structure with everything below the IP address of the remote service---it therefore includes /redfish/v1 in the directory structure.
* Initial version: 0.9.1  provides mockup tree based on redfish 1.0 schemas.  Some new resources that were added after 1.0 are not included (eg .../Systems/<sysId>/Memory)
* This version does not walk the SPMF schema to find navigation links, but uses a couple of simple structures at the top of the program.  We will add additional navigation properties (eg Memory, Drives,...) in next release.
