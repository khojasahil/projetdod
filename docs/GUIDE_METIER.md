# Comprendre le modèle sans commencer par les colonnes

Une DOD raconte un ensemble de faits : ce qui a été observé, qui était concerné, quelles opérations ont eu lieu et pourquoi ces faits ont éveillé un soupçon. Le modèle range ces renseignements pour pouvoir les retrouver et constituer le document destiné à CANAFE.

Il conserve les neuf domaines du projet précédent. Une **table** est une liste de renseignements de même nature. Une **ligne** est un élément de cette liste. Une **clé** est un repère qui permet de relier deux lignes sans recopier leur contenu.

L’exemple qui suit est entièrement fictif : Camille effectue une opération pour la société A. Nous nous en servons pour expliquer les liens, sans en déduire qu’une telle opération est suspecte.

## 1. Rapport — quel dossier transmet-on ?

`STR_REPORT` est le point d’entrée. Il contient la référence du rapport, l’entité déclarante, le récit du soupçon et les mesures prises. On peut lui associer des projets de partenariat public-privé dans `STR_PPP_PROJECT`.

Si un autre rapport aide à comprendre le dossier, `STR_RELATED_REPORT` en conserve la référence. `STR_RELATED_REPORT_TXN_REF` précise les opérations à regarder dans cet autre rapport. On conserve des références; on ne recopie pas ce rapport.

**À retenir pour la présentation :** « Cette première partie explique de quel dossier on parle et donne le contexte. »

## 2. Définitions — de qui parle-t-on ?

`STR_DEFINITION` attribue un repère à une fiche. `STR_PERSON` porte les renseignements sur une personne physique. `STR_ENTITY` porte ceux d’une entreprise, d’une organisation ou d’une fiducie. `STR_EMPLOYER_INFO` complète certaines fiches de personne avec les renseignements sur leur employeur.

Le rôle de Camille dans une opération cite son repère. C’est ce qui permet de retrouver sa fiche sans répéter son adresse et ses autres renseignements dans chaque rôle.

Le Swagger distingue six niveaux ou formes de définition. Nous gardons une table PERSON et une table ENTITY, comme dans l’ancien modèle. Le code de définition indique quelles colonnes sont applicables.

| Code | Fiche décrite | Usage dans le rapport |
|---:|---|---|
| 1 | Nom de personne | Source des fonds, personne impliquée, titulaire |
| 2 | Nom d’entité | Source des fonds, entité impliquée, titulaire |
| 3 | Personne avec renseignements détaillés | Bénéficiaire d’une action finale |
| 4 | Entité avec renseignements détaillés | Bénéficiaire d’une action finale |
| 5 | Personne avec possibilité de renseignements sur l’employeur | Exécutant ou tiers représenté |
| 6 | Entité avec renseignements sur la propriété et la direction | Exécutant ou tiers représenté |

Une même personne réelle peut donc avoir plusieurs définitions si les rôles exigent des codes différents. Le modèle décrit les fiches d’un rapport; il ne remplace pas un référentiel client unique de l’organisation.

## 3. Identité — comment la décrire et l’identifier ?

`STR_ADDRESS` conserve une adresse. Une fiche de personne, d’entité ou d’employeur, par exemple, pointe vers son adresse. Certaines listes de dirigeants ou de propriétaires disposent aussi d’une adresse selon le Swagger.

`STR_IDENTIFICATION` conserve une pièce ou un renseignement d’identification : son type, son numéro et son lieu de délivrance lorsque ces renseignements sont prévus.

**Exemple :** le nom de Camille est dans PERSON; son adresse est dans ADDRESS; les renseignements de sa pièce d’identité sont dans IDENTIFICATION. Ces trois informations ont des usages différents, même si elles décrivent la même personne.

## 4. Entité — comment l’organisation est-elle constituée ?

`STR_REGISTRATION_INCORPORATION` contient les renseignements d’enregistrement ou de constitution. `STR_AUTHORIZED_PERSON` contient les noms des personnes autorisées à agir pour l’entité.

Une personne autorisée à agir pour la société A n’en est pas nécessairement propriétaire. Cette distinction explique pourquoi ces renseignements restent séparés du domaine suivant.

## 5. Bénéficiaires effectifs — qui dirige ou détient l’entité ?

Les sept tables reprennent les sept listes prévues dans la définition d’entité de type 6.

| Table, sans le préfixe STR_ | Ce qu’elle décrit |
|---|---|
| DIRECTOR | Administrateurs de la société |
| SHARE_OWNER | Personnes détenant des actions |
| TRUSTEE | Fiduciaires |
| SETTLOR | Constituants de la fiducie |
| TRUST_UNIT_OWNER | Personnes détenant des unités de fiducie |
| TRUST_BENEFICIARY | Bénéficiaires de la fiducie |
| OTHER_ENTITY_OWNER | Propriétaires d’une entité autre qu’une société ou une fiducie |

