# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Mockup-Creator/LICENSE.md

# redfishMockupCreate
#
# contains:
#
import os
import sys
import getopt
import json
from redfishtoollib  import RfTransport
# uses same transport that is used by redfishtool.
# only the program name, date, and version is changed
import errno
import datetime
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


# rootservice navigation properties
rootLinks=["Systems","Chassis","Managers", "SessionService", "AccountService", "Registries",
        "JsonSchemas", "Tasks", "EventService", "UpdateService"]
# list of navigation properties for each root service nav props
resourceLinks={
        # rootResource: [list of sub-resources],
        "Systems": [ "Processors", "SimpleStorage", "EthernetInterfaces", "LogServices",
                    "Memory", "NetworkInterfaces", "SecureBoot", "Bios", "PCIeDevices", "MemoryDomains", "Storage"],
        "Chassis": ["Power", "Thermal", "LogServices"],
        "Managers": ["NetworkProtocol", "EthernetInterfaces", "SerialInterfaces", "LogServices", "VirtualMedia"],
        "SessionService": ["Sessions"],
        "AccountService": ["Accounts", "Roles"],
        "Registries": [],
        "JsonSchemas": [],
        "Tasks": ["Tasks"],
        "EventService": ["Subscriptions"],
        "UpdateService": []
}

def displayUsage(rft,*argv,**kwargs):
        rft.printErr("  Usage:",noprog=True)
        rft.printErr("   {} [-VhvqS] -u<user> -p<passwd> -r<rhost[<port>] [-A <auth>] [-D <dir>]",prepend="  ")
        rft.printErr("   where -S is https",     prepend="  ")

def displayOptions(rft):
        print("")
        print("  Common OPTIONS:")
        print("   -V,              --version            -- show {} version, and exit".format(rft.program))
        print("   -h,              --help               -- show Usage, Options".format(rft.program))
        print("   -v,              --verbose            -- verbose level, can repeat up to 4 times for more verbose output")
        print("   -q,              --quiet              -- quiet mode. no progress messages are displayed")
        print("   --custom         --                   -- custom mode. use static nav structure instead of recursive algorithm")
        print("   -C <string>,     --Copyright=<string> -- Add Copyright. The specified Copyright will be added to each resource")
        print("   -H,              --Headers            -- Headers mode. An additional headers property will be added to each resource")
        print("   -T,              --Time               -- Time mode. Retrieval time of each GET will be captured")
        print("   -S,              --Secure             -- use HTTPS for all gets.   otherwise HTTP is used")
        print("   -u <user>,       --user=<usernm>      -- username used for remote redfish authentication")
        print("   -p <passwd>,     --password=<passwd>  -- password used for remote redfish authentication")
        print("   -r <rhost>,      --rhost=<rhost>      -- remote redfish service hostname or IP:port")
        print("   -A <Auth>,       --Auth=<auth>        -- auth method ot use: None, Basic(dflt), Session ")
        print("   -D <directory>,  --Dir=<directory>    -- output mockup to directory path <directory>")
        print("   -d <description> --description=<d>    -- text description that is put in README. ex: -d \"mockup of Contoso 1U\" ")

        print("")





def addHeaderFile(addHeaders, r, dirPath):
#Store headers into the headers.json
    rc = 0
    if (addHeaders is True):
        hdrsFilePath = os.path.join(dirPath, "headers.json")
        with open(hdrsFilePath, 'w', encoding='utf-8') as hf:
            dictHeader = dict(r.headers)
            headerFileData = {"GET":dictHeader}
            rc = json.dump(headerFileData, hf, indent=4)
    return rc

allResponseTimes = {}

def genTimeStatistics(mockupDir):
    # Using all previous response times, generate statistics
    results = {
            'minResponseTime': (9999, None),
            'maxResponseTime': (0, None),
            'averageResponseTime': 0,
            'totalResponseTime': 0
            }

    if len(allResponseTimes) < 1:
        return {}

    for item in allResponseTimes:
        time = allResponseTimes[item]
        uri = item.replace(mockupDir, '')
        results['totalResponseTime'] += time
        results['minResponseTime'] = (time, uri) if time < results['minResponseTime'][0] else results['minResponseTime']
        results['maxResponseTime'] = (time, uri) if time > results['maxResponseTime'][0] else results['maxResponseTime']

    results['averageResponseTime'] = round(results['totalResponseTime'] / len(allResponseTimes), 3)
    results['totalResponseTime'] = round(results['totalResponseTime'], 3)
    results['minResponseTime'] = (round(results['minResponseTime'][0], 3), results['minResponseTime'][1])
    results['maxResponseTime'] = (round(results['maxResponseTime'][0], 3), results['maxResponseTime'][1])
    return results

