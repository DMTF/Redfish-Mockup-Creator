#!/bin/bash
# 
# Launch the mockup
cd /mockup
rm -rf model
mkdir -p model
cmd="./redfishMockupCreate.py -r $MODELIP -u '' -p '' -A Basic -S -D model -d 'Redfish Mockup of a HPE ProLiant DL'"
echo "Launching $cmd"
python3 $cmd
# Fix a remaining bug with simulator generation with that index.json file
echo "Fixing bug"
curl -k https://$MODELIP/redfish/v1/ > /mockup/model/redfish/v1/index.json
