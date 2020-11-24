#!/bin/bash

# Fetch data from genisis (once an hour) & load into postgres

GENISIS_USERNAME=$GENISIS_USERNAME
GENISIS_PASSWORD=$GENISIS_PASSWORD
URL=$GENISIS_URL

WORKING_DIR="/home/ubuntu/launchpad"

mkdir -p ${WORKING_DIR}"/data"

TMP_FILE=${WORKING_DIR}"/data/tmp.json"
OUT_FILE=${WORKING_DIR"/data/genisis_data.json"
MAX_TIME="-m 1000"
LOG_FILE=${WORKING_DIR}"/data/cron.log"

START_TIME=$(date)
echo "Starting to copy genisis db & load to postgres: "${START_TIME} >> ${LOG_FILE}

curl --insecure -u ${GENISIS_USERNAME}:${GENISIS_PASSWORD} ${MAX_TIME} -X GET ${URL} > ${TMP_FILE}
CURL_EXIT_CODE=$?

if [ "${CURL_EXIT_CODE}" != "0" ]; then
	echo "CURL COMMAND FAILED" >> ${LOG_FILE}
	exit 1
else
	echo "CURL COMMAND SUCCESS" >> ${LOG_FILE}
fi

# Now that it has been successful, replace current version
if [ -f ${OUT_FILE} ]; then
	echo "A previous outfile exists. Moving it to old." >> ${LOG_FILE}
        mv ${OUT_FILE} ${OUT_FILE}.old
else
	echo "No previous outfile exists" >> ${LOG_FILE}
fi

mv ${TMP_FILE} ${OUT_FILE}

echo "Loading into postgres" >> ${LOG_FILE}
source /home/ubuntu/launchpadenv/bin/activate
python /home/ubuntu/launchpad/load_from_genisis.py ${OUT_FILE} >> ${LOG_FILE} 2>&1

python /home/ubuntu/launchpad/check_num_records.py >> ${LOG_FILE}

END_TIME=$(date)
echo "Complete - yay! at: "${END_TIME} >> ${LOG_FILE}