def addTimeFile(addTime, addHeaders, rft, r, dirPath):
    rc = 0
    if (addTime is True):
        timeFilePath = os.path.join(dirPath, "time.json")
        with open(timeFilePath, 'w', encoding='utf-8') as tf:
            allResponseTimes[dirPath] = rft.elapsed
            elapsedTime = '{0:.2f}'.format(rft.elapsed)
            timeFileData = {"GET_Time":elapsedTime}
            if (addHeaders is True):
                elapsedHeadTime = '{0:.2f}'.format(r.elapsed.total_seconds())
                timeFileData['HEAD_Time'] = elapsedHeadTime
            rc = json.dump(timeFileData, tf, indent=4)
    return rc

def main(argv):
    # Resource, links used to drive the mockup creation
    # in future, mockupCreate could follow schemas, but initial 1.0 uses these


    # program flow:
    #
    # parse main options
    # write README file to top of mockup directory
    # create /redfish, /redfish/v1, /redfish/v1/odata, and /redfish/v1/$metadata folders/files
    # create $metadata resources
    # create folders/files for apis under root
    #  for res in rootLinks:  (eg Systems, AccountService)
    #    mkdir ./res
    #    CreateIndexFile(./res/index.json)     --- read,write to index.json
    #    if(type is collection)  (eg Systems, Chassis)
    #      for each member,
    #        mkdir, create index.json
    #        subLinks=resourceLinks[res]  
    #        for res2 in sublinks:    (eg Processors, LogService, Power)
    #           mkdir ./res/res2, CreateIndexFile(./res/res2/index.json)
    #           if(type is collection)  (eg Processors)
    #               for each member, mkdir, create index.json
    #               if(type is LogService)
    #                   mkdir ./res/res2/member
    #                   CreateIndexFile for log Entries
    #   else //not a collection (eg AccountService)
    #        for res2 in sublinks:    (eg Accounts)
    #           mkdir ./res/res2, CreateIndexFile(./res/res2/index.json)
    #           if(type is collection)  (eg Accounts, Sessions)
    #               for each member, mkdir, create index.json


    #instantiate transport object which initializes default options
    #    this is the same transport that is used by redfishtool, with program=redfishMockupCreate
    rft=RfTransport()

    # set default verbose level to 1.  so -v will cause verbose level to go to 2
    rft.verbose=1
    rft.program="redfishMockupCreate"
    rft.version="1.0.0"
    rft.releaseDate="02/02/2018"
    rft.secure="Never"
    rft.waitTime=5
    rft.timeout=20

    #initialize properties used here in main
    absPath=None
    mockDirPath=None
    mockDir=None
    defaultDir="rfMockUpDfltDir"
    description=""
    rfFile="index.json"
    rfFileHeaders="headers.json"
    rfFileTime="time.json"
    custom=False
    addCopyright=None
    addHeaders=False
    addTime=False
    scrapeMetadata=False
    #Exception List required given Dell 13g iDRAC does not include odata.type with expanded Log
    exceptionList = ['iDRAC.Embedded.1/Logs/']

    try:
        opts, args = getopt.gnu_getopt(argv[1:],"VhvqMSHTu:p:r:A:C:D:d:",
                        ["Version", "help", "quiet", "ScrapeMetadata", "Secure=",
                         "user=", "password=", "rhost=","Auth=",
                         "custom", "Copyright=", "Headers", "Time", "Dir=, description=]"])
    except getopt.GetoptError:
        rft.printErr("Error parsing options")
        displayUsage(rft)
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            rft.help=True
            displayUsage(rft)
            displayOptions(rft)
            sys.exit(1)
        elif opt in ("-V", "--version"):
            print("{} Version: {}".format(rft.program, rft.version))
            sys.exit(0)
        elif opt in ("-v"):
            rft.verbose = min((rft.verbose+1), 5)
        elif opt in ("-u", "--user"):
            rft.user=arg
        elif opt in ("-p", "--password"):
            rft.password=arg
        elif opt in ("-r", "--rhost"):
            rft.rhost=arg
        elif opt in ("-D", "--Dir"):
            mockDirPath=arg
        elif opt in ("-d", "--description"):
            description=arg
        elif opt in ("-S", "--Secure"):
            rft.secure="Always"
        elif opt in ("-q", "--quiet"):
            rft.quiet=True
        elif opt in ("--custom"):
            custom=True
        elif opt in ("-C", "--Copyright"):
            addCopyright=arg
        elif opt in ("-H", "--Headers"):
            addHeaders=True
        elif opt in ("-M", "--ScrapeMetadata"):
            scrapeMetadata=True
        elif opt in ("-T", "--Time"):
            addTime=True
        elif opt in ("-A", "--Auth"):           # specify authentication type
            rft.auth=arg
            if not rft.auth in rft.authValidValues:
                rft.printErr("Invalid --Auth option: {}".format(rft.auth))
                rft.printErr("   Valid values: {}".format(rft.authValidValues),noprog=True)
                sys.exit(1)
        else:
            rft.printErr("Error: Unsupported option: {}".format(opt))
            displayUsage(rft)
            sys.exit(1)

    if( rft.rhost is None):
        rft.printErr("Error: -r rHost was not specified and is required by this command. aborting")
        displayUsage(rft)
        displayOptions(rft)
        sys.exit(1)
    if( rft.user is None):
        rft.printErr("Error: -u user was not specified and is required. aborting")
        displayUsage(rft)
        displayOptions(rft)
        sys.exit(1)
    if( rft.password is None):
        rft.printErr("Error: -p password was not specified and is required. aborting")
        displayUsage(rft)
        displayOptions(rft)
        sys.exit(1)


    rft.printVerbose(5,"Main: verbose={}, User={}, Password={}, rhost={}".format(rft.verbose,
                                                        rft.user,rft.password,rft.rhost))
    rft.printVerbose(5,"Main: Auth={}, quiet={}, Secure={}, Dir={} timeout={}".format(rft.token,
                                            rft.auth, rft.quiet, rft.secure, mockDirPath, rft.timeout))

    rft.printVerbose(5,"Main: options parsed.  Now lookup subcommand and execute it")

    # verify we can talk to the rhost
    rc,r,j,d=rft.getVersions(rft,cmdTop=True)
    if( rc != 0 ):
        rft.printErr("ERROR: Cant find Redfish Service at rhost sending GET /redfish  request. aborting")
        sys.exit(1)

    # If directory was specified, check and create; Otherwise do the same the default directory
    if mockDirPath is not None:
        mockDir=os.path.realpath(mockDirPath)
        #  If the dir exists and non-empty fail 
        if os.path.isdir(mockDir) and os.listdir(mockDir):
            rft.printErr("ERROR: Directory not empty...faint-heartedly refusing to create mockup")
            sys.exit(1)
        # Else create it or fail    
        elif( rfMakeDir(rft, mockDir) is False ):
            rft.printErr("ERROR: cant create /redfish directory. aborting")
            sys.exit(1)
    else:
        mockDirPath=os.path.join(os.getcwd(), defaultDir) #Directory created is "MockCrDfltDir"
        mockDir=os.path.realpath(mockDirPath)
        if os.path.isdir(mockDir) and os.listdir(mockDir):
            rft.printErr("ERROR: Directory not empty...faint-heartedly refusing to create mockup")
            sys.exit(1)
        elif( rfMakeDir(rft, mockDir) is False ):
            rft.printErr("ERROR: cant create /redfish directory. aborting")
            sys.exit(1)

    # print out rhost and directory path
    rft.printVerbose(1,"rhost: {}".format(rft.rhost))
    rft.printVerbose(1,"full directory path: {}".format(mockDir))
    rft.printVerbose(1,"description: {}".format(description))
    rft.printVerbose(1,"starting mockup creation")

    readmeFile=os.path.join(mockDir, "README")

    rfdatetime=str(datetime.datetime.now())
    rfdatetime=rfdatetime.split('.',1)[0]
    with open(readmeFile, 'w', encoding='utf-8') as readf:
        readf.write("Redfish Service state stored in Redfish Mockup Format\n")
        readf.write("Program: {},  ver: {}\n".format(rft.program, rft.version))
        readf.write("Created: {}\n".format(rfdatetime))
        readf.write("rhost:  {}\n".format(rft.rhost))
        readf.write("Description: {}\n".format(description))
        readf.write("Commandline: {} {}\n".format('python3.4', ' '.join(argv)))
    if os.path.isfile(readmeFile) is False:
        rft.printErr("ERROR: cant create README file in directory. aborting")
        sys.exit(1)

    #create a ^/redfish directory.  Exit if one already exists--that is an error
    rft.printVerbose(1,"Creating /redfish resource")
    dirPath=os.path.join(mockDir, "redfish")
    if( rfMakeDir(rft, dirPath) is False ):
        rft.printErr("ERROR: cant create /redfish directory. aborting")
        sys.exit(1)

    #copy the versions output to ^/redfish/index.json
    filePath=os.path.join(dirPath,rfFile)
    with open( filePath, 'w', encoding='utf-8' ) as f:
        f.write(r.text)
    #Add copyright key/value pair into index.json
    if (addCopyright is not None):
        if(type(d) is dict):
            d['@Redfish.Copyright'] = addCopyright
        else:
            rft.printErr("BUG: Expecting a dictionary for resource {} but got type: {}".format(absPath, type(d)))
    #Store resource dictionary into index.json
    filePath=os.path.join(dirPath,"index.json")
    with open( filePath, 'w', encoding='utf-8' ) as f:
        json.dump(d, f, indent=4)

    addHeaderFile(addHeaders, r, dirPath)

    #Store elapsed response time into time.json
    addTimeFile(addTime, addHeaders, rft, r, dirPath)

    #create the /redfish/v1 root dir and copy output of Get ^/redfish/v1 to index.json file
    rft.printVerbose(1,"Creating /redfish/v1 resource")
    rc,r,j,d=rft.rftSendRecvRequest(rft.UNAUTHENTICATED_API, 'GET', r.url, relPath=rft.rootPath)
    rootv1data = d
    if(rc!=0):
        rft.printErr("ERROR: Cant read root service:  GET /redfish/ from rhost. aborting")
        #print r.status_code for more info on failure
        rft.printErr("Status Code: {} ".format(r.status_code))
        sys.exit(1)
    dirPath=os.path.join(mockDir, "redfish", "v1")
    if( rfMakeDir(rft, dirPath) is False ):
        rft.printErr("ERROR: cant create /redfish/v1 directory. aborting")
        sys.exit(1)
    filePath=os.path.join(dirPath,rfFile)
    with open( filePath, 'w', encoding='utf-8' ) as f:
        f.write(r.text)
    #Add copyright key/value pair into index.json
    if (addCopyright is not None):
        if(type(d) is dict):
            d['@Redfish.Copyright'] = addCopyright
        else:
            rft.printErr("BUG: Expecting a dictionary for resource {} but got type: {}".format(absPath, type(d)))
    #Store resource dictionary into index.json
    filePath=os.path.join(dirPath,"index.json")
    with open( filePath, 'w', encoding='utf-8' ) as f:
        json.dump(d, f, indent=4)

    addHeaderFile(addHeaders, r, dirPath)

    #Store elapsed response time into time.json
    addTimeFile(addTime, addHeaders, rft, r, dirPath)

    #save the rootURL for later re-use  (if we were redirected, we get the redirected url here)
    rootUrl=r.url
    rootRes=d

    #get /redfish/v1/odata and save to mockup
    rft.printVerbose(1,"Creating /redfish/v1/odata resource")
    api="odata"
    rc,r,j,d=rft.rftSendRecvRequest(rft.UNAUTHENTICATED_API, 'GET', rootUrl, relPath=api, jsonData=True )
    if(rc!=0):
        rft.printErr("ERROR: Cant read mandatory API: /redfish/v1/odata. Continuing w/o creating mockup entry")
    else:
        dirPath=os.path.join(mockDir, "redfish", "v1", api)
        if( rfMakeDir(rft, dirPath) is False ):
            rft.printErr("ERROR: cant create directory: /redfish/v1/{}. aborting".format(api))
            sys.exit(1)
        filePath=os.path.join(dirPath,rfFile)
        with open( filePath, 'w', encoding='utf-8' ) as f:
            f.write(r.text)
        #Add copyright key/value pair into index.json
        if (addCopyright is not None):
            if(type(d) is dict):
                d['@Redfish.Copyright'] = addCopyright
            else:
                rft.printErr("BUG: Expecting a dictionary for resource {} but got type: {}".format(absPath, type(d)))
    #Store resource dictionary into index.json
    filePath=os.path.join(dirPath,"index.json")
    with open( filePath, 'w', encoding='utf-8' ) as f:
        json.dump(d, f, indent=4)

    #Store headers into the headers.json
    addHeaderFile(addHeaders, r, dirPath)

    #Store elapsed response time into time.json
    addTimeFile(addTime, addHeaders, rft, r, dirPath)

    #get /redfish/v1/$metadata and save to mockup.   Note this is an .xml file stored as index.xml in mockup
    rft.printVerbose(1,"Creating /redfish/v1/$metadata resource")
    api="$metadata"
    # set content-type to xml  (dflt is application/json)
    hdrs = {"Accept": "application/xml", "OData-Version": "4.0" }
    rc,r,j,d=rft.rftSendRecvRequest(rft.UNAUTHENTICATED_API, 'GET', rootUrl, relPath=api, jsonData=False,
                                    headersInput=hdrs)
    if(rc!=0):
        rft.printErr("ERROR: Cant read mandatory API: /redfish/v1/$metadata. Continuing w/o creating mockup entry")
    else:
        dirPath=os.path.join(mockDir, "redfish", "v1", api)
        if( rfMakeDir(rft, dirPath) is False ):
            rft.printErr("ERROR: cant create directory: /redfish/v1/{}. aborting".format(api))
            sys.exit(1)
        filePath=os.path.join(dirPath,"index.xml")
        with open( filePath, 'w', encoding='utf-8' ) as f:
            f.write(r.text)
        if scrapeMetadata:
            try:
                tree = ET.ElementTree(ET.fromstring(r.text))
                root = tree.getroot()
            except Exception:
                rft.printErr("ERROR: cant parse /redfish/v1/$metadata, cannot scrape the metadata for xml".format(str(ref.tag)))
                root = []
            # start at edmx -> reference
            for ref in root:
                if 'Reference' not in str(ref.tag):
                    if 'reference' in str(ref.tag).lower():
                        rft.printErr("Warning: $metadata tags are Case-Sensitive, found: {}".format(str(ref.tag)))
                    else:
                        continue
                for tag in ['uri', 'Uri', 'URI']:
                    if tag != 'Uri':
                        rft.printErr("Warning: Uri attribute is case-sensitive, found: {}".format(str(tag)))
                    uri = ref.attrib.get(tag)
                    if uri is not None:
                        break
                if not bool(urlparse(uri).netloc):
                    # gets if uri is local
                    dirPath=os.path.join(mockDir, *uri.split('/')[:-1])
                    if( rfMakeDir(rft, dirPath) is False ):
                        rft.printErr("ERROR: cant create directory: {}. aborting".format(dirPath))
                        sys.exit(1)
                    rc,innerr,j,d=rft.rftSendRecvRequest(rft.UNAUTHENTICATED_API, 'GET', rootUrl, relPath=uri, jsonData=False,
                                                    headersInput=hdrs)
                    if(rc!=0):
                        rft.printErr("ERROR: Cant get {}, continuing w/o".format(uri))
                    else:
                        rft.printVerbose(1,"Start Creating service xml: {}".format(uri))
                        filePath=os.path.join(mockDir, *uri.split('/'))
                        with open( filePath, 'w', encoding='utf-8' ) as f:
                            f.write(innerr.text)

    # now make create subdirectories for rootService
    # for res in rootLinks:
    #    read the res
    #    mkdir ./res
    #    CreateIndexFile(./res/index.json)     --- read,write to index.json
    #    if(type is collection)
    #        for each member, mkdir, create index.json

    # for res in rootLinks:
    #    mkdir ./res
    #    CreateIndexFile(./res/index.json)     --- read,write to index.json
    #    if(type is collection)
    #        for each member, mkdir, create index.json
    


    rft.printVerbose(1,"Start Creating resources under root service:")

    # If we specified "Custom" in optargs then run static discovery of resources
    if( custom is True):
        rft.printVerbose("Custom discovery of resources under root service specified")

        for rlink in rootLinks:
            #rft.printErr("rlink:{}".format(rlink))
            if(rlink in rootRes):
                link=rootRes[rlink]
                rft.printVerbose(1,"   Creating resource under root service navigation property: {}".format(rlink))
                rc,r,j,d=readResourceMkdirCreateIndxFile(rft, rootUrl, mockDir, link, addCopyright, addHeaders, addTime)
                if(rc!=0):
                    rft.printErr("ERROR: got error reading root service resource--continuing. link: {}".format(link))
                resd=d
                # if res type is a collection, then for each member, read res, mkdir, create index file
                if isCollection(resd) is True:  # (eg Systems, Chassis...)
                    for member in resd["Members"]:
                        rft.printVerbose(4,"    Collection member: {}".format(member))
                        rc,r,j,d=readResourceMkdirCreateIndxFile(rft,rootUrl, mockDir, member, addCopyright, addHeaders, addTime)
                        if(rc!=0):
                            rft.printErr("ERROR: got error reading root service collection member--continuing. link: {}".format(member))
                        memberd=d
                        sublinklist=resourceLinks[rlink]
                        rc,r,j,d=addSecondLevelResource(rft, rootUrl,mockDir, sublinklist, memberd, addCopyright, addHeaders, addTime)
                        if(rc!=0):
                            rft.printErr("ERROR: Error processing 2nd level resource (8)--continuing. link:{}".format(member))
                else:   # its not a collection. (eg accountService) do the 2nd level resources now
                    sublinklist=resourceLinks[rlink]
                    rc,r,j,d=addSecondLevelResource(rft, rootUrl, mockDir, sublinklist, resd, addCopyright, addHeaders, addTime)
                    if(rc!=0):
                        rft.printErr("ERROR: Error processing 2nd level resource (9) --continuing")
    else:
        # Starting recursive call.
        processed = set()
        recursive_call(rft, rootv1data, rootUrl, mockDir, processed, addCopyright, addHeaders, addTime,exceptionList)

    if addTime:
        stats = genTimeStatistics(mockDir)
        with open(readmeFile, 'a', encoding='utf-8') as readf:
            for item in stats:
                print("{}: {}\n".format(item, stats[item]))
                readf.write("{}: {}\n".format(item, stats[item]))

    rft.printVerbose(1," {} Completed creating mockup".format(rft.program))
    sys.exit(0)


