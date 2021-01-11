# Change Log

## [1.0.9] - 2021-01-11
- Added Dockerfile

## [1.0.8] - 2020-12-04
- Replaced internal copy of redfishtoollib to leverage the python-redfish-library

## [1.0.7] - 2020-10-30
- Made enhancement to skip resources not containing `@odata.id` instead of crashing
- Removed password from readme file generation

## [1.0.6] - 2020-10-19
- Made enhancements to be able to create a mockup of a server with a malformed `/redfish` resource

## [1.0.5] - 2019-08-09
- Added check to avoid parsing the resources that are referenced by Location properties

## [1.0.4] - 2019-06-21
- Made change to allow for `/redfish` to not be present on the service, but report an error if not found

## [1.0.3] - 2018-11-30
- Fixed checking of Uri tag in CSDL files hosted by a service

## [1.0.2] - 2018-09-21
- Fixed bug in nextLink handling
- Synched redfishtoolTransport.py with latest version from redfishtool

## [1.0.1] - 2018-08-03
- Fixed print statement usage for when an error is encountered while accessing $metadata
- Reformatted code to be PEP8 conformant

## [1.0.0] - 2018-02-02
- Added support for getting time statistics when collecting resources
- Added support for pulling the $metadata resource
- Added support for pulling the JSON Schema repository
- Added support for pulling OEM resources
- Fixed @odata.type parsing to include support for no versioning

## [0.9.3] - 2017-06-05
- Cleaning help options
- Create directory if specified by "-D" if it is not empty
- Add optional copyright, header and time information to the /redfish, /redfish/v1 and /redfish/v1/odata resources
- Print status code if there is an error in retrieving redfish data with the transport
- Wait time and timeout for Redfish transport have been changed to 5 and 20 respectively

## [0.9.2] - 2017-04-28
- Support to recursively navigate tree instead of using static navigation structure
- Added "--custom" option to support chosing custom navigation and updated structure to include all remaining navigation properties
- Captures GET headers in headers.json for each api
- Captures execution time in time.json for each api
- Adds @redfish.copyright property to each resource; Can specify copyright with "-C `<copyright_message>`" and longform "--Copyright"
- Updated redfishtool library to 0.9.3

## [0.9.1] - 2016-09-06
- Initial Public Release
