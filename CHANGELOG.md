
# Change Log

## [0.9.4] - 2017-06-01
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