def recursive_call(rft, rs, rootUrl, mockDir, processed, addCopyright, addHeaders, addTime, exceptionList):
    # get_nav_and_collection_properties() method will go and fetch any nav or collection properties if present.
    # If none returns None. Indicating that there are no further down navigations.
    d = get_nav_and_collection_properties(rft, rs,exceptionList)
    if d is not None:
        for x in d:
            if '@odata.id' in x:
                link = x.get('@odata.id')
                if link in processed:
                    rft.printVerbose(1, "   Skipping already processed resource at: {}".format(link))
                    continue
                else:
                    processed.add(link)
            rft.printVerbose(1,"   Creating resource at: {}".format(x["@odata.id"]))
            # readResourceMkdirCreateIndxFile(addCopyright, addHeaders, addTime, ) method will create a directory and index.json file for the resource link
            rc,r,j,d=readResourceMkdirCreateIndxFile(rft,rootUrl, mockDir, x, addCopyright, addHeaders, addTime)
            if(rc!=0):
                rft.printErr("ERROR: got error reading resource --continuing. link: {}".format(x))    
            # Recursively calling further tree nodes which will fetch data.
            recursive_call(rft, d, rootUrl, mockDir, processed, addCopyright, addHeaders, addTime, exceptionList)
    else:
        return (None)


