# Relations de la page 11

Les identifiants R01 à R77 correspondent aux connecteurs du fichier simple. Les clés vers un sous-objet sont aussi contrôlées dans la même version du rapport.

| Trait | Parent | Clé parent | Enfant | Clé étrangère | Parents par enfant | Enfants par parent |
|---|---|---|---|---|---|---|
| R01 | STR_REPORT | str_report_id | STR_PPP_PROJECT | str_report_id | 1 | 0..N |
| R02 | STR_REPORT | str_report_id | STR_RELATED_REPORT | str_report_id | 1 | 0..N |
| R03 | STR_REPORT | str_report_id | STR_RELATED_REPORT_TXN_REF | str_report_id | 1 | 0..N |
| R04 | STR_REPORT | str_report_id | STR_DEFINITION | str_report_id | 1 | 0..N |
| R05 | STR_REPORT | str_report_id | STR_PERSON | str_report_id | 1 | 0..N |
| R06 | STR_REPORT | str_report_id | STR_ENTITY | str_report_id | 1 | 0..N |
| R07 | STR_REPORT | str_report_id | STR_EMPLOYER_INFO | str_report_id | 1 | 0..N |
| R08 | STR_REPORT | str_report_id | STR_ADDRESS | str_report_id | 1 | 0..N |
| R09 | STR_REPORT | str_report_id | STR_IDENTIFICATION | str_report_id | 1 | 0..N |
| R10 | STR_REPORT | str_report_id | STR_REGISTRATION_INCORPORATION | str_report_id | 1 | 0..N |
| R11 | STR_REPORT | str_report_id | STR_AUTHORIZED_PERSON | str_report_id | 1 | 0..N |
| R12 | STR_REPORT | str_report_id | STR_DIRECTOR | str_report_id | 1 | 0..N |
| R13 | STR_REPORT | str_report_id | STR_SHARE_OWNER | str_report_id | 1 | 0..N |
| R14 | STR_REPORT | str_report_id | STR_TRUSTEE | str_report_id | 1 | 0..N |
| R15 | STR_REPORT | str_report_id | STR_SETTLOR | str_report_id | 1 | 0..N |
| R16 | STR_REPORT | str_report_id | STR_TRUST_UNIT_OWNER | str_report_id | 1 | 0..N |
| R17 | STR_REPORT | str_report_id | STR_TRUST_BENEFICIARY | str_report_id | 1 | 0..N |
| R18 | STR_REPORT | str_report_id | STR_OTHER_ENTITY_OWNER | str_report_id | 1 | 0..N |
| R19 | STR_REPORT | str_report_id | STR_TRANSACTION | str_report_id | 1 | 0..N |
| R20 | STR_REPORT | str_report_id | STR_STARTING_ACTION | str_report_id | 1 | 0..N |
| R21 | STR_REPORT | str_report_id | STR_COMPLETING_ACTION | str_report_id | 1 | 0..N |
| R22 | STR_REPORT | str_report_id | STR_CONDUCTOR | str_report_id | 1 | 0..N |
| R23 | STR_REPORT | str_report_id | STR_ON_BEHALF_OF | str_report_id | 1 | 0..N |
| R24 | STR_REPORT | str_report_id | STR_SOURCE_OF_FUNDS | str_report_id | 1 | 0..N |
| R25 | STR_REPORT | str_report_id | STR_INVOLVEMENT | str_report_id | 1 | 0..N |
| R26 | STR_REPORT | str_report_id | STR_BENEFICIARY | str_report_id | 1 | 0..N |
| R27 | STR_REPORT | str_report_id | STR_ACCOUNT | str_report_id | 1 | 0..N |
| R28 | STR_REPORT | str_report_id | STR_ACCOUNT_HOLDER | str_report_id | 1 | 0..N |
| R29 | STR_REPORT | str_report_id | STR_VC_DATA | str_report_id | 1 | 0..N |
| R30 | STR_REPORT | str_report_id | STR_API_SUBMISSION | str_report_id | 1 | 0..N |
| R31 | STR_REPORT | str_report_id | STR_SUBMITTED_PAYLOAD | str_report_id | 1 | 0..N |
| R32 | STR_REPORT | str_report_id | STR_VALIDATION_ERROR | str_report_id | 1 | 0..N |
| R33 | STR_REPORT | str_report_id | STR_AUDIT_EVENT | str_report_id | 1 | 0..N |
| R34 | STR_RELATED_REPORT | related_report_id | STR_RELATED_REPORT_TXN_REF | related_report_id | 1 | 0..N |
| R35 | STR_DEFINITION | definition_id | STR_PERSON | definition_id | 1 | 0..1 |
| R36 | STR_DEFINITION | definition_id | STR_ENTITY | definition_id | 1 | 0..1 |
| R37 | STR_PERSON | person_id | STR_EMPLOYER_INFO | person_id | 1 | 0..1 |
| R38 | STR_DEFINITION | definition_id | STR_IDENTIFICATION | definition_id | 1 | 0..N |
| R39 | STR_ENTITY | entity_id | STR_REGISTRATION_INCORPORATION | entity_id | 1 | 0..N |
| R40 | STR_ENTITY | entity_id | STR_AUTHORIZED_PERSON | entity_id | 1 | 0..N |
| R41 | STR_TRANSACTION | transaction_id | STR_STARTING_ACTION | transaction_id | 1 | 0..N |
| R42 | STR_TRANSACTION | transaction_id | STR_COMPLETING_ACTION | transaction_id | 1 | 0..N |
| R43 | STR_STARTING_ACTION | starting_action_id | STR_CONDUCTOR | starting_action_id | 1 | 0..N |
| R44 | STR_CONDUCTOR | conductor_id | STR_ON_BEHALF_OF | conductor_id | 1 | 0..N |
| R45 | STR_STARTING_ACTION | starting_action_id | STR_SOURCE_OF_FUNDS | starting_action_id | 1 | 0..N |
| R46 | STR_COMPLETING_ACTION | completing_action_id | STR_INVOLVEMENT | completing_action_id | 1 | 0..N |
| R47 | STR_COMPLETING_ACTION | completing_action_id | STR_BENEFICIARY | completing_action_id | 1 | 0..N |
| R48 | STR_ACCOUNT | account_id | STR_ACCOUNT_HOLDER | account_id | 1 | 0..N |
| R49 | STR_API_SUBMISSION | submission_id | STR_SUBMITTED_PAYLOAD | submission_id | 1 | 0..1 |
| R50 | STR_ENTITY | entity_id | STR_DIRECTOR | entity_id | 1 | 0..N |
| R51 | STR_ENTITY | entity_id | STR_SHARE_OWNER | entity_id | 1 | 0..N |
| R52 | STR_ENTITY | entity_id | STR_TRUSTEE | entity_id | 1 | 0..N |
| R53 | STR_ENTITY | entity_id | STR_SETTLOR | entity_id | 1 | 0..N |
| R54 | STR_ENTITY | entity_id | STR_TRUST_UNIT_OWNER | entity_id | 1 | 0..N |
| R55 | STR_ENTITY | entity_id | STR_TRUST_BENEFICIARY | entity_id | 1 | 0..N |
| R56 | STR_ENTITY | entity_id | STR_OTHER_ENTITY_OWNER | entity_id | 1 | 0..N |
| R57 | STR_ADDRESS | address_id | STR_PERSON | address_id | 0..1 | 0..1 |
| R58 | STR_ADDRESS | address_id | STR_ENTITY | address_id | 0..1 | 0..1 |
| R59 | STR_ADDRESS | address_id | STR_EMPLOYER_INFO | address_id | 0..1 | 0..1 |
| R60 | STR_ADDRESS | address_id | STR_DIRECTOR | address_id | 0..1 | 0..1 |
| R61 | STR_ADDRESS | address_id | STR_TRUSTEE | address_id | 0..1 | 0..1 |
| R62 | STR_ADDRESS | address_id | STR_SETTLOR | address_id | 0..1 | 0..1 |
| R63 | STR_ADDRESS | address_id | STR_TRUST_UNIT_OWNER | address_id | 0..1 | 0..1 |
| R64 | STR_ADDRESS | address_id | STR_TRUST_BENEFICIARY | address_id | 0..1 | 0..1 |
| R65 | STR_STARTING_ACTION | starting_action_id | STR_ACCOUNT | starting_action_id | 0..1 | 0..1 |
| R66 | STR_COMPLETING_ACTION | completing_action_id | STR_ACCOUNT | completing_action_id | 0..1 | 0..1 |
| R67 | STR_STARTING_ACTION | starting_action_id | STR_VC_DATA | starting_action_id | 0..1 | 0..N |
| R68 | STR_COMPLETING_ACTION | completing_action_id | STR_VC_DATA | completing_action_id | 0..1 | 0..N |
| R69 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_CONDUCTOR | str_report_id, type_code, ref_id | 1 | 0..N |
| R70 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_ON_BEHALF_OF | str_report_id, type_code, ref_id | 1 | 0..N |
| R71 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_SOURCE_OF_FUNDS | str_report_id, type_code, ref_id | 1 | 0..N |
| R72 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_INVOLVEMENT | str_report_id, type_code, ref_id | 1 | 0..N |
| R73 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_BENEFICIARY | str_report_id, type_code, ref_id | 1 | 0..N |
| R74 | STR_DEFINITION | str_report_id, type_code, ref_id | STR_ACCOUNT_HOLDER | str_report_id, type_code, ref_id | 1 | 0..N |
| R75 | STR_API_SUBMISSION | submission_id | STR_VALIDATION_ERROR | submission_id | 0..1 | 0..N |
| R76 | STR_API_SUBMISSION | submission_id | STR_API_SUBMISSION | initial_submission_id | 0..1 | 0..N |
| R77 | STR_REPORT | str_report_id | STR_REPORT | previous_report_id | 0..1 | 0..1 |
