#!/bin/sh

# From https://gist.githubusercontent.com/grant-roy/49b2c19fa88dcffc46ab/raw/a4035e3131f4897fd4ba10c51d13e1cc9603ad87/update-jekyll
# This is a simple bash script that will poll github for changes to your repo,
# if found pull them down, and then rebuild and restart Apache.
# Note, we cannot use cron to schedule a job every 5 seconds, so we create
# a script that executes an infinite loop that sleeps every 5 seconds
# We run the script with nohup so it executes as a background process: $nohup ./poll_for_changes.sh

while true
do

echo "Checking for changes..."

git fetch;
LOCAL=$(git rev-parse HEAD);
REMOTE=$(git rev-parse @{u});

echo "Comparing ${LOCAL} vs. ${REMOTE}..."

#if our local revision id doesn't match the remote, we will need to pull the changes
if [ $LOCAL != $REMOTE ]; then

    echo "Changes found! Pulling..."
    #pull and merge changes
    git pull origin master;

    # activate python virtual environment
    source ../launchpadenv/bin/activate;

    # install python dependenices
    pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r requirements.txt;

    # restart apache
    sudo systemctl reload apache2;

    echo "Update complete!"

fi
sleep 5
done
