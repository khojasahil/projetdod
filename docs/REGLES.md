# Règles, cardinalités et limites du contrat

## 1. Trois niveaux de règles

| Niveau | Origine | Application |
|---|---|---|
| Structure | `required`, `enum`, `pattern`, `oneOf`, cardinalités et autres mots-clés du Swagger | Valider le document produit contre la copie de contrat liée à la version. |
| Règle décrite | Texte descriptif du Swagger, parfois non encodé dans les mots-clés | Ajouter un contrôle métier explicite et traçable. |
| Conception interne | Historique, clés, intégrité, audit, gel | Maintenir un stockage cohérent et une preuve des transmissions. |

Les exigences de conformité au-delà du contrat technique doivent être validées par les responsables métier. Les champs facultatifs dans OpenAPI ne sont pas une preuve qu’ils sont facultatifs dans toute situation réglementaire.

## 2. Cardinalités avant gel

| Relation | Cardinalité par parent | Source / justification |
|---|---|---|
| Déclaration → versions | 1..N pour un dossier initialisé | Interne |
| Version → `reportDetails` | 1 | `STRReport.required` |
| Version → `detailsOfSuspicion` | 1 | `STRReport.required` |
| Version → `actionTaken` | 0..1 | Absent de `STRReport.required` |
| Version → opérations | 1..N | `transactions.required` au niveau racine et `minItems: 1` |
| Version → définitions | 0..N, propriété présente | `definitions` est requis, sans `minItems` |
| Version → rapports connexes | 0..N, propriété présente | `relatedReports` est requis, sans `minItems` |
| Soupçon → projets PPP | 0..N, propriété présente | `publicPrivatePartnershipProjectNameCodes` requis |
| Opération → détails de l’opération douteuse | 1 | Objet requis |
| Opération → actions initiales / finales | 0..N pour chacune, propriétés présentes | Listes requises sans minimum d’éléments |
| Action initiale → détails / sources / exécutants | 1 objet; 0..N sources; 0..N exécutants | Trois propriétés requises |
| Exécutant → détails / tiers représentés | 1 objet; 0..N tiers | Propriétés requises |
| Action finale → détails / implications / bénéficiaires | 1 objet; 0..N pour chaque liste | Trois propriétés requises |
| Action → compte | 0..1 | `details.account` facultatif |
| Compte → titulaires | 0..N, propriété présente | `strAccount.required` contient `holders` |
| Définition → sous-type | Exactement 1 des six | `oneOf`; choix de stockage supertype / sous-type |
| Définition de type 6 → sept listes de propriété effective | 0..N chacune, propriétés présentes | Sept listes requises, sans minimum d’éléments |
| Objet propriétaire → adresse | 0..1 | Adresse facultative, deux variantes exclusives |
| Envoi → éléments | 1..N; exactement 1 en mode SINGLE | Interne |
| Envoi → appels | 0..N | Interne; l’envoi peut être préparé avant le premier appel |
| Appel → chaque projection de réponse | 0..1 | Interne; choisir la projection correspondant à la réponse réelle |

Dans le diagramme, `1 → 0..N` décrit la possibilité de stockage, y compris les brouillons. Les minimums requis au gel sont indiqués ici et dans `structures.csv`. Une flèche va toujours du parent vers l’enfant.

## 3. Intégrité relationnelle

1. Chaque ligne de données DOD dépend d’une seule `STR_VERSION`. Les liens enfant-parent transportent aussi `version_id`; un simple identifiant de parent ne suffit pas à documenter l’isolation entre versions.
2. Lorsque le parent est `STR_VERSION`, `parent_id=version_id`. Lorsque le parent est un sous-objet, la clé étrangère logique porte sur `(version_id, parent_id)` vers `(version_id, id)` du parent.
3. Un sous-type a `id=STR_DEFINITION.id` et le même `version_id`. Une définition de type 5 possède une ligne `STR_PERSON_EMPLOYER`, aucune ligne des cinq autres sous-types.
4. Les références de rôles utilisent `(version_id, type_code, ref_id)`. Domaines : sources, implications et titulaires `{1,2}`; bénéficiaires `{3,4}`; exécutants et tiers `{5,6}`.
5. Chaque liste a un `ordinal >= 0`, unique dans le parent. Les ordinalités sont contiguës à partir de 0 au gel. Ne pas rendre la valeur métier unique : le Swagger n’impose généralement pas `uniqueItems`.
6. Une table enfant d’un objet singulier a `UNIQUE(parent_id)`. Les identifiants de sous-types ont déjà une clé primaire partagée.
7. Un indicateur de présence faux interdit toutes les valeurs ou lignes du sous-objet. Un indicateur vrai avec aucune ligne autorise `[]` seulement si le minimum le permet.
8. Aucune suppression en cascade n’efface une version gelée, son envoi, ses archives ou ses résultats. Les règles de conservation physiques restent à définir par l’organisation.
9. `previous_version_id` doit viser le même `report_id` et une version antérieure. Numéros uniques par déclaration; aucun cycle. Une correction conserve l’identité déclarative; un nouveau rapport subséquent possède une nouvelle identité et peut utiliser `relatedReports`.
10. La référence de déclaration, avec le numéro d’entité déclarante, doit identifier sans ambiguïté la déclaration durable dans l’organisation. La recherche des résultats ajoute le contexte d’environnement et d’envoi. Les versions d’une correction conservent la même référence; un nouvel identifiant CANAFE reçu n’est jamais inventé.

