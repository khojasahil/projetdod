# Alimenter le modèle et suivre les soumissions

## 1. Création d’une déclaration

1. Créer `STR_REPORT` pour l’identité durable du dossier déclaratif.
2. Créer `STR_VERSION` avec `version_number=1`, la référence de déclaration et la copie du contrat utilisée (`schema_release_id`). Les données peuvent rester incomplètes à l’état `DRAFT`.
3. Renseigner les champs scalaires de `reportDetails` et `detailsOfSuspicion`. Positionner `action_taken_present` selon que `actionTaken` doit être absent ou présent.
4. Insérer les définitions : une ligne `STR_DEFINITION` puis exactement une ligne du sous-type correspondant. Utiliser le même `id` pour le sous-type. Conserver le `ref_id` qui sera émis dans le JSON.
5. Insérer les objets répétitifs sous leur parent : identifications, personnes autorisées, enregistrements, listes de propriété effective, projets PPP et rapports connexes. Donner un `ordinal` commençant à 0 dans chaque liste.
6. Insérer les opérations puis leurs actions initiales et finales. Ajouter les comptes et titulaires, les listes de monnaies virtuelles et les rôles.
7. Pour chaque rôle, résoudre la référence `(version_id, type_code, ref_id)` vers une définition de la même version. Une définition peut être utilisée par plusieurs rôles compatibles.
8. Contrôler les obligations structurelles, les références, les domaines de codes et les règles métier retenues. Produire le JSON à partir des correspondances documentées.
9. Passer la version à `FROZEN`, fixer `frozen_at` et créer un événement d’audit. Les données métier de cette version deviennent immuables. Les événements et états de suivi peuvent continuer à évoluer sans modifier cette photographie.

Une insertion transactionnelle de chaque agrégat évite de laisser un rôle sans définition ou un sous-type sans parent. Aucune donnée réelle n’est fournie dans ce dépôt.

## 2. Exemple de placement

Les fichiers [str-v1.json](../examples/str-v1.json) et [str-v2.json](../examples/str-v2.json) sont entièrement fictifs. Ils illustrent les six variantes de définitions, les deux formats d’adresse, un compte, un exécutant, un tiers représenté, des sources de fonds et un bénéficiaire.

| Donnée JSON | Table / colonne | Placement |
|---|---|---|
| `reportDetails.reportingEntityReportReference` | `STR_VERSION.report_details__reporting_entity_report_reference` | Même référence pour v1 et sa correction v2. |
| `definitions[4].refId` | `STR_DEFINITION.ref_id` | `EXEC-P5`, avec `type_code=5`, version propre à v1 ou v2. |
| `definitions[4].givenName` | `STR_PERSON_EMPLOYER.given_name` | Ligne de sous-type ayant le même `id` que sa définition. |
| `definitions[4].address.typeCode` | `STR_PERSON_EMPLOYER.address__type_code` | Discriminant intérieur; ne pas confondre avec `address_type_code`. |
| `transactions[0].startingActions[0].details.amount` | `STR_STARTING_ACTION.details__amount` | Chaîne `1250.00`, conservée sans conversion flottante. |
| `...startingActions[0].conductors[0].refId` | `STR_CONDUCTOR.ref_id` | Référence à `EXEC-P5` dans la même version. |
| `...conductors[0].onBehalfOfs[0].refId` | `STR_ON_BEHALF_OF.ref_id` | Référence à `TIERS-E6`, type 6. |
| `...details.account.holders[0].refId` | `STR_STARTING_ACTION_ACCOUNT_HOLDER.ref_id` | Référence à `NOM-P1`, type 1. |

Les listes obligatoires vides donnent zéro ligne enfant et se reconstruisent comme `[]`. Pour une liste facultative, l’indicateur de présence du parent décide si elle est omise ou émise.

## 3. Envoi individuel et nouvelle tentative

Créer une enveloppe `STR_DISPATCH` en mode `SINGLE`, puis un élément `STR_DISPATCH_ITEM` pointant vers la version gelée. Archiver les octets du document effectivement envoyé dans `STR_ARTIFACT` et leur empreinte SHA-256. L’archive correspond au document déclaratif, pas aux secrets ni aux en-têtes d’authentification du transport.

Chaque appel crée une ligne `STR_API_EXCHANGE`, avec sa méthode, son chemin, son numéro d’ordre dans l’envoi, ses dates, son statut HTTP et les références d’archives. Une nouvelle tentative crée un nouvel échange. Elle ne crée pas à elle seule une nouvelle version métier. Une charge utile modifiée requiert une nouvelle version et un nouvel élément d’envoi.

