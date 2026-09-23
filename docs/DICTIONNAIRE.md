# Dictionnaire des 34 tables

**Édition avec référentiels :** ce dictionnaire conserve les 365 colonnes du modèle initial. Le [complément référentiels](REFERENTIELS_CANAFE.md) décrit les 24 colonnes internes ajoutées aux tables métier et les 23 nouvelles tables de référence/version. Le [registre champ → domaine de valeurs](../traceability/reference-fields.csv) indique, pour chaque champ concerné, la liste, la variante, les valeurs permises et la source Swagger.

Ce document sert à construire le modèle. Pour le présenter à des collègues, commencer par le [guide métier](GUIDE_METIER.md).

Les neuf domaines et les noms de tables reprennent le projet précédent. Une ligne de `STR_REPORT` représente une version; tous ses enfants portent le même `str_report_id`. Les règles de saisie et les obligations au moment d’envoyer sont distinguées dans [REGLES.md](REGLES.md).

Les identifiants, rangs et indicateurs de présence sont internes. Les types sont logiques, sans choix de SGBD. « Facultatif dans le Swagger » ne dispense pas de vérifier une obligation métier conditionnelle. Les champs propres à un type de définition ne sont ni saisis ni transmis pour les autres types.

Les références `Fxxxx` renvoient aux lignes de [fields.csv](../traceability/fields.csv), qui donnent le chemin JSON complet, la variante, le JSON Pointer, les lignes du YAML et les contraintes exactes. Les réponses API sont archivées intégralement; seuls les messages et l’identifiant externe sont également projetés en colonnes.

## Rapport

Quel dossier transmet-on ?

### STR_REPORT — Le rapport

Une version de la déclaration, avec le récit du soupçon et les mesures prises.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| str_report_id | Identifiant | Identifie cette ligne de le rapport. Clé primaire | INTERNE · Voir règle interne | Interne |
| previous_report_id | Identifiant | Relie cette version à la précédente. FK vers STR_REPORT.str_report_id; facultatif | INTERNE · Voir règle interne | Interne |
| report_group_id | Identifiant | Regroupe les versions d’une même déclaration. Stable dans toute la chaîne | INTERNE · Voir règle interne | Interne |
| version_number | Entier | Numérote les versions pour retrouver ce qui a changé. Unique par report_group_id; commence à 1 | INTERNE · Voir règle interne | Interne |
| status | Texte | État de préparation interne du rapport. BROUILLON, PRET, GELE, REMPLACE | INTERNE · Voir règle interne | Interne |
| created_at | Date et heure | Date de création de cette version. | INTERNE · Voir règle interne | Interne |
| created_by | Texte | Personne ou service à l’origine de la version. | INTERNE · Voir règle interne | Interne |
| frozen_at | Date et heure | Date à partir de laquelle les données métier ne sont plus modifiables. Facultatif avant gel | INTERNE · Voir règle interne | Interne |
| schema_sha256 | Texte | Identifie la copie exacte du Swagger utilisée. Empreinte du fichier officiel archivé | INTERNE · Voir règle interne | Interne |
| report_type_code | Entier | Type de déclaration : DOD, code 102 dans ce projet. | SWAGGER · Selon le contexte | F0001 — `$.reportDetails.reportTypeCode` |
| submit_type_code | Entier | Nature de la demande : création, mise à jour ou suppression. | SWAGGER · Selon le contexte | F0002 — `$.reportDetails.submitTypeCode` |
| activity_sector_code | Entier | Secteur d’activité de l’entité déclarante. | SWAGGER · Facultatif dans le Swagger | F0003 — `$.reportDetails.activitySectorCode` |
| reporting_entity_number | Nombre exact | Numéro de l’entité responsable de la déclaration. | SWAGGER · Selon le contexte | F0004 — `$.reportDetails.reportingEntityNumber` |
| submitting_re_number | Nombre exact | Numéro de l’entité qui transmet la déclaration. | SWAGGER · Selon le contexte | F0005 — `$.reportDetails.submittingReportingEntityNumber` |
| re_report_reference | Texte | Référence de déclaration attribuée par l’entité déclarante. | SWAGGER · Selon le contexte | F0006 — `$.reportDetails.reportingEntityReportReference` |
| re_contact_id | Nombre exact | Identifiant du contact de l’entité déclarante. | SWAGGER · Selon le contexte | F0007 — `$.reportDetails.reportingEntityContactId` |
| ministerial_directive_code | Texte | Directive ministérielle associée. | SWAGGER · Facultatif dans le Swagger | F0008 — `$.reportDetails.ministerialDirectiveCode` |
| suspicious_activity_desc | Texte | Récit des faits, du contexte et des soupçons. | SWAGGER · Facultatif dans le Swagger | F0009 — `$.detailsOfSuspicion.descriptionOfSuspiciousActivity` |
| suspicion_type_code | Entier | Catégorie du soupçon déclaré. | SWAGGER · Facultatif dans le Swagger | F0010 — `$.detailsOfSuspicion.suspicionTypeCode` |
| pep_included_indicator | Oui / non | Présence déclarée d’une personne politiquement vulnérable. | SWAGGER · Facultatif dans le Swagger | F0012 — `$.detailsOfSuspicion.politicallyExposedPersonIncludedIndicator` |
| action_taken_desc | Texte | Description des mesures prises. | SWAGGER · Facultatif dans le Swagger | F0015 — `$.actionTaken.description` |
| action_taken_present | Oui / non | Distingue des mesures non renseignées d’un objet actionTaken présent mais vide. Interne; jamais envoyé dans le JSON | INTERNE · Voir règle interne | Interne |

À respecter :

- Une ligne = une version. UNIQUE(report_group_id, version_number). previous_report_id reste dans le même groupe et pointe vers la version précédente; pas de branche ni de cycle.
- Au gel : report_type_code = 102; au moins une transaction; objets et listes requis présents.
- Correction : même reporting_entity_number et re_report_reference. Une nouvelle déclaration subséquente a un nouveau groupe.
- Les données d’une version gelée et de ses enfants ne sont jamais écrasées.

### STR_PPP_PROJECT — Les projets associés

Les projets de partenariat public-privé cités dans le rapport.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| ppp_id | Identifiant | Identifie cette ligne de les projets associés. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| project_name_code | Entier | Projet de partenariat public-privé associé. | SWAGGER · Selon le contexte | F0011 — `$.detailsOfSuspicion.publicPrivatePartnershipProjectNameCodes[]` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_RELATED_REPORT — Les rapports liés

Les références d’autres déclarations utiles pour comprendre le dossier.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| related_report_id | Identifiant | Identifie cette ligne de les rapports liés. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| re_report_reference | Texte | Référence de déclaration attribuée par l’entité déclarante. | SWAGGER · Selon le contexte | F0013 — `$.relatedReports[].reportingEntityReportReference` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_RELATED_REPORT_TXN_REF — Les opérations liées

