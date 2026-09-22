# Utiliser et reproduire les schémas dans draw.io

## Choisir le bon fichier

| Fichier | Usage |
|---|---|
| [CANAFE_DOD.drawio](../diagrams/CANAFE_DOD.drawio) | Neuf vues métier pour expliquer le modèle. Colonnes essentielles, liens sélectionnés et notes. |
| [CANAFE_DOD_DETAIL.drawio](../diagrams/CANAFE_DOD_DETAIL.drawio) | Annexe de construction : une page par table, toutes les colonnes et leurs types logiques. |

L’annexe contient 34 pages. Elle facilite la reprise des tables; le [registre des relations](RELATIONS.md) donne les liens complets à dessiner. Les vues métier n’affichent pas tous les liens vers REPORT, ni toutes les références de rôles, afin de garder les pages lisibles.

## Ouvrir et modifier

Ouvrir [le modèle métier dans diagrams.net](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD.drawio), puis enregistrer une copie. Autre possibilité : télécharger le fichier `.drawio` depuis GitHub et l’ouvrir avec **Fichier → Ouvrir à partir de → Périphérique**. Le nom exact des menus dépend de la langue de l’application.

Les pages se trouvent dans les onglets en bas. Les cartes, textes, notes et connecteurs sont des objets modifiables, pas une image de fond. Pour déplacer une carte entière, sélectionner son rectangle et ses textes, puis les grouper. Pour modifier une note, double-cliquer son texte.

Les images [PNG et SVG](../diagrams/images) reprennent la même composition. Elles conviennent à un document ou à une présentation; utiliser le `.drawio` pour modifier les objets.

## Refaire une page soi-même

1. Choisir une seule question à expliquer, par exemple « Qui fait quoi dans une opération ? ».
2. Poser les tables du domaine et les quelques tables voisines nécessaires. Écrire un titre français lisible, puis le nom technique en dessous.
3. Ajouter d’abord la clé de la table et les clés de rattachement, puis trois à cinq colonnes utiles à l’explication. Pour une vue complète, reprendre les colonnes de l’annexe ou du dictionnaire.
4. Tracer les liens du parent vers l’enfant. Écrire leur sens en quelques mots, puis la cardinalité. Par exemple : TRANSACTION → STARTING_ACTION, « actions initiales · 0..N ».
5. Ajouter une note pour la distinction qui prête à confusion : personne et rôle, bénéficiaire de fiducie et bénéficiaire d’opération, version et tentative.
6. Aligner les cartes et réserver de l’espace aux légendes des liens. Éviter de faire passer un connecteur sur une carte.
7. Vérifier les colonnes et les relations avec le dictionnaire. Répéter pour le domaine suivant.

## Lire les clés et les cardinalités

`PK` signifie clé primaire : elle identifie une ligne. `FK` signifie clé étrangère : elle permet de retrouver une ligne liée. Dans l’annexe, ces indications apparaissent à côté des colonnes concernées. Un composant d’une référence composite peut porter FK; il faut consulter le registre pour connaître la clé complète.

`0..1` signifie « zéro ou une ligne »; `0..N`, « zéro, une ou plusieurs lignes ». Le registre se lit depuis le parent vers l’enfant. Le caractère facultatif de la clé enfant est indiqué séparément. Certains rattachements sont exclusifs : une ligne ACCOUNT a une action initiale ou finale, jamais les deux.

Les vues montrent les possibilités de stockage, y compris les brouillons. Les obligations avant envoi, par exemple au moins une transaction dans un rapport, figurent dans [REGLES.md](REGLES.md).

## Retrouver la justification d’une colonne

Rechercher le nom de la table dans [DICTIONNAIRE.md](DICTIONNAIRE.md). La colonne possède une explication et soit une origine interne, soit des références `Fxxxx`. Rechercher cette référence dans [fields.csv](../traceability/fields.csv) pour retrouver le chemin JSON, la variante, les contraintes et la ligne du YAML.

Exemple : `STR_STARTING_ACTION.amount` correspond à `$.transactions[].startingActions[].details.amount`. Les crochets signifient que le champ appartient à une liste. Sa forme de texte provient du contrat; ce n’est pas une préférence de mise en page.