def get_location_uri_as_odata_id(rft, location):
    rft.printVerbose(2, '   Processing location resource {}'.format(location))
    odata_id = None
    if 'Uri' in location:
        uri = location.get('Uri')
        if isinstance(uri, str):
            rft.printVerbose(2, '   Found Location Uri {} in resource'.format(uri))
            odata_id = {'@odata.id': uri}
    return odata_id


def get_items(rs):
    """
    Generator function that recursively finds all key/value pairs in the given resource (dictionary)
    :param rs: resource (dictionary) to inspect
    :return: list of key/value pairs found in resource
    """
    for k, v in rs.items():
        if isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    yield from get_items(x)
        elif isinstance(v, dict):
            yield from get_items(v)
        yield (k, v)


def get_nav_and_collection_properties(rft,rs, exceptionList):    
    if not isinstance(rs,dict):
        return (None)
    if "@odata.id" not in rs:
        return (None)
    nav_list = list()
    rs_type = None
    if '@odata.type' in rs:
        _, _, rs_type = rft.parseOdataType(rft, rs)
    location_uri_type_list = ['JsonSchemaFile', 'MessageRegistryFile']
    # Seperate rule for Exception list. 
    if ( any(x in rs['@odata.id']  for x in exceptionList ) ) :
        if isCollection(rs):
            for k,v in rs.items():
                if k == 'Members' and isinstance(v,list):
                    for i in v:
                        if '@odata.id' in i:
                            nav_list.append(i)
    else:
        for k, v in get_items(rs):
            rft.printVerbose(2, '   Checking for nav properties in item with k = {}, v = {}'.format(k, v))
            # Checking if values have keys "@odata.id" only or not.
            if isinstance(v,list):
                for x in v:
                    if isinstance(x,dict):
                        # This is to make sure there is only one key-value pair and it has "@odata.id" as key
                        if len(x) == 1 and '@odata.id' in x.keys():
                            nav_list.append(x)
                        elif len(x) >1 and '@odata.type' in x:
                            ns,ver,resType=rft.parseOdataType(rft,x)
                            if resType == 'LogEntry':
                                nav_list.append(x)
                        # handle case of location uri references to JSON schemas and messages registries
                        elif k == 'Location' and rs_type in location_uri_type_list:
                            odata_id = get_location_uri_as_odata_id(rft, x)
                            if odata_id is not None:
                                rft.printVerbose(2, '   Appending {} to nav_list'.format(odata_id))
                                nav_list.append(odata_id)

            elif isinstance(v,dict):
                # This is to make sure there is only one key-value pair and it has "@odata.id" as key
                if len(v) == 1 and '@odata.id' in v.keys():
                    nav_list.append(v)
                elif len(v) >1 and '@odata.type' in v:
                    ns,ver,resType=rft.parseOdataType(rft,v)
                    if resType == 'LogEntry':
                        nav_list.append(v)
    
    if not nav_list:
        return (None)                   # If the list is empty, it means there are no navigation properties.
    else:
        return (nav_list)               # Returns a list of navigation properties, if they are present.


