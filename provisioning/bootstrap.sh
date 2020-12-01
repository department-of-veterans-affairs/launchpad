#! /bin/bash
set -x;

# Load secrets as environment variables
source ./load_secrets.sh;

# Install OS dependencies
sudo apt update;
sudo apt-get -y install apache2 apache2-utils libexpat1 ssl-cert python3 \
python3-pip libapache2-mod-wsgi-py3 python3-django libpq-dev python3-venv;

# Get latest source
git clone -c http.sslVerify=false \
https://github.com/department-of-veterans-affairs/launchpad.git;

# Setup Python environment
cd launchpad;
bash ./setup.sh;

# Configure Apache and reload server
sudo chown ubuntu:ubuntu /etc/apache2/apache2.conf;
echo "
WSGIScriptAlias / /home/ubuntu/launchpad/launchpad/wsgi.py
WSGIPythonHome /home/ubuntu/launchpad/launchpadenv
WSGIPythonPath /home/ubuntu/launchpad

<Directory /home/ubuntu/launchpad/launchpad/>
<Files wsgi.py>
Require all granted
</Files>
</Directory>

# Alias /static/ /home/ubuntu/launchpad/static/

# <Directory /home/ubuntu/launchpad/static>
# Require all granted
# </Directory>
" >> /etc/apache2/apache2.conf;
sudo chown root:root /etc/apache2/apache2.conf;
sudo systemctl reload apache2;

# Make all files in home dir owned by user
sudo chown -R ubuntu:ubuntu /home/ubuntu

# Poll for new commits from GitHub
nohup bash ./poll_for_commits.sh &
