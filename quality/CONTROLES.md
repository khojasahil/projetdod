# Vérifications de livraison

Date : 22 septembre 2026.

## Contrôles automatisés

Le [résultat détaillé](verification.json) est généré par `tools/verify.py`, indépendamment du parcours de génération des tables.

- 61 tables, 679 colonnes et 20 pages draw.io.
- 486 occurrences scalaires documentées, variantes distinguées, sur les schémas retenus; toutes ont une correspondance. Parmi elles, 437 appartiennent au graphe de `STRReport`. Ces nombres comptent les usages et branches, pas seulement les noms de propriétés uniques.
- 516 lignes de correspondance en incluant les indicateurs techniques de présence.
- Aucune cible de relation absente et aucune collision de propriétés JSON dans une même colonne.
- Toutes les tables contenant les données DOD sont rattachées à une version.
- Empreinte du YAML officiel vérifiée.
- XML draw.io, identifiants de formes et références des connecteurs vérifiés.
- Exemples DOD v1 et v2, réponse individuelle et demande de suppression contrôlés localement.
- Neuf scénarios invalides détectés : montant mal formé, données requises absentes, liste d’opérations vide, références inconnues ou incompatibles, `refId` dupliqué, adresse libre incomplète et champ supplémentaire interdit.
- Ambiguïtés `oneOf` des messages de validation et du code de province reproduites; elles restent documentées comme anomalies du contrat.

## Ouverture dans draw.io

Le fichier publié sur GitHub a été ouvert dans l’éditeur officiel diagrams.net au moyen de **Fichier → Ouvrir depuis → URL**. L’éditeur a reconnu les 20 pages et les noms des 61 tables. La vue d’ensemble et la page « Définitions — 3 », comprenant la table de personne/employeur la plus fournie, ont été inspectées visuellement, avec agrandissement pour la lecture des colonnes.

Le contrôle visuel est un échantillonnage; les 20 pages ont été vérifiées structurellement dans le XML. La présentation utilise des pages de travail sans découpage papier. Une impression sur A4 nécessitera une mise en page adaptée.

## Portée de ces contrôles

Le validateur local couvre les mots-clés utilisés par les exemples; il n’est pas un moteur OpenAPI général ni un test de certification CANAFE. Aucun appel de soumission n’a été réalisé. L’intégrité est spécifiée dans le modèle logique et devra être implantée puis testée dans le SGBD choisi.
