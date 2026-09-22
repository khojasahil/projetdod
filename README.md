# CANAFE — Modèle de données DOD / STR

Ce projet reprend **les 34 tables et les neuf domaines de projet-io**. Il sert à comprendre le modèle, à le reproduire dans draw.io et à l’expliquer à des collègues. Le périmètre reste celui des déclarations d’opérations douteuses, avec l’historique des versions et le suivi des envois.

Le fil conducteur est simple : **on décrit un rapport, les personnes concernées et les opérations, puis on conserve la trace de ce qui a été transmis.**

## Commencer ici

1. Parcourir les images ci-dessous pour retrouver l’architecture déjà présentée.
2. Lire le [guide métier](docs/GUIDE_METIER.md) : une question, une explication et un exemple par domaine.
3. Utiliser les [notes de présentation](docs/PRESENTER_AUX_COLLEGUES.md) pour préparer une réunion d’une dizaine de minutes.
4. Ouvrir le [modèle métier dans draw.io](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD.drawio), puis enregistrer une copie pour le modifier.

## Une architecture qui reste familière

![Les neuf domaines et leurs 34 tables](diagrams/images/01-domaines.png)

| Domaine | Tables | Question à laquelle il répond |
|---|---:|---|
| 🔵 Rapport | 4 | Quel dossier transmet-on ? |
| 🟢 Définitions | 4 | De qui parle-t-on ? |
| 🟡 Identité | 2 | Comment décrire et identifier ces personnes ou entités ? |
| 🟢 Entité | 2 | Comment l’organisation est-elle constituée ? |
| 🔴 Bénéficiaires effectifs | 7 | Qui dirige ou détient l’entité ? |
| 🟠 Transactions | 3 | Que s’est-il passé ? |
| 🟣 Rôles | 5 | Qui fait quoi dans l’opération ? |
| 💚 Comptes | 3 | Par quels comptes ou adresses les fonds passent-ils ? |
| ⬜ Audit | 4 | Qu’a-t-on envoyé et quelle réponse a-t-on reçue ? |
| **Total** | **34** | |

Tous les noms de tables commencent par `STR_`. Ce préfixe signifie *Suspicious Transaction Report*, l’équivalent anglais de DOD. Les couleurs servent à retrouver les domaines; elles ne portent aucune règle de validation.

## Comprendre une opération

Une opération peut comporter plusieurs actions initiales et plusieurs actions finales. Par exemple, dans une opération de change, on décrit les fonds remis au départ puis la devise remise à l’arrivée.

![L’opération, ses actions initiales et ses actions finales](diagrams/images/06-transactions.png)

Les rôles répondent ensuite à une autre question : qui intervient dans ce mouvement ? La fiche d’une personne et son rôle dans une opération sont deux informations distinctes.

![Les cinq rôles et leur rattachement](diagrams/images/07-roles.png)

## Garder l’historique sans ajouter un domaine

Une ligne de `STR_REPORT` représente **une version du rapport**. Une correction crée une nouvelle ligne, reliée à la précédente. Un nouvel essai d’envoi du même contenu crée seulement une nouvelle ligne de suivi dans `STR_API_SUBMISSION`.

![Les quatre tables du domaine Audit](diagrams/images/09-audit.png)

## Les vues à utiliser en réunion

Le fichier principal contient dix pages : neuf vues métier et une grande page du modèle complet. Les domaines Définitions et Identité sont réunis sur une même vue métier pour montrer leurs liens.

| Page | Image à ouvrir ou à insérer dans une présentation |
|---|---|
| 1 | [Vue des neuf domaines](diagrams/images/01-domaines.png) |
| 2 | [Rapport et références liées](diagrams/images/02-rapport.png) |
| 3 | [Définitions et identité](diagrams/images/03-personnes-identite.png) |
| 4 | [Entité : enregistrement et personnes autorisées](diagrams/images/04-entite.png) |
| 5 | [Direction et propriété de l’entité](diagrams/images/05-propriete.png) |
| 6 | [Transactions](diagrams/images/06-transactions.png) |
| 7 | [Rôles](diagrams/images/07-roles.png) |
| 8 | [Comptes et monnaie virtuelle](diagrams/images/08-comptes.png) |
| 9 | [Audit et suivi des envois](diagrams/images/09-audit.png) |
| 10 | [Modèle complet : les neuf domaines, les 34 tables et leurs 365 colonnes](diagrams/images/10-modele-complet.png) |