def rfMakeDir(rft, dirPath):
    success=True
    try:
        os.makedirs(dirPath)
    except OSError as ee:
        if( ee.errno == errno.EEXIST):
            #rft.printErr("ERROR: rfMakeDir: Directory: already exists. aborting")
            #rft.printErr("Directory: {} ".format(dirPath),noprog=True,prepend="            ")
            #It's ok if the path is already created from a previous URL
            success=True
        else:
            rft.printErr("ERROR: rfMakeDir: Error creating directory: {}".format(ee.errno))
            success=False
    return(success)



def readResourceMkdirCreateIndxFile(rft, rootUrl, mockDir, link, addCopyright, addHeaders, addTime, jsonData=True):
    #print("building resource tree for link: {}".format(link))
    if not "@odata.id" in link:
        rft.printErr("ERROR:readResourceMkdirCreateIndxFile: no @odata.id property in link: {}".format(link))
        return(5,None,False, None)

    absPath=link["@odata.id"]
    if(absPath[0]=='/'):
        relPath=absPath[1:]
    else:
        relPath=absPath

    # read the resource.


    rc,r,j,d=rft.rftSendRecvRequest(rft.AUTHENTICATED_API, 'GET', rootUrl, relPath=absPath, jsonData=jsonData )
    if(rc!=0):
        rft.printErr("ERROR:readResourceMkdirCreateIndxFile: Error reading resource: link:{}".format(link))
        return(5,r,False, None)

    dirPath=os.path.join(mockDir, relPath)
    if( rfMakeDir(rft, dirPath) is False ):
        rft.printErr("ERROR:readResourceMkdirCreateIndxFile: for link:{}, path:{}, cant create directory: {}. aborting".format(link,absPath,dirPath))
        return(5,r,False, None)

    # Before storing header,time,etc files; Check if index file exists, if so we have some problem
    filePath=os.path.join(dirPath,"index.json")
    if os.path.isfile(filePath) is True:
        rft.printErr("ERROR: index.json file already exists in this directory {} --continuing".format(filePath))

    #Store headers into the headers.json
    addHeaderFile(addHeaders, r, dirPath)

    #Store elapsed response time into time.json
    addTimeFile(addTime, addHeaders, rft, r, dirPath)

    #Add copyright key/value pair into index.json
    if (addCopyright is not None):
        if(type(d) is dict):
            d['@Redfish.Copyright'] = addCopyright
        else:
            rft.printErr("BUG: Expecting a dictionary for resource {} but got type: {}".format(absPath, type(d)))
    #Store resource dictionary into index.json
    filePath=os.path.join(dirPath,"index.json")
    with open( filePath, 'w', encoding='utf-8' ) as f:
        json.dump(d, f, indent=4) 

    return(rc, r, j, d )




