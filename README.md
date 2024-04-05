# Redfish Mockup Creator

Copyright 2016-2020 DMTF. All rights reserved.

## About

The Redfish Mockup Creator is a tool that creates a Redfish mockup from a live Redfish service.
The mockup created can be used with the [Redfish Mockup Server](https://github.com/DMTF/Redfish-Mockup-Server).

## Requirements

To run the mockup creator natively on your system:

* Install [Python 3](https://www.python.org/downloads/ "https://www.python.org/downloads/") and [pip](https://pip.pypa.io/en/stable/installing/ "https://pip.pypa.io/en/stable/installing").
* Install required Python packages: `pip install -r requirements.txt`

To run the mockup server as a Docker container:

* Install [Docker](https://www.docker.com/get-started "https://www.docker.com/get-started").

## Usage

```
usage: redfishMockupCreate.py [-h] --user USER --password PASSWORD --rhost
                              RHOST [--Secure] [--Auth {None,Basic,Session}]
                              [--Headers] [--Time] [--Dir DIR]
                              [--Copyright COPYRIGHT]
                              [--description DESCRIPTION] [--quiet]

A tool to walk a Redfish service and create a mockup from all resources

required arguments:
  --user USER, -u USER  The user name for authentication
  --password PASSWORD, -p PASSWORD
                        The password for authentication
  --rhost RHOST, -r RHOST
                        The IP address (and port) of the Redfish service

optional arguments:
  -h, --help            show this help message and exit
  --Dir DIR, -D DIR     Output directory for the mockup; defaults to
                        'rfMockUpDfltDir'
  --Secure, -S          Use HTTPS for all operations
  --Auth {None,Basic,Session}, -A {None,Basic,Session}
                        Authentication mode
  --Headers, -H         Captures the response headers in the mockup
  --Time, -T            Capture the time of each GET in the mockup
  --Copyright COPYRIGHT, -C COPYRIGHT
                        Copyright string to add to each resource
  --description DESCRIPTION, -d DESCRIPTION
                        Mockup description to add to the output readme file
  --quiet, -q           Quiet mode; progress messages suppressed
  --trace, -trace       Enable tracing; creates the file rf-mockup-create.log
                        in the output directory to capture Redfish traces with
                        the service
  --maxlogentries MAXLOGENTRIES, -maxlogentries MAXLOGENTRIES
                        The maximum number of log entries to collect in each
                        log service
  --forcefolderrename, -forcefolderrename
                        Indicates if URIs containing characters that are
                        disallowed in Windows folder names are renamed to
                        replace the characters with underscores
```

Example: `python redfishMockupCreate.py -u root -p root -r 192.168.1.100 -S -D /output`

The tool will log into the service specified by the *rhost* argument using the credentials provided by the *user* and *password* arguments.
It will then walk the service to find all resources and place each resource in directory specified by the *Dir* argument.
If *Dir* is not specified, the output will be "rfMockUpDfltDir".
For every resource found, it will create an "index.json" file in the output directory.
If the *Headers* argument is specified, it will save the response headers for each resource in a "headers.json" file.
If the *Time* argument is specified, it will save the time elapsed for each resource in a "time.json" file. 

Some implementations use URIs that contain characters that are disallowed in Windows folder names.
The tool attempts to discover the OS to determine if these characters should be replaced by underscore characters.
However, in some situations, such as a Docker container running under Windows, it's not possible for the tool to detect this condition.
The *forcefolderrename* argument can be used in these cases to perform this replacement regardless of the detected OS.

## Docker container example

To run as a Docker container, use one of these actions to pull or build the container:

* Pull the container from Docker Hub:

    ```bash
    docker pull dmtf/redfish-mockup-creator:latest
    ```
* Build a container from local source:

    ```bash
    docker build -t dmtf/redfish-mockup-creator:latest .
    ```
* Build a container from GitHub:

    ```bash
    docker build -t dmtf/redfish-mockup-creator:latest https://github.com/DMTF/Redfish-Mockup-Creator.git#main
    ```

This command runs the container with a specified mockup, where `<path-to-mockup>` is the path to the mockup directory:

```bash
docker run --rm --user="$(id -u):$(id -g)" -v <path-to-mockup>:/mockup dmtf/redfish-mockup-creator:latest -u root -p root -r 192.168.1.100 -S
```

## Release Process

1. Go to the "Actions" page
2. Select the "Release and Publish" workflow
3. Click "Run workflow"
4. Fill out the form
5. Click "Run workflow"
