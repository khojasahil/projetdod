# Continuité avec le projet précédent

La base de comparaison est [projet-io](https://github.com/khojasahil/projet-io), au commit `3af25c38efdd78e7d56edcdaf32f89f3ace38515`. La présente architecture en reprend les **34 tables et les neuf domaines**, avec leurs noms techniques. La copie du Swagger du 22 septembre 2026 est identique, octet pour octet, à la source comparée dans ce projet.

## Ce qui reste familier

| Domaine | Tables conservées, préfixe STR_ omis |
|---|---|
| Rapport · 4 | REPORT, PPP_PROJECT, RELATED_REPORT, RELATED_REPORT_TXN_REF |
| Définitions · 4 | DEFINITION, PERSON, ENTITY, EMPLOYER_INFO |
| Identité · 2 | ADDRESS, IDENTIFICATION |
| Entité · 2 | REGISTRATION_INCORPORATION, AUTHORIZED_PERSON |
| Bénéficiaires effectifs · 7 | DIRECTOR, SHARE_OWNER, TRUSTEE, SETTLOR, TRUST_UNIT_OWNER, TRUST_BENEFICIARY, OTHER_ENTITY_OWNER |
| Transactions · 3 | TRANSACTION, STARTING_ACTION, COMPLETING_ACTION |
| Rôles · 5 | CONDUCTOR, ON_BEHALF_OF, SOURCE_OF_FUNDS, INVOLVEMENT, BENEFICIARY |
| Comptes · 3 | ACCOUNT, ACCOUNT_HOLDER, VC_DATA |
| Audit · 4 | API_SUBMISSION, SUBMITTED_PAYLOAD, VALIDATION_ERROR, AUDIT_EVENT |

Le parcours de présentation reste le même : contexte du rapport, intervenants, opérations, puis suivi. Les tables PERSON et ENTITY continuent de réunir les champs applicables à leurs différentes variantes.

## Ce qui est rendu explicite

| Précision | Pourquoi elle est utile |
|---|---|
| Une ligne REPORT par version, un groupe stable | Retrouver le contenu exact avant et après une correction. |
| `str_report_id` sur chaque enfant et contrôle des parents dans cette version | Empêcher qu’une correction utilise par erreur les données d’une autre version. |
| Référence de rôle contrôlée par code et refId | Éviter de citer une fiche qui n’a pas le niveau de détail attendu. |
| Une adresse avec un propriétaire défini | Savoir exactement à quelle fiche elle appartient. |
| Une seule clé d’action pour ACCOUNT et VC_DATA | Éviter un rattachement ambigu entre le début et la fin d’une opération. |
| Un rang pour les listes et des indicateurs de présence ciblés | Reconstruire les listes et distinguer un objet absent d’un objet vide. |
| Un suivi par appel et des archives exactes | Séparer une correction de contenu d’un nouvel essai technique. |
| Un chemin Swagger pour chaque champ nommé | Justifier les colonnes et retrouver la règle source. |

Les précisions de clés et de contraintes ne constituent pas une migration prête à exécuter d’une base existante. Le dépôt livre le modèle logique révisé et permet de comparer les choix avant implantation.

## Ce qui change dans les supports

Les cartes portent un titre français avant le nom technique. Les vues de présentation affichent les colonnes essentielles et des notes courtes. Le dictionnaire et l’annexe draw.io gardent l’ensemble des colonnes. Le README contient les images et un parcours de lecture; un guide métier et des notes de réunion accompagnent les schémas.

Pour expliquer cette reprise aux collègues : « Nous conservons la structure déjà présentée. Nous précisons les liens et l’historique, et nous avons ajouté des supports plus simples à lire. »
