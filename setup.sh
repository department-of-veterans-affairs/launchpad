#!/bin/sh

# Make sure env variables loaded (I do this via source ../prod_setup.sh)

# Create virtual environment and load required packages

python3 -m venv launchpadenv
source launchpadenv/bin/activate

pip3 install --trusted-host pypi.org \
--trusted-host files.pythonhosted.org -r launchpad/requirements.txt

python3 launchpad/manage.py makemigrations rocketship

# Only run this if there are new migrations.
# python3 launchpad/manage.py migrate