| Usage | Endpoint du Swagger | Conservation |
|---|---|---|
| Soumettre | `POST /api/v1/reports`, requête multipart avec `reportFile`; paramètre `reportTypeCode=102` | Version gelée, document exact, échange, `STR_SUBMIT_RESPONSE`. |
| Corriger | `PUT /api/v1/reports`, requête multipart avec `reportFile` | Nouvelle version avec `submitTypeCode=2`, nouvel envoi, même identité déclarative. |
| Supprimer | `DELETE /api/v1/reports`, corps JSON `DeleteReport` | `STR_DELETE_REQUEST`, motif, version visée, échange; succès documenté HTTP 204 sans corps obligatoire. |
| Consulter les résultats | `GET /api/v1/reports/validations` | Un résultat immuable par consultation; accusés et messages enfants. |
| Rapprocher les références | `GET /api/v1/reports/list` | Réponse brute archivée; projection spécialisée à ajouter si nécessaire. |

Le préfixe serveur relatif publié est `/reporting-ingest`. La sélection du serveur réel et des identifiants d’accès appartient à la configuration d’environnement. Aucun appel de ces endpoints n’est exécuté par les outils de ce dépôt.

## 4. Lots

Créer une enveloppe `BULK` et un élément pour chaque version DOD. Conserver `bulk_reference` et `file_name`. Obtenir l’URL de transfert via `GET /api/v1/bulkSubmission`, déposer le document de lot sur l’URL retournée, puis consulter `/api/v1/reports/validations`.

Le Swagger décrit le transfert du lot comme un fichier binaire JSON; il n’explicite pas dans cette opération une enveloppe métier complète de lot. Le modèle couvre le suivi et les résultats de lots. La construction exacte du fichier de lot doit être confirmée avec la documentation opérationnelle CANAFE avant implantation. Aucun format d’enveloppe non documenté n’est inventé ici.

L’URL signée temporaire ne doit pas être conservée avec son jeton SAS dans les journaux. Conserver un chemin expurgé et les métadonnées utiles. Les secrets OAuth relèvent du gestionnaire de secrets.

## 5. Réception des résultats

1. Archiver les octets de réponse et le statut HTTP.
2. Projeter les champs connus vers `STR_SUBMIT_RESPONSE`, `STR_VALIDATION_RESULT` ou `STR_API_ERROR`, selon la réponse reçue.
3. Insérer chaque accusé dans `STR_VALIDATION_RESULT_ACK`, puis ses messages dans la table enfant. `message_type_code` précise si le contenu est une validation de schéma ou métier.
4. Rechercher l’élément d’envoi dans le même contexte de soumission à partir de la référence de déclaration. Créer `STR_ACK_LINK` seulement si la correspondance est certaine. Conserver sans lien les accusés encore non rapprochés.
5. Présenter à l’utilisateur un état dérivé du dernier résultat pertinent. Le modèle ne stocke pas un simple booléen « accepté » qui écraserait les états intermédiaires ou les avertissements.

Exemples fictifs : [réponse individuelle](../examples/submit-response.json) et [résultat de validation](../examples/validation-result.json). Le second illustre l’ambiguïté `oneOf` du contrat décrite dans [REGLES.md](REGLES.md); il sert à vérifier la conservation des messages, pas à attester une réponse certifiée par CANAFE.

## 6. Correction et suppression

Pour une correction, copier la photographie v1 dans v2 avec de nouveaux identifiants internes, y compris les définitions et leurs dépendances. Conserver les `refId` si les mêmes liens logiques restent utiles; les clés composites incluent la nouvelle version. Modifier uniquement v2, lier `previous_version_id` à v1, valider puis geler v2. L’archive v1 reste intacte.

Une suppression CANAFE ne supprime aucune ligne historique locale. Elle crée une demande `DeleteReport`, liée à l’élément d’envoi et à la version visée. Le motif `3` indique un duplicata et `4` une soumission par erreur. Le [fichier fictif de suppression](../examples/delete-request.json) utilise le code de déclaration `102` et `submitTypeCode=5`.

## 7. Mesures d’exploitation à prévoir lors de l’implantation

Limiter l’accès aux données nominatives et aux récits; chiffrer les données et archives selon les standards de l’organisation; journaliser les consultations et modifications utiles. Définir avec les responsables métier les durées de conservation, le traitement des demandes de correction et la gestion des droits. Ces mécanismes ne sont pas fournis par un diagramme de données.

Un pilote doit notamment vérifier les réponses réelles de CANAFE, le comportement de reprise après interruption et les règles conditionnelles métier. Les outils de ce dépôt contrôlent le modèle localement et ne remplacent pas ces essais d’intégration.
