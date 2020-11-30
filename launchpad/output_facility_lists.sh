#!/bin/bash

# Outputs csvs of interested registrants for facilities
WORKING_DIR="/home/ubuntu/launchpad/launchpad"
LOG_FILE=${WORKING_DIR}"/data/list_output.log"

START_TIME=$(date)
echo "Create new facility lists starting: "${START_TIME} >> ${LOG_FILE}

mkdir -p ${WORKING_DIR}"/launchpad/data/for_study_sites"

source ${WORKING_DIR}/../launchpadenv/bin/activate

python ${WORKING_DIR}/extract_registrants_for_studies.py facility_list.txt \
${WORKING_DIR}"/launchpad/data/for_study_sites" 2>> ${LOG_FILE}.err 1>> ${LOG_FILE}

END_TIME=$(date)
echo "Complete at: "${END_TIME} >> ${LOG_FILE}