## 4. Règles de sérialisation

- Le code de déclaration DOD est `102`; pour un envoi individuel initial, `submitTypeCode=1`; pour une correction, `2`. `5` concerne la suppression, émise avec `DeleteReport`.
- La version contient un `STRReport` complet; une demande `DeleteReport` est liée séparément à l’élément d’envoi et reprend les identifiants de la version visée.
- Les clés internes, `ordinal`, `version_id` et indicateurs `*_present` ne sont jamais transmis.
- Toute liste requise sans élément produit `[]`. Une liste facultative sans présence produit une propriété absente.
- Les montants restent des chaînes. Par exemple `"10.00"` est autorisé par le motif de `currencyAmount`, `"10.0"` ne l’est pas. Le contrôle de dates doit aussi vérifier une date de calendrier réelle; la seule expression régulière n’écarte pas tous les jours impossibles.
- Choisir les propriétés de la variante d’adresse active; distinguer les deux `typeCode` intérieur et extérieur. Conserver le `refId` exact, y compris casse et caractères permis.
- `additionalProperties:false` s’applique uniquement aux objets où il est déclaré. Plusieurs schémas réutilisables, par exemple `PersonName` et `StructuredAddress`, ne le précisent pas. Le modèle projette leurs propriétés nommées; l’archive exacte peut conserver un document reçu contenant d’autres propriétés. La génération proposée utilise une liste explicite des champs connus.

## 5. Règles décrites et anomalies à ne pas masquer

| Référence | Observation | Traitement proposé |
|---|---|---|
| `STRReport...startingActions[].details.fundAssetVirtualCurrencyTypeCode.description` | Valeurs permises selon `direction` : entrée `{1,2,3,4,5,6,8,9,10,11,12,13,14,16,17}`, sortie `{3,7,9,16,17}`. | Contrôle métier supplémentaire; l’enum globale ne suffit pas. |
| `STRReport.reportDetails.minItems:1` | `minItems` est posé sur un objet, pas sur une liste. | Ne pas l’interpréter comme une obligation supplémentaire de champ. Utiliser `required`. |
| `DeleteReport.reportDetails.reportSubmitReasonCode.required` | La liste `required` est placée dans la propriété scalaire, plutôt que sur `reportDetails`. | Le mapping conserve la position réelle. Exiger les six champs de `reportDetails` comme règle interne prudente et confirmer le comportement API. Ne pas corriger silencieusement la source. |
| `Validations.status.code` | L’enum contient `2021`, tandis que la description mentionne `5021`. | Préserver le code reçu et la réponse brute. Signaler l’écart; ne pas remplacer automatiquement un code par l’autre. |
| `Validations...validationMessages.items.oneOf` | Les deux schémas n’ont pas de listes `required` discriminantes et autorisent des propriétés non précisées. Un objet peut donc satisfaire les deux. | Le test strict de `oneOf` peut être ambigu. Utiliser `messageTypeCode` de l’accusé pour l’interprétation métier, conserver l’archive, et faire confirmer la spécification. |
| `ProvinceStateCode.oneOf` | Trois listes de codes et une branche générale de deux caractères se recouvrent. Par exemple `QC` satisfait deux branches. | Conserver la valeur et les quatre branches dans la traçabilité. Faire confirmer le comportement du validateur CANAFE; ne pas transformer silencieusement `oneOf` en `anyOf`. Les exemples structurés utilisent le nom de province pour ne pas dépendre de cette ambiguïté. |
| `activitySectorCode` | 25 valeurs explicites, dont les codes vont jusqu’à 28 avec des trous. | Ne pas confondre valeur maximale et nombre de valeurs. |
| `CountryCode`, `CurrencyCode`, `VirtualCurrencyCode` | Domaines intégrés à cette copie du Swagger. | Ne pas remplacer automatiquement par une liste ISO ou externe plus récente. |

Ces observations sont tirées du [YAML archivé](../source/swaggerExternal.yaml). Les JSON Pointers et lignes détaillés sont dans les fichiers de traçabilité.

## 6. Interprétation des réponses

Le statut HTTP, le code de traitement d’un lot et le résultat individuel sont trois informations différentes. Un dépôt de lot réussi au transport ne prouve pas l’acceptation de ses déclarations. Les avertissements ne sont pas des rejets.

Chaque consultation des validations crée un nouvel échange et un nouveau résultat. Ne jamais remplacer la réponse précédente. `STR_ACK_LINK` rattache chaque accusé au bon élément du même envoi. Un accusé sans correspondance reste conservé et non rapproché; il ne doit pas être assigné arbitrairement.

Pour `STR_VALIDATION_RESULT_ACK_MESSAGE`, la variante active est déterminée par `STR_VALIDATION_RESULT_ACK.message_type_code` : 1 = schéma; 2 = métier. Les champs non applicables restent absents. Le modèle conserve toutes les propriétés nommées des deux variantes malgré l’ambiguïté OpenAPI signalée ci-dessus.

Après un délai réseau dépassé, le résultat est inconnu. Consulter les rapports ou validations avant de retransmettre; le Swagger ne déclare pas ici une clé d’idempotence qui garantirait à elle seule l’absence de doublon.
