#!/bin/bash

# Collect change log info
CHANGES="## [$1] - $(date +'%Y-%m-%d')"$'\n'
echo "Enter changes:"
while : ; do
    read CHANGE
    if [ "$CHANGE" = "" ]; then
        break
    fi

    CHANGES="$CHANGES- $CHANGE"$'\n'
done

# Rebase
git checkout master
git fetch && git rebase origin

# Update the version number in redfishMockupCreate.py
sed -i -E 's/tool_version = .+/tool_version = "'$1'"/' redfishMockupCreate.py

# Update the change log file
ex CHANGELOG.md <<eof
3 insert
$CHANGES
.
xit
eof

# Commit and push changes
git add CHANGELOG.md redfishMockupCreate.py
git commit -m "$1 versioning"
git push origin master

# Make new release in GitHub
CHANGES="Changes since last release:"$'\n\n'"$CHANGES"
gh release create $1 -n "$CHANGES"
