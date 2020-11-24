
registrant_fields = [
    'firstName',
    'middle',
    'lastName',
    'suffix',
    'phone',
    'email',
    'zipCode',
    'veteranDateOfBirth',
    'GENDER',
    'GENDER_SELF_IDENTIFY_DETAILS',
    'RACE_ETHNICITY',
    'VETERAN',
    'diagnosed',
    'closeContactPositive',
    'hospitalized',
    'smokeOrVape',
    'HEALTH_HISTORY',
    'EMPLOYMENT_STATUS',
    'TRANSPORTATION',
    'residentsInHome',
    'closeContact',
    'consentAgreementAccepted'
]

caluculated_fields = [
    'timezone',
    'state',
    'age',
]

ic_fields = [
    'iCRepresentativeName',
    'iCLatestCallDate',
    'iCoptOut',     # TODO: fix casing.
    'iCCallBackNeeded',
    'iCCallBackDate',
    'iCCallBackTime',
    'iCReceivedOtherC19Vaccine',
    'iCComments',
    'iCLastModifiedDate',
    'iCInUseBy',
    'iCReadyforStudyTeam',
]

study_team_fields = [
    'studyTeamOptOut',
    'studyTeamEligibilityOutcome',
    'studyTeamEnrollmentStatus',
    'studyTeamComments',
    'studyTeamName',
]

all_fields = registrant_fields + caluculated_fields + ic_fields \
                + study_team_fields
