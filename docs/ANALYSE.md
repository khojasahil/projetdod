# Analyse du Swagger et modèle proposé

## 1. Finalité

Le modèle est une base de préparation et de preuve des déclarations DOD. Il doit permettre de saisir les données, constituer une version cohérente, produire un document `STRReport`, conserver ce document, puis rapprocher chaque retour de CANAFE de l’envoi qui l’a provoqué.

Ce n’est pas un référentiel central de clientèle. Une personne, un compte ou une adresse représente l’information déclarée dans une version donnée. Une modification du dossier client courant ne doit jamais réécrire une déclaration déjà envoyée. Un éventuel lien vers les systèmes sources pourra être ajouté lors de l’intégration, dans des colonnes internes documentées séparément.

La [directive DOD de CANAFE](https://fintrac-canafe.canada.ca/guidance-directives/transaction-operation/str-dod/str-dod-fra) décrit les opérations tentées et effectuées et l’importance des faits, du contexte et des indicateurs qui fondent les soupçons. Le modèle conserve donc le récit du soupçon, les mesures prises et le détail des opérations. Il ne décide pas automatiquement si le seuil de déclaration est atteint.

## 2. Périmètre du contrat

| Élément | Traitement |
|---|---|
| `STRReport` | Tous les champs nommés, objets, listes et variantes accessibles sont projetés dans le modèle. |
| Six variantes de `definitions[]` | Couvertes individuellement : types 1 à 6. |
| `strAccount`, adresses, identifications, propriété effective | Couvertes dans leur contexte DOD. |
| `SubmitReportResponse`, `Validations`, `ValidationMessage`, `SchemaValidationMessages` | Projections normalisées pour exploiter les résultats. |
| `ErrorWithValidation` | Projection des erreurs et messages; les autres réponses restent aussi archivables sous forme brute. |
| `DeleteReport` | Demande de suppression distincte de la photographie DOD. |
| Envois individuels et lots | Enveloppe, éléments, appels, archives et rapprochement des accusés. |
| `LVCTRReport`, `LCTRReport`, `EFTRReport`, `CDRReport` | Hors périmètre métier. Ils restent dans la copie officielle complète du Swagger. |
| Jetons OAuth et URL SAS | Hors modèle déclaratif; ne pas archiver les secrets dans les champs d’audit. |
| Réponses de liste, santé, obtention d’URL de lot | Archivables dans les échanges; leurs projections détaillées ne sont pas incluses dans le dictionnaire métier. |

Le code de type de déclaration est **102** pour ce projet. Le domaine partagé `reportTypeCode` du Swagger contient d’autres codes; sa réutilisation ne signifie pas que le modèle couvre leurs données.

## 3. Trois identités différentes

| Identité | Table | Pourquoi |
|---|---|---|
| Déclaration durable | `STR_REPORT` | Regroupe toutes les révisions d’un même dossier déclaratif. |
| Photographie des données | `STR_VERSION` | Fixe les faits connus et les personnes/opérations déclarées à un instant donné. |
| Envoi et appels réels | `STR_DISPATCH`, `STR_DISPATCH_ITEM`, `STR_API_EXCHANGE` | Une version peut subir plusieurs tentatives; un appel peut échouer sans que le contenu change. |

La référence CANAFE fournie par l’entité déclarante reste dans `reportDetails.reportingEntityReportReference`. Elle n’est pas remplacée par l’identifiant interne. L’identifiant externe renvoyé par CANAFE est conservé dans `STR_SUBMIT_RESPONSE.payload__external_report_uuid`; il reste textuel, car le Swagger le décrit comme une chaîne et non comme un UUID SQL.

## 4. Organisation des données

`STR_VERSION` porte les objets scalaires `reportDetails`, `detailsOfSuspicion` et `actionTaken`. Les propriétés de ces objets sont intégrées à la table avec un préfixe, par exemple `report_details__reporting_entity_number`. Le double soulignement marque une frontière d’objet JSON.

Toute liste répétitive possède une table enfant avec un `ordinal`. On peut donc restituer deux éléments identiques et leur ordre initial. Une liste de références de transactions n’est pas stockée dans une seule chaîne séparée par des virgules.

Les actions initiales et finales restent séparées : elles ont des attributs, des rôles et des codes différents. Les fonds d’origine, exécutants, tiers représentés, personnes impliquées et bénéficiaires occupent leurs propres tables. Les détails d’un rôle appartiennent à l’occurrence de ce rôle, pas à la définition de personne partagée.

## 5. Définitions : supertype et six sous-types

| `typeCode` | Schéma Swagger | Table de détail | Utilisation dans les rôles du STR |
|---|---|---|---|
| 1 | `PersonName` | `STR_PERSON_NAME` | Sources de fonds, implications, titulaires de compte |
| 2 | `EntityName` | `STR_ENTITY_NAME` | Sources de fonds, implications, titulaires de compte |
| 3 | `PersonDetails` | `STR_PERSON_DETAILS` | Bénéficiaires d’actions finales |
| 4 | `EntityDetails` | `STR_ENTITY_DETAILS` | Bénéficiaires d’actions finales |
| 5 | `personAndEmployerDetails` | `STR_PERSON_EMPLOYER` | Exécutants et tiers représentés |
| 6 | `entityAndBeneficialOwnershipDetails` | `STR_ENTITY_OWNERSHIP` | Exécutants et tiers représentés |

`STR_DEFINITION` porte `type_code`, `ref_id`, l’ordre et la version. Un sous-type utilise la même clé interne que son parent. Ce découpage rend visibles les propriétés permises pour chaque variante et évite une table personne où tous les champs sembleraient disponibles pour tous les rôles.

Le choix d’un `ref_id` unique par version est une règle d’intégrité interne destinée à éliminer toute ambiguïté. Le Swagger donne le format du champ et les domaines de type; ses contraintes de structure ne remplacent pas une vérification des références. Les rôles pointent vers `(version_id, type_code, ref_id)`, ce qui interdit une référence à une autre version ou à un type incompatible.

La même personne réelle peut devoir avoir plusieurs définitions, de types différents. Le modèle ne déduit aucune fusion d’identité à partir d’un nom identique.

## 6. Adresses et comptes

Une adresse a au plus une occurrence par propriétaire dans les objets modélisés. Ses colonnes sont donc intégrées au propriétaire. Cela élimine les liens génériques `owner_type` / `owner_id` qui ne constituent pas une clé étrangère relationnelle ordinaire.

Les deux champs suivants sont distincts :

- `addressTypeCode` → `address_type_code` : propriété extérieure à l’objet adresse;
- `address.typeCode` → `address__type_code` : discriminant de `StructuredAddress` ou `UnstructuredAddress`.

Le domaine extérieur est celui du Swagger; il n’est pas remplacé par le domaine interne de l’adresse. Pour l’adresse structurée, `address__type_code=1`; pour le texte libre, `address__type_code=2` et `address__unstructured` est requis. Les champs de l’autre variante ne sont pas émis.

Un compte est une photographie rattachée à une action. `STR_STARTING_ACTION_ACCOUNT` et `STR_COMPLETING_ACTION_ACCOUNT` évitent une clé polymorphe et rendent explicite la provenance. L’état du compte au moment de l’opération reste au niveau de l’action, comme dans le Swagger. Les titulaires sont des références aux définitions de types 1 ou 2.

## 7. Propriété effective

Les sept listes de la variante 6 restent distinctes : administrateurs, détenteurs d’actions, fiduciaires, constituants, détenteurs d’unités de fiducie, bénéficiaires de fiducie et propriétaires d’une autre forme d’entité.

Le Swagger ne fournit pas les mêmes attributs partout. Certaines listes n’ont que les noms; d’autres utilisent `personContact` avec adresse et téléphone. Le modèle ne rajoute ni pourcentage de propriété ni référence de définition dans ces listes. Le bénéficiaire de fiducie et le bénéficiaire d’une action finale sont deux concepts distincts.

## 8. Types et présence

Les montants et taux sont des chaînes dans le contrat, avec une expression régulière autorisant de 1 à 17 chiffres entiers et, lorsqu’une partie décimale existe, de 2 à 10 décimales. La forme textuelle est conservée pour produire le JSON sans arrondi. Une projection numérique pour des analyses pourra être ajoutée séparément.

Les dates, heures avec décalage et horodatages API conservent également leur forme contractuelle. Le modèle ne transforme pas une heure locale en UTC en supprimant le décalage original.

Les colonnes techniques `*_present` distinguent un objet ou une liste facultative absent d’un objet ou d’une liste présent mais vide. Elles ne sont jamais émises dans le JSON. Une propriété scalaire absente correspond à une valeur interne non renseignée; elle est omise à la sérialisation. `false`, `0` et une chaîne vide permise ne doivent pas être confondus avec l’absence.

## 9. Dimensionnement du modèle

Les 61 tables comprennent les données déclaratives et les données de fonctionnement. Le découpage privilégie des liens explicites : identifications propres à chaque sous-type, comptes propres à chaque famille d’actions et listes de monnaies virtuelles séparées. Le nombre de tables est supérieur à celui du projet précédent, mais les propriétaires sont vérifiables et les variantes restent lisibles.

Les objets scalaires non répétitifs sont intégrés dans les tables pour contenir ce nombre. Le dictionnaire justifie chaque colonne; les choix techniques sont identifiés afin de ne pas les présenter comme des exigences CANAFE.
