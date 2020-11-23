#!/bin/bash


# Fetch data from genisis, starting with once an hour
GENISIS_USERNAME=$GENISIS_USERNAME
GENISIS_PASSWORD=$GENISIS_PASSWORD
URL=$GENISIS_URL
TMP_FILE="/home/ubuntu/launchpad/tmp.json"
OUT_FILE="/home/ubuntu/launchpad/genisis_data.json"
MAX_TIME="-m 1000"
LOG_FILE="/home/ubuntu/launchpad/cron.log"
now=$(date)
echo "HIHI" >> ${LOG_FILE}
echo ${now} >> $LOG_FILE

curl --insecure -u ${GENISIS_USERNAME}:${GENISIS_PASSWORD} ${MAX_TIME} -X GET ${URL} > ${TMP_FILE}
CURL_EXIT_CODE=$?
echo ${CURL_EXIT_CODE}

if [ "${CURL_EXIT_CODE}" != "0" ]; then
	echo "CURL COMMAND FAILED" >> ${LOG_FILE}
	exit 1
else
	echo "CURL COMMAND SUCCESS" >> ${LOG_FILE}
fi

# Now that it has been successful, replace current version
echo "Rearranging files"
if [ -f ${OUT_FILE} ]; then
	echo "A previous outfile exists. Moving it to old."
        mv ${OUT_FILE} ${OUT_FILE}.old
else
	echo "No previous outfile exists"
fi

mv ${TMP_FILE} ${OUT_FILE}

echo "Loading into postgres"
source /home/ubuntu/launchpad/launchpadenv/bin/activate
python /home/ubuntu/launchpad/launchpad/rocketship/load_from_genisis.py ${OUT_FILE}

echo "Complete! Wahoo!" >> ${LOG_FILE}