Les images et les pages draw.io partagent la même composition. Les cartes montrent une sélection de colonnes pour faciliter la lecture. `0..N` signifie « aucun, un ou plusieurs ». Les clés, les obligations et les liens non affichés sont détaillés dans la documentation de construction.

### Voir tout le modèle sur une seule page

L’onglet **« Le modèle complet — domaines, tables et colonnes »** réunit les 34 tables, leurs 365 colonnes, les types logiques et les repères PK/FK. Les 77 références sont indiquées au bas des cartes, y compris les liens entre domaines. Des notes expliquent les points à retenir : la personne et son rôle, les versions et les tentatives d’envoi, ou encore le rattachement d’un compte à une action.

[Ouvrir directement la page complète dans draw.io](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD.drawio#%7B%22pageId%22%3A%22page9%22%7D) · [Image PNG](diagrams/images/10-modele-complet.png) · [Image vectorielle SVG](diagrams/images/10-modele-complet.svg)

Cette planche est faite pour être parcourue en zoomant. Les vues métier précédentes restent les plus adaptées à une présentation projetée.

## Reproduire le modèle

- **[Version facile à modifier — CANAFE_DOD_EDITION_SIMPLE.drawio](diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio)** : les mêmes dix pages, avec une seule forme et un texte multiligne par table. Un champ par ligne; les notes sont aussi des blocs uniques. [Mode d’emploi](docs/EDITION_SIMPLE.md).
- [Guide draw.io](docs/GUIDE_DRAWIO.md) : ouvrir, modifier ou redessiner les vues.
- [Fichier principal — neuf vues métier et une vue complète](diagrams/CANAFE_DOD.drawio).
- [Annexe draw.io — les 34 tables avec toutes leurs colonnes](diagrams/CANAFE_DOD_DETAIL.drawio).
- [Dictionnaire](docs/DICTIONNAIRE.md) : les 365 colonnes, leur utilité, leurs règles et leurs références Swagger.
- [Registre des relations](docs/RELATIONS.md) : les liens et leurs cardinalités, pour tracer les connecteurs.
- [Continuité avec projet-io](docs/COMPARAISON_PROJET_IO.md) : ce qui est conservé et ce qui est précisé.

## Pour l’équipe qui alimentera les données

[Choix de conception](docs/ANALYSE.md) · [Alimentation et versions](docs/ALIMENTATION.md) · [Règles et points à confirmer](docs/REGLES.md) · [Domaines de codes](docs/DOMAINES_CODES.md)

La traçabilité couvre **486 occurrences de champs nommés**, dont **437 dans le rapport STR**, variantes comprises. Ce nombre décrit les chemins du Swagger, pas le nombre de colonnes. Les champs communs à plusieurs variantes partagent une colonne; les réponses API sont aussi conservées intégralement.

- [Correspondance champ → colonne → Swagger](traceability/fields.csv)
- [Objets, listes et obligations de présence](traceability/structures.csv)
- [Résultats et limites des contrôles](quality/CONTROLES.md)

Source : [Swagger CANAFE](https://www148.fintrac-canafe.canada.ca/swagger), copie du **22 septembre 2026**, version déclarée `1.0.0`. Le [YAML original](source/swaggerExternal.yaml) et sa [provenance](source/provenance.json) sont conservés. Quelques ambiguïtés du contrat sont documentées; les contrôles locaux ne constituent pas une homologation CANAFE. Aucun rapport réel n’a été transmis.

Ce dépôt contient un modèle logique et sa documentation, **sans script de création de tables**.

<details>
<summary>Regénérer les livrables et vérifier leur cohérence</summary>

Python 3.10 ou plus récent et Pillow sont nécessaires. Depuis la racine du dépôt :

```text
python tools/generate.py
python tools/verify.py
python tools/simple_editing.py
```

Les fichiers de référence sont le Swagger archivé, le catalogue `tools/build_model.py` et les compositions `tools/render_models.py`. La régénération ne modifie pas les guides rédigés ni le YAML officiel. Les polices Arial sont utilisées sous Windows; DejaVu Sans sert de repli sous Linux.

</details>
