# Redfish Mockup Creator

Copyright 2016-2020 DMTF. All rights reserved.

## About

The Redfish Mockup Creator is a tool that creates a Redfish mockup from a live Redfish service.
The mockup created can be used with the [Redfish Mockup Server](https://github.com/DMTF/Redfish-Mockup-Server).

## Requirements

If running the mockup server natively on your system:
* Install [Python 3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/)
* Install required Python packages: `pip install -r requirements.txt`

## Usage

```
usage: redfishMockupCreate.py [-h] --user USER --password PASSWORD --rhost
                              RHOST [--Secure] [--Auth {None,Basic,Session}]
                              [--Headers] [--Time] [--Dir DIR]
                              [--Copyright COPYRIGHT]
                              [--description DESCRIPTION] [--quiet]

A tool to walk a Redfish a service and create a mockup from all resources

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The IP address (and port) of the Redfish service

optional arguments:
  -h, --help            show this help message and exit
  --Secure, -S          Use HTTPS for all operations
  --Auth {None,Basic,Session}, -A {None,Basic,Session}
                        Authentication mode
  --Headers, -H         Captures the response headers in the mockup
  --Time, -T            Capture the time of each GET in the mockup
  --Dir DIR, -D DIR     Output directory for the mockup
  --Copyright COPYRIGHT, -C COPYRIGHT
                        Copyright string to add to each resource
  --description DESCRIPTION, -d DESCRIPTION
                        Mockup description to add to the output readme file
  --quiet, -q           Quiet mode; progress messages suppressed

```

Example: `python redfishMockupCreate.py -u root -p root -r 192.168.1.100 -S -D my-mockup`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then walk the service to find all resources and place each resource in directory specified by the *Dir* argument.
If *Dir* is not specified, the output will be "rfMockUpDfltDir".
For every resource found, it will create an "index.json" file in the output directory.
If the *Headers* argument is specified, it will save the response headers for each resource in a "headers.json" file.
If the *Time* argument is specified, it will save the time elapsed for each resource in a "time.json" file. 

## Release Process

Run the `release.sh` script to publish a new version.

```bash
sh release.sh <NewVersion>
```

Enter the release notes when prompted; an empty line signifies no more notes to add.
