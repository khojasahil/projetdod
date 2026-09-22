# Comparaison avec projet-io

Référence examinée : [projet-io au commit 3af25c3](https://github.com/khojasahil/projet-io/tree/3af25c38efdd78e7d56edcdaf32f89f3ace38515), notamment le README, le modèle V2 et le document complet V2. La copie YAML y est identique à la copie officielle récupérée le 22 septembre 2026.

Le nouveau travail reprend la séparation fonctionnelle rapport / définitions / opérations / rôles / comptes / audit. Les changements ci-dessous répondent au besoin d’historique et rendent la traçabilité vérifiable.

| Sujet | Constat dans le projet précédent | Décision dans projetdod |
|---|---|---|
| Historique | Rapport principal et tables d’audit; la photographie versionnée n’est pas l’agrégat central du modèle présenté. | Identité durable, versions explicites et envois distincts. Les références portent la version. |
| Définitions | Tables personne et entité partagées entre plusieurs types. | Six sous-types correspondant exactement aux six branches `oneOf`, avec clé partagée. |
| Propriétaires d’adresses et identifications | `owner_type` et `owner_id` sont décrits comme FK polymorphe. | Adresses intégrées au propriétaire; identifications par sous-type avec parent explicite. |
| Comptes des actions | Compte partagé entre plusieurs catégories de parent. | Deux tables de comptes, avec leurs titulaires, pour des liens relationnels explicites. |
| Monnaie virtuelle | Table générique `VC_DATA`. | Trois listes distinctes par famille d’action : transactions, adresses émettrices et réceptrices. |
| Ordre et présence | Le rôle de l’ordre et la distinction absence / vide ne sont pas systématisés dans le modèle synthétique. | `ordinal` pour les listes; présence explicite pour les objets et listes facultatifs. |
| Traçabilité | Chemins YAML fournis dans les tableaux. | Chemin JSON, JSON Pointer d’usage, cible résolue, ligne, contraintes, branche de variante et fichier source figé. |
| `additionalProperties` | Présenté comme interdit partout dans le README. | Interdit uniquement où le mot-clé vaut `false`; les absences du mot-clé sont conservées. |
| Secteurs d’activité | Le texte annonce 28 valeurs. | Le domaine contient 25 valeurs; 28 est une valeur maximale, pas un décompte. |
| Soumissions | Journal de soumission et archive. | Enveloppe, éléments, appels, réponses successives et rapprochement des accusés; compatible avec suivi individuel et lots. |
| Validation | Description des couches de validation. | Contrôles de couverture reproductibles et anomalies du Swagger explicitement documentées. |

Le nombre de tables passe du modèle annoncé de 34 tables à 61 tables logiques, en incluant l’historique, les référentiels et les projections des réponses. Ce n’est pas une extension aux autres types de déclarations. Aucun script SQL n’est fourni, conformément au périmètre demandé.

Les détails d’implantation pourront regrouper certaines tables au prix de contraintes conditionnelles supplémentaires. Le modèle livré privilégie la lisibilité des propriétaires et l’intégrité de leurs références.
