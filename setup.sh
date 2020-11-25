#!/bin/sh

# Create virtual environment and load required packages

python3 -m venv launchpadenv
source launchpadenv/bin/activate

pip3 install --trusted-host pypi.org \
--trusted-host files.pythonhosted.org -r launchpad/requirements.txt
