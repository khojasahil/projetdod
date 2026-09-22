# Vérifications de livraison

Date : 22 septembre 2026.

## Contrôles automatisés

Le [résultat détaillé](verification.json) est généré par `tools/verify.py`, indépendamment du parcours de génération des tables.

- 34 tables, 365 colonnes et neuf domaines, avec les effectifs 4 / 4 / 2 / 2 / 7 / 3 / 5 / 3 / 4 demandés.
- Neuf pages métier et une annexe de 34 pages, une par table avec toutes ses colonnes.
- 486 occurrences scalaires documentées, variantes distinguées, sur les schémas retenus; toutes ont une correspondance. Parmi elles, 437 appartiennent au graphe de `STRReport`. Ces nombres comptent les usages et branches, pas seulement les noms de propriétés uniques.
- 486 lignes de correspondance. Les colonnes internes, dont les indicateurs de présence, sont expliquées séparément dans le dictionnaire.
- Toutes les cibles de relations existent. Les propriétés partagées et les regroupements volontaires, notamment les listes de monnaie virtuelle et les messages, sont contrôlés et documentés.
- Toutes les tables contenant les données DOD sont rattachées à une version.
- Empreinte du YAML officiel vérifiée.
- XML draw.io, identifiants de formes, références des connecteurs et limites des pages vérifiés dans les deux fichiers. Les neuf images PNG ont les dimensions attendues; les textes des cartes restent dans leur cadre.
- Les liens relatifs du README et des guides pointent vers des fichiers présents.
- Exemples DOD v1 et v2, réponse individuelle et demande de suppression contrôlés localement.
- Neuf scénarios invalides détectés : montant mal formé, données requises absentes, liste d’opérations vide, références inconnues ou incompatibles, `refId` dupliqué, adresse libre incomplète et champ supplémentaire interdit.
- Ambiguïtés `oneOf` des messages de validation et du code de province reproduites; elles restent documentées comme anomalies du contrat.

## Relecture des supports

Les neuf images métier ont été inspectées visuellement. Les légendes de relations des pages Rapport, Rôles et Audit ont été ajustées pour rester visibles entre les cartes. Les images et les pages draw.io sont produites à partir de la même composition.

La vérification structurelle couvre les 43 pages des deux fichiers. La présentation utilise des pages de travail sans découpage papier. Une impression A4 nécessitera une mise en page adaptée; les PNG sont destinés à une consultation à l’écran et à l’insertion dans des présentations.

## Portée de ces contrôles

Le validateur local couvre les mots-clés utilisés par les exemples; il n’est pas un moteur OpenAPI général ni un test de certification CANAFE. Aucun appel de soumission n’a été réalisé. L’intégrité est spécifiée dans le modèle logique et devra être implantée puis testée dans le SGBD choisi.