Les références d’opérations à retrouver dans un rapport lié.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| id | Identifiant | Identifie cette ligne de les opérations liées. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| related_report_id | Identifiant | Précise une opération de ce rapport lié. FK vers STR_RELATED_REPORT.related_report_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| txn_reference | Texte | Référence d’une opération dans une déclaration connexe. | SWAGGER · Selon le contexte | F0014 — `$.relatedReports[].reportingEntityTransactionReferences[]` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Définitions

De qui parle-t-on ?

### STR_DEFINITION — Le point de référence

Le repère utilisé pour citer une personne ou une entreprise dans le rapport.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| definition_id | Identifiant | Identifie cette ligne de le point de référence. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0016, F0021, F0024, F0063, F0108, F0168 — `$.definitions[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0017, F0022, F0025, F0064, F0109, F0169 — `$.definitions[].refId` |

À respecter :

- UNIQUE(str_report_id, ref_id) et UNIQUE(str_report_id, type_code, ref_id).
- Exactement une ligne PERSON si type_code ∈ {1,3,5}, ou une ligne ENTITY si type_code ∈ {2,4,6}.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_PERSON — La personne

Les renseignements sur une personne physique, selon le niveau de détail demandé.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| person_id | Identifiant | Identifie cette ligne de la personne. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| definition_id | Identifiant | Décrit la personne citée par ce repère. FK vers STR_DEFINITION.definition_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0018, F0026, F0111 — `$.definitions[].givenName` |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0019, F0027, F0110 — `$.definitions[].surname` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0020, F0028, F0112 — `$.definitions[].otherNameInitial` |
| alias | Texte (100) | Alias de la personne. | SWAGGER · Facultatif dans le Swagger | F0029, F0113 — `$.definitions[].alias` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0030, F0132 — `$.definitions[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0031, F0133 — `$.definitions[].extensionNumber` |
| date_of_birth | Texte | Date de naissance. | SWAGGER · Facultatif dans le Swagger | F0032, F0134 — `$.definitions[].dateOfBirth` |
| country_of_residence_code | Texte | Pays de résidence. | SWAGGER · Facultatif dans le Swagger | F0033, F0135 — `$.definitions[].countryOfResidenceCode` |
| occupation | Texte (200) | Profession ou métier. | SWAGGER · Facultatif dans le Swagger | F0034, F0137 — `$.definitions[].occupation` |
| name_of_employer | Texte (100) | Nom de l’employeur déclaré dans PersonDetails. | SWAGGER · Facultatif dans le Swagger | F0035 — `$.definitions[].nameOfEmployer` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0036, F0114 — `$.definitions[].addressTypeCode` |
| country_of_citizenship_code | Texte | Pays de citoyenneté. | SWAGGER · Facultatif dans le Swagger | F0136 — `$.definitions[].countryOfCitizenshipCode` |

À respecter :

- UNIQUE(definition_id). Les champs autorisés dépendent du type_code de la définition; voir les variantes de la traçabilité.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_ENTITY — L’entité

Les renseignements sur une entreprise, une organisation ou une fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| entity_id | Identifiant | Identifie cette ligne de l’entité. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| definition_id | Identifiant | Décrit l’entité citée par ce repère. FK vers STR_DEFINITION.definition_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| name_of_entity | Texte (100) | Dénomination de l’entité. | SWAGGER · Facultatif dans le Swagger | F0023, F0065, F0170 — `$.definitions[].nameOfEntity` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0066, F0189 — `$.definitions[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0067, F0190 — `$.definitions[].extensionNumber` |
| nature_of_principal_business | Texte (200) | Nature de l’activité principale de l’entité. | SWAGGER · Facultatif dans le Swagger | F0068, F0205 — `$.definitions[].natureOfPrincipalBusiness` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0069, F0171 — `$.definitions[].addressTypeCode` |
| registration_incorporation_indicator | Oui / non | Indicateur d’enregistrement ou de constitution. | SWAGGER · Facultatif dans le Swagger | F0099, F0206 — `$.definitions[].registrationIncorporationIndicator` |
| structure_type_code | Entier | Structure juridique de l’entité. | SWAGGER · Facultatif dans le Swagger | F0203 — `$.definitions[].structureTypeCode` |
| structure_type_other | Texte (200) | Précision de la structure autre. | SWAGGER · Facultatif dans le Swagger | F0204 — `$.definitions[].structureTypeOther` |

À respecter :

- UNIQUE(definition_id). Les champs autorisés dépendent du type_code de la définition; voir les variantes de la traçabilité.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_EMPLOYER_INFO — L’employeur

Les coordonnées de l’employeur lorsque la définition de personne les prévoit.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| employer_id | Identifiant | Identifie cette ligne de l’employeur. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| person_id | Identifiant | Décrit l’employeur de cette personne. FK vers STR_PERSON.person_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| name | Texte (100) | Nom de l’employeur. | SWAGGER · Facultatif dans le Swagger | F0138 — `$.definitions[].employerInformation.name` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0139 — `$.definitions[].employerInformation.addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0157 — `$.definitions[].employerInformation.telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0158 — `$.definitions[].employerInformation.extensionNumber` |

À respecter :

- UNIQUE(person_id). Possible uniquement pour une personne de type 5; une ligne vide conserve employerInformation: {}.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Identité

Comment la décrire et l’identifier ?

### STR_ADDRESS — L’adresse

Une adresse structurée ou en texte libre, rattachée à son propriétaire.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| address_id | Identifiant | Identifie cette ligne de l’adresse. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0037, F0051, F0070, F0084, F0115, F0129, F0140, F0154, F0172, F0186, F0219, F0233, F0245, F0259, F0268, F0282, F0291, F0305, F0314, F0328 — `$.definitions[].address.typeCode` (+ 6 autres usages) |
| unit_number | Texte (10) | Numéro d’unité. | SWAGGER · Facultatif dans le Swagger | F0038, F0071, F0116, F0141, F0173, F0220, F0246, F0269, F0292, F0315 — `$.definitions[].address.unitNumber` (+ 6 autres usages) |
| building_number | Texte (10) | Numéro d’immeuble. | SWAGGER · Facultatif dans le Swagger | F0039, F0072, F0117, F0142, F0174, F0221, F0247, F0270, F0293, F0316 — `$.definitions[].address.buildingNumber` (+ 6 autres usages) |
| street_address | Texte (100) | Rue. | SWAGGER · Facultatif dans le Swagger | F0040, F0073, F0118, F0143, F0175, F0222, F0248, F0271, F0294, F0317 — `$.definitions[].address.streetAddress` (+ 6 autres usages) |
| city | Texte (100) | Ville. | SWAGGER · Facultatif dans le Swagger | F0041, F0074, F0119, F0144, F0176, F0223, F0249, F0272, F0295, F0318 — `$.definitions[].address.city` (+ 6 autres usages) |
| district | Texte (100) | District. | SWAGGER · Facultatif dans le Swagger | F0042, F0075, F0120, F0145, F0177, F0224, F0250, F0273, F0296, F0319 — `$.definitions[].address.district` (+ 6 autres usages) |
| province_state_code | Texte | Code de province ou État. | SWAGGER · Facultatif dans le Swagger | F0043, F0044, F0045, F0046, F0076, F0077, F0078, F0079, F0121, F0122, F0123, F0124, F0146, F0147, F0148, F0149, F0178, F0179, F0180, F0181, F0225, F0226, F0227, F0228, F0251, F0252, F0253, F0254, F0274, F0275, F0276, F0277, F0297, F0298, F0299, F0300, F0320, F0321, F0322, F0323 — `$.definitions[].address.provinceStateCode` (+ 6 autres usages) |
| province_state_name | Texte (100) | Nom de province ou État. | SWAGGER · Facultatif dans le Swagger | F0047, F0080, F0125, F0150, F0182, F0229, F0255, F0278, F0301, F0324 — `$.definitions[].address.provinceStateName` (+ 6 autres usages) |
| sub_province_sub_locality | Texte (100) | Subdivision ou localité. | SWAGGER · Facultatif dans le Swagger | F0048, F0081, F0126, F0151, F0183, F0230, F0256, F0279, F0302, F0325 — `$.definitions[].address.subProvinceSubLocality` (+ 6 autres usages) |
| postal_zip_code | Texte (20) | Code postal. | SWAGGER · Facultatif dans le Swagger | F0049, F0082, F0127, F0152, F0184, F0231, F0257, F0280, F0303, F0326 — `$.definitions[].address.postalZipCode` (+ 6 autres usages) |
| country_code | Texte | Pays de l’adresse. | SWAGGER · Facultatif dans le Swagger | F0050, F0052, F0083, F0085, F0128, F0130, F0153, F0155, F0185, F0187, F0232, F0234, F0258, F0260, F0281, F0283, F0304, F0306, F0327, F0329 — `$.definitions[].address.countryCode` (+ 6 autres usages) |
| unstructured | Texte (500) | Adresse en texte libre. | SWAGGER · Selon le contexte | F0053, F0086, F0131, F0156, F0188, F0235, F0261, F0284, F0307, F0330 — `$.definitions[].address.unstructured` (+ 6 autres usages) |

À respecter :

- Une adresse appartient à un seul propriétaire de la même version. Ce contrôle entre tables est à implanter; ce n’est pas une clé étrangère polymorphe.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_IDENTIFICATION — Les pièces d’identité

Les documents utilisés pour identifier la personne ou l’entité.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| identification_id | Identifiant | Identifie cette ligne de les pièces d’identité. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| definition_id | Identifiant | Identifie cette personne ou cette entité. FK vers STR_DEFINITION.definition_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| identifier_type_code | Entier | Type de document d’identification. | SWAGGER · Facultatif dans le Swagger | F0054, F0087, F0159, F0191 — `$.definitions[].identifications[].identifierTypeCode` |
| identifier_type_other | Texte (200) | Précision du document autre. | SWAGGER · Facultatif dans le Swagger | F0055, F0088, F0160, F0192 — `$.definitions[].identifications[].identifierTypeOther` |
| number | Texte (100) | Numéro déclaré dans le contexte de cette table. | SWAGGER · Facultatif dans le Swagger | F0056, F0089, F0161, F0193 — `$.definitions[].identifications[].number` |
| jurisdiction_country_code | Texte | Pays de délivrance ou d’enregistrement. | SWAGGER · Facultatif dans le Swagger | F0057, F0090, F0162, F0194 — `$.definitions[].identifications[].jurisdictionOfIssueCountryCode` |
| jurisdiction_province_state_code | Texte | Province ou État de délivrance ou d’enregistrement. | SWAGGER · Facultatif dans le Swagger | F0058, F0059, F0060, F0061, F0091, F0092, F0093, F0094, F0163, F0164, F0165, F0166, F0195, F0196, F0197, F0198 — `$.definitions[].identifications[].jurisdictionOfIssueProvinceStateCode` |
| jurisdiction_province_state_name | Texte (100) | Nom de juridiction non codifiée. | SWAGGER · Facultatif dans le Swagger | F0062, F0095, F0167, F0199 — `$.definitions[].identifications[].jurisdictionOfIssueProvinceStateName` |

À respecter :

- La définition propriétaire est de type 3, 4, 5 ou 6. Le domaine du document dépend de personne ou entité.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Entité

Comment l’organisation est-elle constituée ?

### STR_REGISTRATION_INCORPORATION — L’enregistrement

Les numéros et lieux d’enregistrement ou de constitution de l’entité.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| reg_inc_id | Identifiant | Identifie cette ligne de l’enregistrement. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Documente la constitution de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Facultatif dans le Swagger | F0100, F0207 — `$.definitions[].registrationsIncorporations[].typeCode` |
| number | Texte (100) | Numéro déclaré dans le contexte de cette table. | SWAGGER · Facultatif dans le Swagger | F0101, F0208 — `$.definitions[].registrationsIncorporations[].number` |
| jurisdiction_country_code | Texte | Pays de délivrance ou d’enregistrement. | SWAGGER · Facultatif dans le Swagger | F0102, F0209 — `$.definitions[].registrationsIncorporations[].jurisdictionOfIssueCountryCode` |
| jurisdiction_province_state_code | Texte | Province ou État de délivrance ou d’enregistrement. | SWAGGER · Facultatif dans le Swagger | F0103, F0104, F0105, F0106, F0210, F0211, F0212, F0213 — `$.definitions[].registrationsIncorporations[].jurisdictionOfIssueProvinceStateCode` |
| jurisdiction_province_state_name | Texte (100) | Nom de juridiction non codifiée. | SWAGGER · Facultatif dans le Swagger | F0107, F0214 — `$.definitions[].registrationsIncorporations[].jurisdictionOfIssueProvinceStateName` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_AUTHORIZED_PERSON — Les personnes autorisées

Les noms des personnes autorisées à agir pour l’entité.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| auth_id | Identifiant | Identifie cette ligne de les personnes autorisées. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Désigne une personne autorisée pour cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0096, F0200 — `$.definitions[].authorizedPersons[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0097, F0201 — `$.definitions[].authorizedPersons[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0098, F0202 — `$.definitions[].authorizedPersons[].otherNameInitial` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Bénéficiaires effectifs

Qui dirige ou détient l’entité ?

### STR_DIRECTOR — Les administrateurs

Les personnes qui administrent la société.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| director_id | Identifiant | Identifie cette ligne de les administrateurs. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0215 — `$.definitions[].directorsOfCorporation[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0216 — `$.definitions[].directorsOfCorporation[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0217 — `$.definitions[].directorsOfCorporation[].otherNameInitial` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0218 — `$.definitions[].directorsOfCorporation[].addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0236 — `$.definitions[].directorsOfCorporation[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0237 — `$.definitions[].directorsOfCorporation[].extensionNumber` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_SHARE_OWNER — Les détenteurs d’actions

Les personnes détenant des actions, telles qu’elles sont déclarées.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| share_owner_id | Identifiant | Identifie cette ligne de les détenteurs d’actions. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0238 — `$.definitions[].personsOwningSharesOfCorporation[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0239 — `$.definitions[].personsOwningSharesOfCorporation[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0240 — `$.definitions[].personsOwningSharesOfCorporation[].otherNameInitial` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_TRUSTEE — Les fiduciaires

Les personnes qui administrent la fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| trustee_id | Identifiant | Identifie cette ligne de les fiduciaires. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0241 — `$.definitions[].trusteesOfTrust[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0242 — `$.definitions[].trusteesOfTrust[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0243 — `$.definitions[].trusteesOfTrust[].otherNameInitial` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0244 — `$.definitions[].trusteesOfTrust[].addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0262 — `$.definitions[].trusteesOfTrust[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0263 — `$.definitions[].trusteesOfTrust[].extensionNumber` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_SETTLOR — Les constituants

Les personnes à l’origine de la fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| settlor_id | Identifiant | Identifie cette ligne de les constituants. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0264 — `$.definitions[].settlorsOfTrust[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0265 — `$.definitions[].settlorsOfTrust[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0266 — `$.definitions[].settlorsOfTrust[].otherNameInitial` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0267 — `$.definitions[].settlorsOfTrust[].addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0285 — `$.definitions[].settlorsOfTrust[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0286 — `$.definitions[].settlorsOfTrust[].extensionNumber` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_TRUST_UNIT_OWNER — Les détenteurs d’unités

Les personnes détenant des unités de la fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| trust_unit_owner_id | Identifiant | Identifie cette ligne de les détenteurs d’unités. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0287 — `$.definitions[].personsOwningUnitsOfTrust[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0288 — `$.definitions[].personsOwningUnitsOfTrust[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0289 — `$.definitions[].personsOwningUnitsOfTrust[].otherNameInitial` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0290 — `$.definitions[].personsOwningUnitsOfTrust[].addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0308 — `$.definitions[].personsOwningUnitsOfTrust[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0309 — `$.definitions[].personsOwningUnitsOfTrust[].extensionNumber` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_TRUST_BENEFICIARY — Les bénéficiaires de fiducie

Les personnes désignées comme bénéficiaires de la fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| trust_beneficiary_id | Identifiant | Identifie cette ligne de les bénéficiaires de fiducie. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| address_id | Identifiant | Adresse de cette personne ou de cette organisation. FK vers STR_ADDRESS.address_id; facultatif | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0310 — `$.definitions[].beneficiariesOfTrust[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0311 — `$.definitions[].beneficiariesOfTrust[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0312 — `$.definitions[].beneficiariesOfTrust[].otherNameInitial` |
| address_type_code | Entier | Qualification de l’adresse au niveau du propriétaire. | SWAGGER · Facultatif dans le Swagger | F0313 — `$.definitions[].beneficiariesOfTrust[].addressTypeCode` |
| telephone_number | Texte (20) | Numéro de téléphone. | SWAGGER · Facultatif dans le Swagger | F0331 — `$.definitions[].beneficiariesOfTrust[].telephoneNumber` |
| extension_number | Texte (10) | Poste téléphonique. | SWAGGER · Facultatif dans le Swagger | F0332 — `$.definitions[].beneficiariesOfTrust[].extensionNumber` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_OTHER_ENTITY_OWNER — Les autres propriétaires

Les personnes détenant une entité qui n’est ni une société ni une fiducie.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| other_entity_owner_id | Identifiant | Identifie cette ligne de les autres propriétaires. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| entity_id | Identifiant | Décrit la propriété ou la gouvernance de cette entité. FK vers STR_ENTITY.entity_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| surname | Texte (100) | Nom de famille. | SWAGGER · Facultatif dans le Swagger | F0333 — `$.definitions[].personsOwningEntityNotCorporationOrTrust[].surname` |
| given_name | Texte (100) | Prénom. | SWAGGER · Facultatif dans le Swagger | F0334 — `$.definitions[].personsOwningEntityNotCorporationOrTrust[].givenName` |
| other_name_initial | Texte (100) | Autres noms ou initiales. | SWAGGER · Facultatif dans le Swagger | F0335 — `$.definitions[].personsOwningEntityNotCorporationOrTrust[].otherNameInitial` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Transactions

Que s’est-il passé ?

### STR_TRANSACTION — L’opération

L’opération effectuée ou tentée, sa date et les circonstances connues.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| transaction_id | Identifiant | Identifie cette ligne de l’opération. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| re_location_id | Texte (30) | Établissement de l’entité déclarante concerné. | SWAGGER · Selon le contexte | F0336 — `$.transactions[].reportingEntityLocationId` |
| attempted_indicator | Oui / non | Distinction entre opération tentée et opération effectuée. | SWAGGER · Selon le contexte | F0337 — `$.transactions[].suspiciousTransactionDetails.attemptedTransactionIndicator` |
| reason_not_completed | Texte (200) | Raison pour laquelle l’opération n’a pas été achevée. | SWAGGER · Facultatif dans le Swagger | F0338 — `$.transactions[].suspiciousTransactionDetails.reasonNotCompleted` |
| date_of_transaction | Texte | Date locale de l’opération. | SWAGGER · Facultatif dans le Swagger | F0339 — `$.transactions[].suspiciousTransactionDetails.dateOfTransaction` |
| time_of_transaction | Texte | Heure de l’opération avec décalage UTC. | SWAGGER · Facultatif dans le Swagger | F0340 — `$.transactions[].suspiciousTransactionDetails.timeOfTransaction` |
| method_code | Entier | Mode de réalisation de l’opération. | SWAGGER · Facultatif dans le Swagger | F0341 — `$.transactions[].suspiciousTransactionDetails.methodCode` |
| method_other | Texte (200) | Précision du mode autre. | SWAGGER · Facultatif dans le Swagger | F0342 — `$.transactions[].suspiciousTransactionDetails.methodOther` |
| date_of_posting | Texte | Date de comptabilisation. | SWAGGER · Facultatif dans le Swagger | F0343 — `$.transactions[].suspiciousTransactionDetails.dateOfPosting` |
| time_of_posting | Texte | Heure de comptabilisation avec décalage UTC. | SWAGGER · Facultatif dans le Swagger | F0344 — `$.transactions[].suspiciousTransactionDetails.timeOfPosting` |
| re_txn_reference | Texte | Référence de l’opération attribuée par l’entité déclarante. | SWAGGER · Facultatif dans le Swagger | F0345 — `$.transactions[].suspiciousTransactionDetails.reportingEntityTransactionReference` |
| purpose | Texte (200) | Objet de l’opération. | SWAGGER · Facultatif dans le Swagger | F0346 — `$.transactions[].suspiciousTransactionDetails.purpose` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_STARTING_ACTION — L’action initiale

Ce qui amorce le mouvement : nature des fonds, sens et montant.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| starting_action_id | Identifiant | Identifie cette ligne de l’action initiale. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| transaction_id | Identifiant | Décrit une action au début du mouvement. FK vers STR_TRANSACTION.transaction_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| direction | Entier | Sens du flux de l’action initiale. | SWAGGER · Facultatif dans le Swagger | F0347 — `$.transactions[].startingActions[].details.direction` |
| fund_type_code | Entier | Nature des fonds, actifs ou monnaies virtuelles. | SWAGGER · Facultatif dans le Swagger | F0348 — `$.transactions[].startingActions[].details.fundAssetVirtualCurrencyTypeCode` |
| fund_type_other | Texte (200) | Précision de la nature autre des fonds ou actifs. | SWAGGER · Facultatif dans le Swagger | F0349 — `$.transactions[].startingActions[].details.fundAssetVirtualCurrencyTypeOther` |
| amount | Texte | Montant déclaré, conservé dans sa représentation textuelle exacte. | SWAGGER · Facultatif dans le Swagger | F0350 — `$.transactions[].startingActions[].details.amount` |
| currency_code | Texte | Devise des fonds. | SWAGGER · Facultatif dans le Swagger | F0351 — `$.transactions[].startingActions[].details.currencyCode` |
| vc_type_code | Texte | Type de monnaie virtuelle. | SWAGGER · Facultatif dans le Swagger | F0352 — `$.transactions[].startingActions[].details.virtualCurrencyTypeCode` |
| vc_type_other | Texte (200) | Précision de la monnaie virtuelle autre. | SWAGGER · Facultatif dans le Swagger | F0353 — `$.transactions[].startingActions[].details.virtualCurrencyTypeOther` |
| exchange_rate | Texte | Taux de change déclaré, conservé sans arrondi. | SWAGGER · Facultatif dans le Swagger | F0354 — `$.transactions[].startingActions[].details.exchangeRate` |
| reference_number | Texte (200) | Numéro de référence de l’action. | SWAGGER · Facultatif dans le Swagger | F0358 — `$.transactions[].startingActions[].details.referenceNumber` |
| ref_number_other | Texte (200) | Autre numéro associé à la référence. | SWAGGER · Facultatif dans le Swagger | F0359 — `$.transactions[].startingActions[].details.referenceNumberOtherRelatedNumber` |
| account_status_code | Entier | État du compte au moment de cette action. | SWAGGER · Facultatif dans le Swagger | F0372 — `$.transactions[].startingActions[].details.accountStatusAtTimeOfTransaction` |
| how_funds_obtained | Texte (200) | Origine décrite des fonds ou monnaies virtuelles. | SWAGGER · Facultatif dans le Swagger | F0373 — `$.transactions[].startingActions[].details.howFundsOrVirtualCurrencyObtained` |
| source_funds_indicator | Oui / non | Indicateur de présence d’une source de fonds. | SWAGGER · Facultatif dans le Swagger | F0374 — `$.transactions[].startingActions[].details.sourcesOfFundsOrVirtualCurrencyIndicator` |
| conductor_indicator | Oui / non | Indicateur de présence d’un exécutant. | SWAGGER · Facultatif dans le Swagger | F0375 — `$.transactions[].startingActions[].details.conductorIndicator` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_COMPLETING_ACTION — L’action finale

Ce qui est fait des fonds à l’issue du mouvement.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| completing_action_id | Identifiant | Identifie cette ligne de l’action finale. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| transaction_id | Identifiant | Décrit une action à la fin du mouvement. FK vers STR_TRANSACTION.transaction_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| disposition_code | Entier | Utilisation ou destination des fonds. | SWAGGER · Facultatif dans le Swagger | F0400 — `$.transactions[].completingActions[].details.dispositionCode` |
| disposition_other | Texte (200) | Précision de la disposition autre. | SWAGGER · Facultatif dans le Swagger | F0401 — `$.transactions[].completingActions[].details.dispositionOther` |
| amount | Texte | Montant déclaré, conservé dans sa représentation textuelle exacte. | SWAGGER · Facultatif dans le Swagger | F0402 — `$.transactions[].completingActions[].details.amount` |
| currency_code | Texte | Devise des fonds. | SWAGGER · Facultatif dans le Swagger | F0403 — `$.transactions[].completingActions[].details.currencyCode` |
| vc_type_code | Texte | Type de monnaie virtuelle. | SWAGGER · Facultatif dans le Swagger | F0404 — `$.transactions[].completingActions[].details.virtualCurrencyTypeCode` |
| vc_type_other | Texte (200) | Précision de la monnaie virtuelle autre. | SWAGGER · Facultatif dans le Swagger | F0405 — `$.transactions[].completingActions[].details.virtualCurrencyTypeOther` |
| exchange_rate | Texte | Taux de change déclaré, conservé sans arrondi. | SWAGGER · Facultatif dans le Swagger | F0406 — `$.transactions[].completingActions[].details.exchangeRate` |
| value_in_cad | Texte | Contre-valeur déclarée en dollars canadiens. | SWAGGER · Facultatif dans le Swagger | F0407 — `$.transactions[].completingActions[].details.valueInCanadianDollars` |
| reference_number | Texte (200) | Numéro de référence de l’action. | SWAGGER · Facultatif dans le Swagger | F0411 — `$.transactions[].completingActions[].details.referenceNumber` |
| ref_number_other | Texte (200) | Autre numéro associé à la référence. | SWAGGER · Facultatif dans le Swagger | F0412 — `$.transactions[].completingActions[].details.referenceNumberOtherRelatedNumber` |
| account_status_code | Entier | État du compte au moment de cette action. | SWAGGER · Facultatif dans le Swagger | F0425 — `$.transactions[].completingActions[].details.accountStatusAtTimeOfTransaction` |
| involvement_indicator | Oui / non | Indicateur de présence d’une personne ou entité impliquée. | SWAGGER · Facultatif dans le Swagger | F0426 — `$.transactions[].completingActions[].details.involvementIndicator` |
| beneficiary_indicator | Oui / non | Indicateur de présence d’un bénéficiaire de l’action finale. | SWAGGER · Facultatif dans le Swagger | F0427 — `$.transactions[].completingActions[].details.beneficiaryIndicator` |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Rôles

Qui fait quoi dans l’opération ?

### STR_CONDUCTOR — L’exécutant

La personne ou l’entité qui réalise l’action initiale.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| conductor_id | Identifiant | Identifie cette ligne de l’exécutant. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| starting_action_id | Identifiant | Indique qui réalise cette action. FK vers STR_STARTING_ACTION.starting_action_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0381 — `$.transactions[].startingActions[].conductors[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0382 — `$.transactions[].startingActions[].conductors[].refId` |
| client_number | Texte (100) | Numéro de client connu dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0383 — `$.transactions[].startingActions[].conductors[].details.clientNumber` |
| email_address | Texte (200) | Adresse courriel connue dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0384 — `$.transactions[].startingActions[].conductors[].details.emailAddress` |
| url | Texte (200) | Adresse web connue dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0385 — `$.transactions[].startingActions[].conductors[].details.url` |
| device_type_code | Entier | Type d’appareil utilisé. | SWAGGER · Facultatif dans le Swagger | F0386 — `$.transactions[].startingActions[].conductors[].details.typeOfDeviceCode` |
| device_type_other | Texte (200) | Précision du type d’appareil autre. | SWAGGER · Facultatif dans le Swagger | F0387 — `$.transactions[].startingActions[].conductors[].details.typeOfDeviceOther` |
| username | Texte (100) | Nom d’utilisateur utilisé. | SWAGGER · Facultatif dans le Swagger | F0388 — `$.transactions[].startingActions[].conductors[].details.username` |
| device_id_number | Texte (200) | Identifiant de l’appareil utilisé. | SWAGGER · Facultatif dans le Swagger | F0389 — `$.transactions[].startingActions[].conductors[].details.deviceIdentifierNumber` |
| ip_address | Texte (200) | Adresse IP de la session. | SWAGGER · Facultatif dans le Swagger | F0390 — `$.transactions[].startingActions[].conductors[].details.internetProtocolAddress` |
| online_session_datetime | Texte | Date et heure de session avec décalage UTC. | SWAGGER · Facultatif dans le Swagger | F0391 — `$.transactions[].startingActions[].conductors[].details.dateTimeOfOnlineSession` |
| on_behalf_of_indicator | Oui / non | Indicateur d’exécution pour le compte d’un tiers. | SWAGGER · Facultatif dans le Swagger | F0392 — `$.transactions[].startingActions[].conductors[].details.onBehalfOfIndicator` |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_ON_BEHALF_OF — Le tiers représenté

La personne ou l’entité pour le compte de laquelle agit l’exécutant.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| obo_id | Identifiant | Identifie cette ligne de le tiers représenté. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| conductor_id | Identifiant | Indique pour qui agit cet exécutant. FK vers STR_CONDUCTOR.conductor_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0393 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0394 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].refId` |
| client_number | Texte (100) | Numéro de client connu dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0395 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].details.clientNumber` |
| email_address | Texte (200) | Adresse courriel connue dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0396 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].details.emailAddress` |
| url | Texte (200) | Adresse web connue dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0397 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].details.url` |
| relationship_code | Entier | Lien entre l’exécutant et la personne ou entité représentée. | SWAGGER · Facultatif dans le Swagger | F0398 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].details.relationshipOfConductorCode` |
| relationship_other | Texte (200) | Précision de la relation autre. | SWAGGER · Facultatif dans le Swagger | F0399 — `$.transactions[].startingActions[].conductors[].onBehalfOfs[].details.relationshipOfConductorOther` |
| details_present | Oui / non | Distingue des détails absents d’un objet details vide. Interne; jamais envoyé dans le JSON | INTERNE · Voir règle interne | Interne |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_SOURCE_OF_FUNDS — La source des fonds

La personne ou l’entité désignée comme source des fonds.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| source_id | Identifiant | Identifie cette ligne de la source des fonds. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| starting_action_id | Identifiant | Indique d’où proviennent les fonds. FK vers STR_STARTING_ACTION.starting_action_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0376 — `$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0377 — `$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].refId` |
| account_number | Texte (200) | Numéro de compte associé au rôle. | SWAGGER · Facultatif dans le Swagger | F0378 — `$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].details.accountNumber` |
| policy_number | Texte (100) | Numéro de police associé au rôle. | SWAGGER · Facultatif dans le Swagger | F0379 — `$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].details.policyNumber` |
| identifying_number | Texte (100) | Autre numéro identifiant la participation au flux. | SWAGGER · Facultatif dans le Swagger | F0380 — `$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].details.identifyingNumber` |
| details_present | Oui / non | Distingue des détails absents d’un objet details vide. Interne; jamais envoyé dans le JSON | INTERNE · Voir règle interne | Interne |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_INVOLVEMENT — La personne impliquée

La personne ou l’entité impliquée dans l’action finale.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| involvement_id | Identifiant | Identifie cette ligne de la personne impliquée. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| completing_action_id | Identifiant | Indique qui intervient dans cette action. FK vers STR_COMPLETING_ACTION.completing_action_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0428 — `$.transactions[].completingActions[].involvements[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0429 — `$.transactions[].completingActions[].involvements[].refId` |
| account_number | Texte (200) | Numéro de compte associé au rôle. | SWAGGER · Facultatif dans le Swagger | F0430 — `$.transactions[].completingActions[].involvements[].details.accountNumber` |
| identifying_number | Texte (100) | Autre numéro identifiant la participation au flux. | SWAGGER · Facultatif dans le Swagger | F0431 — `$.transactions[].completingActions[].involvements[].details.identifyingNumber` |
| policy_number | Texte (100) | Numéro de police associé au rôle. | SWAGGER · Facultatif dans le Swagger | F0432 — `$.transactions[].completingActions[].involvements[].details.policyNumber` |
| details_present | Oui / non | Distingue des détails absents d’un objet details vide. Interne; jamais envoyé dans le JSON | INTERNE · Voir règle interne | Interne |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_BENEFICIARY — Le bénéficiaire de l’opération

La personne ou l’entité qui bénéficie de l’action finale.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| beneficiary_id | Identifiant | Identifie cette ligne de le bénéficiaire de l’opération. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| completing_action_id | Identifiant | Indique qui bénéficie de cette action. FK vers STR_COMPLETING_ACTION.completing_action_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0433 — `$.transactions[].completingActions[].beneficiaries[].typeCode` |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0434 — `$.transactions[].completingActions[].beneficiaries[].refId` |
| client_number | Texte (100) | Numéro de client connu dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0435 — `$.transactions[].completingActions[].beneficiaries[].details.clientNumber` |
| username | Texte (100) | Nom d’utilisateur utilisé. | SWAGGER · Facultatif dans le Swagger | F0436 — `$.transactions[].completingActions[].beneficiaries[].details.username` |
| email_address | Texte (200) | Adresse courriel connue dans ce rôle. | SWAGGER · Facultatif dans le Swagger | F0437 — `$.transactions[].completingActions[].beneficiaries[].details.emailAddress` |
| details_present | Oui / non | Distingue des détails absents d’un objet details vide. Interne; jamais envoyé dans le JSON | INTERNE · Voir règle interne | Interne |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Comptes

Par quels comptes ou adresses les fonds passent-ils ?

### STR_ACCOUNT — Le compte

Le compte tel qu’il est décrit pour une action donnée.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| account_id | Identifiant | Identifie cette ligne de le compte. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| starting_action_id | Identifiant | Rattache les données à cette action. FK vers STR_STARTING_ACTION.starting_action_id; facultatif | INTERNE · Voir règle interne | Interne |
| completing_action_id | Identifiant | Rattache les données à cette action. FK vers STR_COMPLETING_ACTION.completing_action_id; facultatif | INTERNE · Voir règle interne | Interne |
| fi_number | Texte (50) | Numéro de l’institution financière du compte. | SWAGGER · Facultatif dans le Swagger | F0360, F0413 — `$.transactions[].startingActions[].details.account.financialInstitutionNumber` (+ 1 autres usages) |
| branch_number | Texte (50) | Numéro de succursale. | SWAGGER · Facultatif dans le Swagger | F0361, F0414 — `$.transactions[].startingActions[].details.account.branchNumber` (+ 1 autres usages) |
| number | Texte (100) | Numéro déclaré dans le contexte de cette table. | SWAGGER · Facultatif dans le Swagger | F0362, F0415 — `$.transactions[].startingActions[].details.account.number` (+ 1 autres usages) |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Facultatif dans le Swagger | F0363, F0416 — `$.transactions[].startingActions[].details.account.typeCode` (+ 1 autres usages) |
| type_other | Texte (200) | Précision du type de compte autre. | SWAGGER · Facultatif dans le Swagger | F0364, F0417 — `$.transactions[].startingActions[].details.account.typeOther` (+ 1 autres usages) |
| currency_code | Texte | Devise des fonds. | SWAGGER · Facultatif dans le Swagger | F0365, F0418 — `$.transactions[].startingActions[].details.account.currencyCode` (+ 1 autres usages) |
| vc_type_code | Texte | Type de monnaie virtuelle. | SWAGGER · Facultatif dans le Swagger | F0366, F0419 — `$.transactions[].startingActions[].details.account.virtualCurrencyTypeCode` (+ 1 autres usages) |
| vc_type_other | Texte (200) | Précision de la monnaie virtuelle autre. | SWAGGER · Facultatif dans le Swagger | F0367, F0420 — `$.transactions[].startingActions[].details.account.virtualCurrencyTypeOther` (+ 1 autres usages) |
| date_opened | Texte | Date d’ouverture du compte. | SWAGGER · Facultatif dans le Swagger | F0368, F0421 — `$.transactions[].startingActions[].details.account.dateOpened` (+ 1 autres usages) |
| date_closed | Texte | Date de fermeture du compte. | SWAGGER · Facultatif dans le Swagger | F0369, F0422 — `$.transactions[].startingActions[].details.account.dateClosed` (+ 1 autres usages) |

À respecter :

- Une seule des clés starting_action_id et completing_action_id est renseignée (XOR). Le parent appartient au même str_report_id.
- Une action a au plus un compte : unicité de chaque clé d’action lorsqu’elle est renseignée.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_ACCOUNT_HOLDER — Les titulaires

Les personnes ou entités titulaires de ce compte.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| holder_id | Identifiant | Identifie cette ligne de les titulaires. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| account_id | Identifiant | Désigne un titulaire de ce compte. FK vers STR_ACCOUNT.account_id; requis | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| type_code | Entier | Discriminant de la structure ou du rôle dans ce contexte. | SWAGGER · Selon le contexte | F0370, F0423 — `$.transactions[].startingActions[].details.account.holders[].typeCode` (+ 1 autres usages) |
| ref_id | Texte | Référence locale à une définition de la même version de déclaration. | SWAGGER · Selon le contexte | F0371, F0424 — `$.transactions[].startingActions[].details.account.holders[].refId` (+ 1 autres usages) |

À respecter :

- Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_VC_DATA — La monnaie virtuelle

Les identifiants et adresses de monnaie virtuelle associés à une action.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| vc_data_id | Identifiant | Identifie cette ligne de la monnaie virtuelle. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| starting_action_id | Identifiant | Rattache les données à cette action. FK vers STR_STARTING_ACTION.starting_action_id; facultatif | INTERNE · Voir règle interne | Interne |
| completing_action_id | Identifiant | Rattache les données à cette action. FK vers STR_COMPLETING_ACTION.completing_action_id; facultatif | INTERNE · Voir règle interne | Interne |
| data_type | Texte | Distingue identifiant de transaction, adresse émettrice et adresse réceptrice. TXN_ID, SENDING_ADDR, RECEIVING_ADDR | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| value | Texte (200) | Identifiant d’opération sur le réseau de monnaie virtuelle. | SWAGGER · Selon le contexte | F0355, F0356, F0357, F0408, F0409, F0410 — `$.transactions[].startingActions[].details.virtualCurrencyTransactionIds[]` (+ 5 autres usages) |

À respecter :

- Une seule des clés starting_action_id et completing_action_id est renseignée (XOR). Le parent appartient au même str_report_id.
- Rang unique par action ET data_type; chaque catégorie reconstitue sa propre liste, vide si aucune ligne.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

## Audit

Qu’a-t-on envoyé et quelle réponse a-t-on reçue ?

### STR_API_SUBMISSION — Le suivi de l’envoi

Une tentative d’envoi ou une consultation de résultats pour une version précise.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| submission_id | Identifiant | Identifie cette ligne de le suivi de l’envoi. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| initial_submission_id | Identifiant | Relie une consultation ou une reprise à l’envoi initial. FK vers STR_API_SUBMISSION.submission_id; facultatif | INTERNE · Voir règle interne | Interne |
| operation | Texte | Nature de l’appel : soumettre, corriger, supprimer ou consulter. SUBMIT, UPDATE, DELETE, VALIDATIONS, RECONCILE | INTERNE · Voir règle interne | Interne |
| environment | Texte | Distingue les essais des envois de production. TEST ou PROD | INTERNE · Voir règle interne | Interne |
| attempt_number | Entier | Ordonne les appels associés à la version. Unique avec str_report_id | INTERNE · Voir règle interne | Interne |
| started_at | Date et heure | Début de l’appel. | INTERNE · Voir règle interne | Interne |
| completed_at | Date et heure | Fin de l’appel, si connue. | INTERNE · Voir règle interne | Interne |
| http_status_code | Entier | Statut réseau; ne signifie pas à lui seul que le rapport est accepté. Facultatif si absence de réponse | INTERNE · Voir règle interne | Interne |
| transport_error | Texte | Explication d’un échec technique. Facultatif | INTERNE · Voir règle interne | Interne |
| processing_status | Texte | État métier déduit de la réponse et des messages. INCONNU, RECU, EN_TRAITEMENT, ACCEPTE, AVERTISSEMENT, REJETE, SUPPRIME | INTERNE · Voir règle interne | Interne |
| external_report_uuid | Texte | Identifiant du rapport renvoyé par CANAFE. Facultatif; conservé comme chaîne | SWAGGER · Facultatif dans le Swagger | F0441 — `SubmitReportResponse$.payload.externalReportUuid` |
| api_response_body | Texte JSON | Réponse complète, avant interprétation; conserve aussi les champs non projetés. Immuable | INTERNE · Voir règle interne | F0438, F0439, F0440, F0442, F0443, F0450, F0451, F0452, F0453, F0454, F0455, F0456, F0457, F0458, F0459, F0460, F0472, F0473, F0474 — `SubmitReportResponse$.code` (+ 18 autres usages) |
| response_sha256 | Texte | Empreinte des octets de la réponse conservée. | INTERNE · Voir règle interne | Interne |
| bulk_reference | Texte | Référence de lot, si le rapport a été transmis en lot. Facultatif | INTERNE · Voir règle interne | Interne |
| correlation_id | Identifiant | Regroupe les lignes qui concernent le même appel de lot. Facultatif | INTERNE · Voir règle interne | Interne |
| file_name | Texte | Nom du fichier transmis, utile pour rapprocher les retours. Facultatif | INTERNE · Voir règle interne | Interne |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_SUBMITTED_PAYLOAD — Le contenu transmis

La copie exacte du document envoyé, conservée avec son empreinte.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| payload_id | Identifiant | Identifie cette ligne de le contenu transmis. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| submission_id | Identifiant | Conserve le document transmis lors de cet appel. FK vers STR_API_SUBMISSION.submission_id; requis | INTERNE · Voir règle interne | Interne |
| payload_json | Texte JSON | Document exact envoyé; on peut donc retrouver ce que CANAFE a reçu. Conserver les octets UTF-8 sans les reformater | INTERNE · Voir règle interne | F0481, F0482, F0483, F0484, F0485, F0486 — `DeleteReport$.reportDetails.reportTypeCode` (+ 5 autres usages) |
| payload_hash_sha256 | Texte | Détecte une modification du contenu archivé. Une empreinte seule ne prouve pas la non-répudiation | INTERNE · Voir règle interne | Interne |
| created_at | Date et heure | Date d’archivage du document. | INTERNE · Voir règle interne | Interne |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_VALIDATION_ERROR — Les messages de validation

Les erreurs et avertissements détectés en interne ou renvoyés par CANAFE.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| error_id | Identifiant | Identifie cette ligne de les messages de validation. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| submission_id | Identifiant | Message reçu dans cette tentative ou consultation. FK vers STR_API_SUBMISSION.submission_id; facultatif | INTERNE · Voir règle interne | Interne |
| origin | Texte | Distingue un contrôle interne d’un message reçu de CANAFE. LOCAL ou CANAFE | INTERNE · Voir règle interne | Interne |
| message_type | Texte | Distingue une validation de structure d’une validation métier. SCHEMA ou METIER | INTERNE · Voir règle interne | Interne |
| severity | Texte | Distingue un avertissement d’un rejet. warning, reject ou unknown; conserve la casse des valeurs API | SWAGGER · Facultatif dans le Swagger | F0449, F0466, F0480 — `SubmitReportResponse$.payload.validationMessages[].type` (+ 2 autres usages) |
| ack_report_reference | Texte | Référence qui permet de rattacher le message à la bonne déclaration. Facultatif; obligatoire pour rapprochement de lot | INTERNE · Voir règle interne | Interne |
| ack_ordinal | Entier | Position de l’accusé dans la réponse de lot. Facultatif | INTERNE · Voir règle interne | Interne |
| detected_at | Date et heure | Date à laquelle le message est connu. | INTERNE · Voir règle interne | Interne |
| ordinal | Entier | Conserve la position dans la liste JSON, même si deux valeurs sont identiques. Commence à 0; unique dans son parent et sa liste | INTERNE · Voir règle interne | Interne |
| instance_path | Texte | Chemin du champ signalé par la validation métier. | SWAGGER · Facultatif dans le Swagger | F0444, F0461, F0467, F0475 — `SubmitReportResponse$.payload.validationMessages[].path` (+ 3 autres usages) |
| rule_id | Texte | Identifiant de règle de validation. | SWAGGER · Facultatif dans le Swagger | F0445, F0462, F0476 — `SubmitReportResponse$.payload.validationMessages[].rule` (+ 2 autres usages) |
| error_code | Nombre exact | Code numérique du résultat dans ce contexte. | SWAGGER · Facultatif dans le Swagger | F0446, F0463, F0477 — `SubmitReportResponse$.payload.validationMessages[].error.code` (+ 2 autres usages) |
| message_en | Texte | Libellé ou message en anglais. | SWAGGER · Facultatif dans le Swagger | F0447, F0464, F0470, F0478 — `SubmitReportResponse$.payload.validationMessages[].error.en` (+ 3 autres usages) |
| message_fr | Texte | Libellé ou message en français. | SWAGGER · Facultatif dans le Swagger | F0448, F0465, F0471, F0479 — `SubmitReportResponse$.payload.validationMessages[].error.fr` (+ 3 autres usages) |
| schema_path | Texte | Chemin dans le schéma utilisé par le validateur. | SWAGGER · Facultatif dans le Swagger | F0468 — `Validations$.acknowledgements[].validationMessages[].schemaPath` |
| keyword | Texte | Mot-clé de validation concerné. | SWAGGER · Facultatif dans le Swagger | F0469 — `Validations$.acknowledgements[].validationMessages[].keyword` |

À respecter :

- Pour CANAFE, submission_id est requis et correspond au même str_report_id. Le terme ERROR du nom historique englobe aussi les avertissements.
- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).

### STR_AUDIT_EVENT — Le journal du dossier

La trace datée des décisions et des changements apportés au dossier.

| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |
|---|---|---|---|---|
| event_id | Identifiant | Identifie cette ligne de le journal du dossier. Clé primaire | INTERNE · Voir règle interne | Interne |
| str_report_id | Identifiant | Appartient à cette version de rapport. FK vers STR_REPORT.str_report_id; requis | INTERNE · Voir règle interne | Interne |
| event_type | Texte | Action consignée dans le dossier. CREATED, EDITED, VALIDATED, FROZEN, SUBMITTED, CORRECTED | INTERNE · Voir règle interne | Interne |
| event_user | Texte | Auteur de l’action. | INTERNE · Voir règle interne | Interne |
| event_timestamp | Date et heure | Moment de l’action. | INTERNE · Voir règle interne | Interne |
| event_details | Texte | Raison ou explication de l’action, en langage courant. | INTERNE · Voir règle interne | Interne |

À respecter :

- Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).