Chaque ligne est rattachée à l’entité concernée. Dans ces listes, le Swagger transmet directement des noms et, selon la liste, d’autres renseignements. Il ne s’agit pas de références vers les fiches DEFINITION.

Le nom historique du domaine est conservé. Il regroupe également des renseignements de direction et de fiducie : il ne signifie pas que chaque personne listée a exactement le même statut juridique.

**Attention au vocabulaire :** le bénéficiaire d’une fiducie et le bénéficiaire d’une opération sont deux notions distinctes.

## 6. Transactions — que s’est-il passé ?

`STR_TRANSACTION` décrit l’opération : date, lieu de déclaration, référence et circonstances connues. Une opération tentée a sa place dans cette table; un indicateur permet de la distinguer.

`STR_STARTING_ACTION` décrit les actions initiales. `STR_COMPLETING_ACTION` décrit les actions finales. Dans une opération de change, on peut ainsi décrire les fonds remis puis la devise obtenue. Il peut y avoir plusieurs actions de chaque côté; le modèle ne suppose pas une correspondance une pour une.

**À dire :** « L’opération donne le contexte du mouvement. Les actions nous disent ce qui est entré et ce qui en est ressorti, selon les faits à déclarer. »

## 7. Rôles — qui fait quoi dans cette opération ?

| Table | Question simple | Rattachement |
|---|---|---|
| STR_SOURCE_OF_FUNDS | Qui est désigné comme source des fonds ? | Action initiale |
| STR_CONDUCTOR | Qui effectue l’action ? | Action initiale |
| STR_ON_BEHALF_OF | Pour le compte de qui cet exécutant agit-il ? | Exécutant |
| STR_INVOLVEMENT | Qui est impliqué dans l’action finale ? | Action finale |
| STR_BENEFICIARY | Qui bénéficie de l’action finale ? | Action finale |

Camille effectue l’opération pour la société A : Camille est l’exécutante et A est le tiers représenté. Cela ne permet pas de conclure automatiquement que A est aussi la source des fonds, ni que Camille est titulaire du compte. Ces renseignements se documentent séparément.

Le rôle contient une référence à la fiche et les renseignements propres à cette participation. La fiche répond à « qui est-ce ? », le rôle à « que fait cette personne ici ? ».

## 8. Comptes — par où passent les fonds ?

`STR_ACCOUNT` décrit le compte pour une action précise. `STR_ACCOUNT_HOLDER` désigne ses titulaires. Un même compte réel peut apparaître dans plusieurs actions : chaque occurrence restitue ce qui a été déclaré pour cette action.

`STR_VC_DATA` conserve les identifiants de transactions en monnaie virtuelle ainsi que les adresses émettrices et réceptrices. Le champ `data_type` distingue ces trois listes.

Un compte ou une donnée de monnaie virtuelle appartient à une action initiale **ou** à une action finale. Les deux rattachements ne sont pas renseignés en même temps.

## 9. Audit — qu’a-t-on envoyé et quelle réponse a-t-on reçue ?

`STR_API_SUBMISSION` suit chaque tentative et chaque consultation de résultats. `STR_SUBMITTED_PAYLOAD` garde le document exact transmis. `STR_VALIDATION_ERROR` rend les messages de validation consultables. Malgré son nom historique, cette table conserve aussi les avertissements. `STR_AUDIT_EVENT` consigne les actions et décisions internes.

Une réponse technique positive ne suffit pas à conclure que le rapport est accepté. Il faut lire le résultat de traitement correspondant au rapport. Les réponses complètes sont conservées pour pouvoir revenir à ce que CANAFE a réellement renvoyé.

## Une correction et un nouvel essai ne sont pas la même chose

| Situation | Ce que l’on crée |
|---|---|
| Le rapport est encore en préparation | On complète le brouillon existant. |
| Le contenu gelé doit être corrigé | Une nouvelle ligne STR_REPORT et de nouvelles lignes enfants pour cette version. |
| L’envoi échoue techniquement, le contenu est inchangé | Une nouvelle tentative STR_API_SUBMISSION après rapprochement du résultat éventuel. |
| On consulte une nouvelle fois les résultats | Une nouvelle ligne de suivi, avec la nouvelle réponse. |

Les versions d’un même rapport partagent `report_group_id`. Chacune possède son propre `str_report_id`. Cela permet de consulter le contenu d’hier sans le remplacer par celui d’aujourd’hui.

Pour la réunion, utiliser les [notes de présentation](PRESENTER_AUX_COLLEGUES.md). Pour construire les tables, passer au [dictionnaire](DICTIONNAIRE.md).
