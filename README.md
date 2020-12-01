## Getting started

### Running locally

[tbc....]

### Provisioning a new server

1. Create a new Ubuntu 20.x instance with ports 5423, 443, and 80 open to inbound TCP traffic and in same security group as the database service instance
1. Get a copy of `load_secrets.sh` from colleague and save to `provisioning`
1. rsync/scp the contents of `provisioning` to home directory on remote (e.g. /home/ubuntu/)
1. Initiate remote session over SSH using port 443
1. Execute (as sudo) `provisioning/bootstrap.sh` to configure instance