# sublinklist=resourceLinks[rlink]
def addSecondLevelResource(rft, rootUrl, mockDir, sublinklist, resd, addCopyright, addHeaders, addTime):
    if( len(sublinklist)==0 ):
        return(0,None,False,None)
    rc, r, j, d = 0, None, False, None
    for rlink2 in sublinklist:   #(ex Processors, Power)
        if( rlink2 in resd):
            link2=resd[rlink2]
            rft.printVerbose(4,"        Creating sub-property: {}".format(rlink2))
            rc,r,j,d=readResourceMkdirCreateIndxFile(rft,rootUrl, mockDir, link2, addCopyright, addHeaders, addTime, jsonData=True)
            if(rc!=0):
                rft.printErr("ERROR: got error reading 2nd level resource--continuing. link: {}".format(link2))
                return(rc,r,j,d)
            resd2=d
            # if collection, then get its members
            if isCollection(resd2) is True:  #ex Processors, get /1, /2
                for member2 in resd2["Members"]:
                    rft.printVerbose(4,"          Creating 2nd-level Collection member: {}".format(member2))
                    rc,r,j,d=readResourceMkdirCreateIndxFile(rft, rootUrl, mockDir, member2, addCopyright, addHeaders, addTime, jsonData=True)
                    resd3=d
                    if(rc!=0):
                        rft.printErr("ERROR: got error reading 2nd level collection member--continuing. link: {}".format(member2))
                        break
                    #if resource type is LogService, then get the entries expanded collection
                    ns,ver,resType=rft.parseOdataType(rft,resd3)
                    if( resType=="LogService" ):
                        if( "Entries" in resd3):
                            entriesLink=resd3["Entries"]
                            rft.printVerbose(2,"               Creating LogService Entries (Expanded Collection): {}".format(member2))
                            rc,r,j,d=readResourceMkdirCreateIndxFile(rft, rootUrl, mockDir, entriesLink, addCopyright, addHeaders, addTime, jsonData=True)
                            if(rc!=0):
                                rft.printErr("ERROR: got error reading logService Entries collection resource--continuing. link: {}".format(entriesLink))
        else:
            rft.printVerbose(2,"       No sub-properties in resource: {}")
            return(0,None,False,None)

    return(rc,r,j,d)





def isCollection(resource):
    if "Members" in resource:
        return True   # its a collection if it has a Members array  (sort of cheating)
    else:
        return False



if __name__ == "__main__":
    main(sys.argv)


'''

'''



