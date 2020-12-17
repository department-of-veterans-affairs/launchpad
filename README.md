## Getting started

### Running locally

[tbc....]

### Provisioning a new server

1. Create a new Ubuntu 20.x instance with ports 5423, 443, and 80 open to inbound TCP traffic and in same security group as the database service instance
1. Get a copy of `load_secrets.sh` from colleague and save to `provisioning`
1. rsync/scp the contents of `provisioning` to home directory on remote (e.g. /home/ubuntu/)
1. Initiate remote session over SSH using port 443
1. Execute (as sudo) `provisioning/bootstrap.sh` to configure instance

### Setting up databases & running code on server

* Load facilities database:
    * curl command:  curl -X GET 'https://sandbox-api.va.gov/services/va_facilities/v0/facilities/all' --header 'apikey:... >
    * python load_facilities.py
* Make sure registry status is current
    * Uncomment scripts in update_registry_status.sh and run them all in that order
* Make sure relevant people are opted out
    * i.e. opt_out_registrants.py
* There are also some one off name changes that I haven't added yet.
* Load genisis db:
    * ./fetch_data_from_genisis.sh
* Extract relevant registrants for study sites:
    * Run ./output_facility_lists.sh
    * The above command will run three scripts:
        * 1: Output all eligibilty (but not set off) records for each study site
        * 2: Output a csv of all records
        * 3: Ouput statistics on all records (ignoring those who opted out, but including those that have been sent off to study teams)
