# Modèle logique CANAFE — DOD / STR

Modèle relationnel pour conserver les données d’une déclaration d’opérations douteuses, ses versions successives, les envois à CANAFE et les réponses reçues. Documentation en français; identifiants de tables et de colonnes en anglais pour faciliter le rapprochement avec l’API.

**Périmètre convenu : DOD / STR uniquement, avec historique et suivi des soumissions, sans scripts de création de tables.** La cible est indépendante du SGBD. Ce dépôt contient un modèle à implanter, pas une application de soumission.

## Commencer ici

1. [Analyse et décisions de modélisation](docs/ANALYSE.md).
2. [Diagramme draw.io modifiable — vue d’ensemble et vues détaillées](diagrams/CANAFE_DOD.drawio).
3. [Dictionnaire complet : tables, colonnes, utilité et source Swagger](docs/DICTIONNAIRE.md).
4. [Règles, cardinalités et intégrité](docs/REGLES.md).
5. [Insertion, versionnement et suivi des soumissions](docs/ALIMENTATION.md).
6. [Guide draw.io et traçabilité](docs/GUIDE_DRAWIO.md).
7. [Écarts avec le projet précédent](docs/COMPARAISON_PROJET_IO.md).

Le diagramme contient **61 tables et 679 colonnes**, réparties sur **20 pages**. Ce nombre inclut les identifiants, les liens entre tables, les colonnes de présence, les tables d’historique et les réponses API. Il ne représente pas 679 champs à fournir à CANAFE. Le [bilan des vérifications](quality/verification.json) donne les décomptes de couverture du contrat.

## Traçabilité exploitable

- [Champs et correspondances](traceability/fields.csv) : chemins JSON, table, colonne, JSON Pointer source, ligne du YAML, contraintes et variante applicable.
- [Objets, listes et présence](traceability/structures.csv) : emplacement des structures, caractère obligatoire et cardinalité minimale du Swagger.
- [Relations entre tables](traceability/relationships.csv) : parent, enfant, clés et cardinalités.
- [Domaines de codes](docs/DOMAINES_CODES.md) et [catalogue structuré](model/code-domains.json).
- [Modèle structuré complet](model/model.json), source commune du dictionnaire et du diagramme.

## Source de référence

Le [Swagger officiel](https://www148.fintrac-canafe.canada.ca/swagger) a été consulté le **22 septembre 2026**. Sa [définition YAML](https://www148.fintrac-canafe.canada.ca/reporting-ingest/api-doc-files/swaggerExternal.yaml) est archivée dans [source/swaggerExternal.yaml](source/swaggerExternal.yaml). OpenAPI : `3.0.0`; version affichée de l’API : `1.0.0`.

Empreinte SHA-256 : `78a49aa716180d4b0a3049e76af3ae3b06a188c2bafb789b11d31ddc9edf17f0`.

La source archivée dans [projet-io](https://github.com/khojasahil/projet-io/tree/3af25c38efdd78e7d56edcdaf32f89f3ace38515) est identique. Les choix de ce dépôt sont néanmoins réévalués à partir du contrat. La [provenance](source/provenance.json) permet de refaire cette comparaison.

## Vérification et limites

Les vérifications locales contrôlent la couverture des propriétés nommées, les liens du modèle, les contraintes essentielles, les exemples fictifs et la structure du fichier draw.io. Aucun envoi n’a été effectué à CANAFE. L’acceptation métier par CANAFE doit être testée dans l’environnement approprié après implantation; elle ne se déduit pas de la seule validité du JSON.

Les seuls outils fournis régénèrent ou contrôlent les livrables : `python tools/generate.py`, puis `python tools/verify.py`. Ils ne créent aucune table et ne transmettent aucune déclaration. Python 3.10 ou supérieur, bibliothèque standard seulement. Le YAML original reste la référence; `source/openapi.json` en est une représentation d’analyse, avec les exemples de dates convertis en chaînes.
