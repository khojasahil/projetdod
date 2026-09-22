# Alimenter le modèle et conserver les versions

## 1. Préparer une version

Créer STR_REPORT avec un nouveau `str_report_id`, un `report_group_id` et `version_number=1`. Le statut interne commence à BROUILLON. Conserver l’empreinte de la copie Swagger utilisée dans `schema_sha256`.

Ranger les renseignements de `reportDetails`, `detailsOfSuspicion` et `actionTaken` dans REPORT. Ajouter les projets et références liées dans leurs tables. Pour une correction, conserver la référence de déclaration et le numéro d’entité déclarante; une déclaration subséquente distincte reçoit un autre groupe.

## 2. Décrire les personnes et les entités

Créer DEFINITION puis PERSON ou ENTITY selon `type_code`. Reprendre `refId` sans le modifier. Ajouter l’employeur, les identifications, les enregistrements, les personnes autorisées et les listes de propriété selon la variante.

Pour une adresse présente, créer ADDRESS et renseigner `address_id` sur son propriétaire. Ne pas confondre `address_type_code` sur le propriétaire avec `type_code` dans ADDRESS : les deux proviennent de propriétés distinctes du JSON.

## 3. Décrire les opérations

Créer TRANSACTION puis ses STARTING_ACTION et COMPLETING_ACTION. Ajouter les rôles et résoudre leurs références dans les définitions de la même version. Créer le compte et ses titulaires lorsqu’un compte est décrit.

Dans ACCOUNT et VC_DATA, renseigner une seule clé d’action. Pour VC_DATA, utiliser TXN_ID, SENDING_ADDR ou RECEIVING_ADDR selon la liste source. Conserver les rangs des listes, à partir de zéro, sans supprimer les doublons automatiquement.

## 4. Préserver la forme du document

Une liste requise sans ligne devient `[]`. L’absence d’un objet facultatif reste différente d’un objet vide. Une ligne EMPLOYER_INFO vide, par exemple, permet de conserver `employerInformation: {}`. Pour les objets facultatifs fusionnés dans leur parent, les colonnes `action_taken_present` et `details_present` conservent cette distinction.

Les montants, taux et valeurs en dollars canadiens sont des chaînes dans le contrat. Les conserver exactement; ne pas passer par un nombre à virgule flottante. Les calculs éventuels utilisent une conversion décimale contrôlée, distincte de la valeur à transmettre.

## 5. Contrôler puis geler

Valider les propriétés requises, les variantes, les codes, les longueurs, les motifs et les règles métier conditionnelles. Contrôler aussi les clés, les rangs, les références de rôles et l’isolation par version. Les anomalies connues du contrat sont décrites dans [REGLES.md](REGLES.md).

Produire le JSON avec les seuls champs applicables au type de définition. Les identifiants internes, les rangs et les indicateurs de présence ne sont pas envoyés. Une fois le contenu approuvé pour transmission, renseigner `frozen_at` et empêcher sa modification, y compris celle de ses enfants.

## 6. Envoyer et conserver les retours

Créer une ligne API_SUBMISSION pour chaque appel, avec l’opération, l’environnement, le numéro de tentative et les dates. Pour un appel avec corps, conserver les octets UTF-8 exacts dans SUBMITTED_PAYLOAD et leur empreinte SHA-256. Un champ texte logique devra être implanté sans normalisation des fins de ligne ni reformattage; un stockage binaire peut être retenu pour préserver strictement les octets.

Conserver le statut HTTP, l’erreur réseau éventuelle, la réponse exacte et son empreinte. Projeter l’identifiant externe et les messages utiles. Ne jamais déduire l’acceptation du seul statut HTTP. Pour une consultation, créer une nouvelle ligne reliée à l’appel initial par `initial_submission_id`; conserver chaque réponse, même si elle ne change pas le résultat.

VALIDATION_ERROR porte `origin=CANAFE` ou LOCAL. Les valeurs API de gravité sont `warning` et `reject`; `unknown` est un état interne lorsque la gravité n’est pas déterminée. `message_type` distingue SCHEMA et METIER, en s’appuyant notamment sur `messageTypeCode` des accusés lorsqu’il est présent. Le chemin, la règle, le code et les messages bilingues restent traçables.

Une réponse doit être rattachée à la bonne déclaration et au bon environnement. En cas de délai réseau dépassé, conserver un résultat inconnu et rechercher le résultat de l’appel avant de retransmettre. Une nouvelle tentative ne garantit pas à elle seule l’absence de doublon.

## 7. Corriger le contenu

Créer une nouvelle ligne REPORT avec le même `report_group_id`, le numéro de version suivant et `previous_report_id`. Copier les lignes métier dans la nouvelle version en attribuant de nouvelles clés internes et en reconstruisant leurs liens. Ne pas faire pointer les enfants de la version 2 vers les lignes de la version 1.

La référence déclarative reste stable. La correction individuelle utilise le code de soumission prévu par le contrat. Les anciens envois, archives et résultats restent liés à leur version d’origine. Consigner la raison de la correction dans AUDIT_EVENT.

Une suppression CANAFE utilise un document DeleteReport archivé avec l’appel DELETE. Elle ne supprime pas l’historique local du rapport.

## Cas des lots

Les mêmes quatre tables d’Audit peuvent conserver un appel de lot, sans ajouter de table. Chaque version concernée possède une ligne de suivi. Les lignes du même appel partagent `correlation_id`; `bulk_reference` et `file_name` facilitent le rapprochement. Le même corps exact et la même réponse peuvent être archivés pour chaque version : cette duplication est assumée dans ce modèle compact.

Les compteurs de lot restent des compteurs de lot. L’accusé individuel est recherché par sa référence déclarative et son contexte d’appel. `ack_report_reference` et `ack_ordinal` permettent de situer un message dans la réponse. Un accusé sans message reste dans la réponse archivée. Un accusé non rapproché reste conservé sans attribuer arbitrairement son résultat à une version.

Le Swagger décrit le chargement d’un fichier binaire JSON, mais ne suffit pas à préciser complètement l’enveloppe métier du fichier. Sa production et les scénarios de réponse de lot restent à confirmer avec la documentation d’intégration et les essais autorisés.

## Exemple à lire

[str-v1.json](../examples/str-v1.json) et [str-v2.json](../examples/str-v2.json) montrent un rapport fictif et sa correction. Les codes et références servent à illustrer le stockage; ces fichiers n’ont pas été envoyés à CANAFE. [parcours-metier.json](../examples/parcours-metier.json) montre un extrait de lignes pour comprendre le lien entre version et tentative.
