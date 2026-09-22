# Règles du modèle et limites du contrat

## Trois origines de règles

Le Swagger décrit la structure du document : propriétés requises, variantes, listes, codes, formats et longueurs. Ses descriptions contiennent aussi certaines règles conditionnelles. Le modèle ajoute les règles internes nécessaires aux versions, aux clés et à l’audit. Ces trois origines restent distinctes dans la documentation.

Un champ facultatif dans le schéma ne démontre pas qu’il est facultatif dans toutes les situations réglementaires. Le présent livrable analyse le contrat technique; les obligations de déclaration applicables sont à valider avec les responsables métier.

## Cardinalités et présence avant envoi

| Relation ou propriété | Règle du contrat ou du modèle |
|---|---|
| Groupe de rapport → versions REPORT | Une ou plusieurs versions; numéros uniques, chaîne sans branche ni cycle. |
| Rapport → reportDetails et detailsOfSuspicion | Deux objets requis, fusionnés dans REPORT. |
| Rapport → actionTaken | Objet facultatif; présence conservée par `action_taken_present`. |
| Rapport → transactions | Liste requise avec au moins un élément. |
| Rapport → definitions et relatedReports | Listes requises; peuvent être vides dans le schéma. |
| Soupçon → projets PPP | Liste requise, sans minimum d’éléments. |
| Transaction → suspiciousTransactionDetails | Objet requis, fusionné dans TRANSACTION. |
| Transaction → actions initiales et finales | Deux listes requises; pas de minimum d’éléments dans le schéma. |
| Action initiale → details, sources, conductors | Objet details requis; les deux listes sont requises mais peuvent être vides. |
| Conductor → details et onBehalfOfs | Objet et liste requis; liste pouvant être vide. |
| Action finale → details, involvements, beneficiaries | Objet details requis; les deux listes sont requises mais peuvent être vides. |
| Action → compte | Zéro ou un compte. |
| Compte → titulaires | Liste requise, sans minimum d’éléments. |
| Définition → PERSON ou ENTITY | Une seule ligne, selon le type : personne 1/3/5, entité 2/4/6. |
| Personne de type 5 → employeur | Zéro ou une ligne. |
| Entité de type 6 → sept listes de propriété et direction | Sept listes requises; peuvent être vides dans le schéma. |
| Propriétaire d’adresse → adresse | Zéro ou une adresse; variante structurée ou libre. |
| Appel → document transmis | Zéro ou un document; obligatoire en interne pour un appel contenant un corps. |
| Appel → messages projetés | Zéro ou plusieurs; la réponse entière reste archivée même sans message. |

Ces règles détaillent les exigences avant gel. Les vues métier utilisent des cardinalités de stockage qui autorisent la préparation progressive des brouillons. [structures.csv](../traceability/structures.csv) donne les autres objets et listes, leurs variantes et leur présence requise.

## Intégrité à implanter

1. Chaque enfant porte le même `str_report_id` que son parent. Une clé d’enfant vers un sous-objet se contrôle avec `(str_report_id, clé_du_parent)`. Prévoir les contraintes d’unicité correspondantes sur les parents.
2. Dans un groupe de rapport, `version_number` est unique. Le prédécesseur est la version précédente du même groupe; un prédécesseur n’a qu’un successeur. Le groupe conserve l’identité déclarative. Aucune suppression en cascade ne détruit une version gelée et ses archives.
3. Dans DEFINITION, `(str_report_id, ref_id)` est unique; le triplet avec `type_code` l’est aussi pour les références de rôles. PERSON et ENTITY sont uniques par `definition_id`. Une seule des deux existe selon le code.
4. Les sources des fonds, implications et titulaires référencent les types 1 ou 2; les bénéficiaires les types 3 ou 4; les exécutants et tiers représentés les types 5 ou 6.
5. Chaque rang commence à zéro et est unique et contigu dans sa liste au gel. Pour VC_DATA, la liste est identifiée par l’action et `data_type`. Pour les messages, elle inclut le contexte d’accusé. Ne pas rendre les valeurs métier uniques sans règle source.
6. ACCOUNT et VC_DATA ont exactement une clé d’action renseignée. Chaque action a au plus un ACCOUNT. Une adresse appartient à un seul propriétaire dans la version, y compris entre les différentes tables propriétaires.
7. Une colonne de présence fausse interdit les valeurs du sous-objet. Une valeur vraie permet un objet vide si le contrat le permet. Les objets matérialisés par une table enfant utilisent l’existence de la ligne comme présence.
8. Une erreur d’origine CANAFE possède un `submission_id` de la même version. Une erreur locale peut exister avant tout appel. Les consultations et reprises pointent vers l’appel initial de la même version.

## Reconstruire le JSON

Le code de rapport DOD est 102. Pour l’envoi individuel, `submitTypeCode=1` désigne l’initial et 2 la correction; 5 concerne DeleteReport. Les clés internes, les rangs et les indicateurs de présence ne sont jamais transmis. Les objets et listes requis sont émis même lorsqu’ils sont vides si le contrat l’autorise.

Les montants sont des chaînes : `"10.00"` respecte le motif de currencyAmount, `"10.0"` ne le respecte pas. Les dates doivent aussi être des dates de calendrier valides; une expression régulière ne suffit pas toujours.

Les deux codes d’adresse, sur le propriétaire et à l’intérieur de l’adresse, sont conservés séparément. Les propriétés transmises dépendent de la variante active. La casse de refId et des autres valeurs est préservée.

`additionalProperties:false` s’applique seulement là où le Swagger le déclare. Le modèle couvre les propriétés nommées. Des propriétés additionnelles non décrites ne sont pas promises comme colonnes relationnelles; le document transmis et les réponses conservent leur forme exacte dans les archives.

## Règles décrites et anomalies à ne pas masquer


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


## Lire les résultats

Le statut HTTP, le résultat global d’un lot et le résultat d’une déclaration sont différents. Un avertissement n’est pas un rejet. Les valeurs reçues restent dans la réponse archivée; `processing_status` est une interprétation interne traçable, pas une colonne directement fournie par tous les endpoints.

Pour un lot, rapprocher l’accusé par la référence de déclaration dans le contexte d’appel et d’environnement. Un accusé non rapproché reste dans l’archive sans attribution arbitraire. Chaque consultation crée une nouvelle ligne API_SUBMISSION : aucune réponse précédente n’est écrasée.

Le Swagger ne définit pas ici de clé d’idempotence garantissant l’absence de doublon. Après une interruption réseau, rechercher le résultat avant une nouvelle tentative.
