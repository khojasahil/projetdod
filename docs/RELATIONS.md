# Registre des relations

Ce registre permet de reproduire tous les liens. Il se lit du parent vers l’enfant. Les liens vers STR_REPORT rattachent chaque ligne à une version; les autres clés sont aussi contrôlées dans cette même version.

Une cardinalité de 0..N décrit le nombre de lignes enfants possibles par parent. Elle ne signifie pas que la clé portée par un enfant est facultative. Les obligations avant gel et les contraintes exclusives figurent dans [REGLES.md](REGLES.md). Les références composites vers DEFINITION utilisent les trois colonnes indiquées.

| Parent | Clé parent | Enfant | Clé portée par l’enfant | Enfants par parent | Clé facultative | Explication |
|---|---|---|---|---|---|---|
| STR_REPORT | str_report_id | STR_PPP_PROJECT | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_RELATED_REPORT | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_RELATED_REPORT_TXN_REF | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_DEFINITION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_PERSON | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_ENTITY | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_EMPLOYER_INFO | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_ADDRESS | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_IDENTIFICATION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_REGISTRATION_INCORPORATION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_AUTHORIZED_PERSON | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_DIRECTOR | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_SHARE_OWNER | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_TRUSTEE | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_SETTLOR | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_TRUST_UNIT_OWNER | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_TRUST_BENEFICIARY | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_OTHER_ENTITY_OWNER | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_TRANSACTION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_STARTING_ACTION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_COMPLETING_ACTION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_CONDUCTOR | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_ON_BEHALF_OF | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_SOURCE_OF_FUNDS | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_INVOLVEMENT | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_BENEFICIARY | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_ACCOUNT | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_ACCOUNT_HOLDER | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_VC_DATA | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_API_SUBMISSION | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_SUBMITTED_PAYLOAD | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_VALIDATION_ERROR | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_REPORT | str_report_id | STR_AUDIT_EVENT | str_report_id | 0..N | Non | Appartient à cette version de rapport. |
| STR_RELATED_REPORT | related_report_id | STR_RELATED_REPORT_TXN_REF | related_report_id | 0..N | Non | Précise une opération de ce rapport lié. |
| STR_DEFINITION | definition_id | STR_PERSON | definition_id | 0..1 | Non | Décrit la personne citée par ce repère. |
| STR_DEFINITION | definition_id | STR_ENTITY | definition_id | 0..1 | Non | Décrit l’entité citée par ce repère. |
| STR_PERSON | person_id | STR_EMPLOYER_INFO | person_id | 0..1 | Non | Décrit l’employeur de cette personne. |
| STR_DEFINITION | definition_id | STR_IDENTIFICATION | definition_id | 0..N | Non | Identifie cette personne ou cette entité. |
| STR_ENTITY | entity_id | STR_REGISTRATION_INCORPORATION | entity_id | 0..N | Non | Documente la constitution de cette entité. |
| STR_ENTITY | entity_id | STR_AUTHORIZED_PERSON | entity_id | 0..N | Non | Désigne une personne autorisée pour cette entité. |
| STR_TRANSACTION | transaction_id | STR_STARTING_ACTION | transaction_id | 0..N | Non | Décrit une action au début du mouvement. |
| STR_TRANSACTION | transaction_id | STR_COMPLETING_ACTION | transaction_id | 0..N | Non | Décrit une action à la fin du mouvement. |
| STR_STARTING_ACTION | starting_action_id | STR_CONDUCTOR | starting_action_id | 0..N | Non | Indique qui réalise cette action. |
| STR_CONDUCTOR | conductor_id | STR_ON_BEHALF_OF | conductor_id | 0..N | Non | Indique pour qui agit cet exécutant. |
| STR_STARTING_ACTION | starting_action_id | STR_SOURCE_OF_FUNDS | starting_action_id | 0..N | Non | Indique d’où proviennent les fonds. |
| STR_COMPLETING_ACTION | completing_action_id | STR_INVOLVEMENT | completing_action_id | 0..N | Non | Indique qui intervient dans cette action. |
| STR_COMPLETING_ACTION | completing_action_id | STR_BENEFICIARY | completing_action_id | 0..N | Non | Indique qui bénéficie de cette action. |
| STR_ACCOUNT | account_id | STR_ACCOUNT_HOLDER | account_id | 0..N | Non | Désigne un titulaire de ce compte. |
| STR_API_SUBMISSION | submission_id | STR_SUBMITTED_PAYLOAD | submission_id | 0..1 | Non | Conserve le document transmis lors de cet appel. |
| STR_ENTITY | entity_id | STR_DIRECTOR | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_SHARE_OWNER | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_TRUSTEE | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_SETTLOR | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_TRUST_UNIT_OWNER | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_TRUST_BENEFICIARY | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ENTITY | entity_id | STR_OTHER_ENTITY_OWNER | entity_id | 0..N | Non | Décrit la propriété ou la gouvernance de cette entité. |
| STR_ADDRESS | address_id | STR_PERSON | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_ENTITY | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_EMPLOYER_INFO | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_DIRECTOR | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_TRUSTEE | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_SETTLOR | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_TRUST_UNIT_OWNER | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_ADDRESS | address_id | STR_TRUST_BENEFICIARY | address_id | 0..1 | Oui | Adresse de cette personne ou de cette organisation. |
| STR_STARTING_ACTION | starting_action_id | STR_ACCOUNT | starting_action_id | 0..1 | Oui | Rattache les données à cette action. |
| STR_COMPLETING_ACTION | completing_action_id | STR_ACCOUNT | completing_action_id | 0..1 | Oui | Rattache les données à cette action. |
| STR_STARTING_ACTION | starting_action_id | STR_VC_DATA | starting_action_id | 0..N | Oui | Rattache les données à cette action. |
| STR_COMPLETING_ACTION | completing_action_id | STR_VC_DATA | completing_action_id | 0..N | Oui | Rattache les données à cette action. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_CONDUCTOR | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_ON_BEHALF_OF | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_SOURCE_OF_FUNDS | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_INVOLVEMENT | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_BENEFICIARY | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_DEFINITION | str_report_id, type_code, ref_id | STR_ACCOUNT_HOLDER | str_report_id, type_code, ref_id | 0..N | Non | Retrouve la personne ou l’entité qui tient ce rôle. |
| STR_API_SUBMISSION | submission_id | STR_VALIDATION_ERROR | submission_id | 0..N | Oui | Message reçu dans cette tentative ou consultation. |
| STR_API_SUBMISSION | submission_id | STR_API_SUBMISSION | initial_submission_id | 0..N | Oui | Relie une consultation ou une reprise à l’envoi initial. |
| STR_REPORT | str_report_id | STR_REPORT | previous_report_id | 0..1 | Oui | Relie cette version à la précédente. |

Pour ADDRESS, la cardinalité 0..1 s’applique dans chaque table propriétaire. Une règle supplémentaire impose un seul propriétaire au total. Pour les versions, previous_report_id est absent sur la première version. Pour ACCOUNT et VC_DATA, une seule des deux clés d’action est renseignée.
