# Une version plus naturelle à modifier

[Ouvrir CANAFE_DOD_EDITION_SIMPLE.drawio](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD_EDITION_SIMPLE.drawio)

Ce second fichier contient treize pages : les dix pages du modèle, la page relationnelle initiale et deux nouvelles vues plus aérées. Les couleurs des domaines, les notes et les connecteurs sont conservés. Le fichier original **CANAFE_DOD.drawio est conservé sans modification**.

## Ce qui change pour vous

Une table est une seule forme. Son titre, son nom et ses colonnes se trouvent dans le même texte, avec un champ par ligne. Il n’y a plus de petits objets à sélectionner et aligner pour chaque colonne. Chaque note est également un rectangle contenant son titre et son explication.

Les contours colorés reprennent la couleur du domaine. Les tables conservent leur position et leurs dimensions. Les connecteurs restent attachés aux tables.

## Modifier une table

1. Enregistrer une copie du fichier.
2. Double-cliquer dans la table pour modifier son texte.
3. Placer le curseur à la fin d’un champ et appuyer sur Entrée pour ajouter une ligne.
4. Saisir le nouveau champ, ou modifier et supprimer une ligne existante comme dans un texte normal.
5. Cliquer en dehors de la table pour terminer. Agrandir le rectangle si le texte ajouté a besoin de place.

Pour déplacer la table, cliquer une fois sur son contour et la faire glisser. Son contenu suit, ainsi que les connecteurs. Pour modifier une note, double-cliquer dans son rectangle.

Le dixième onglet conserve les **34 tables, les 365 colonnes et les 77 références** sur une même page. Zoomer sur le domaine à modifier.

## Page 11 — les relations entre toutes les tables

[Ouvrir directement la page relationnelle](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD_EDITION_SIMPLE.drawio#%7B%22pageId%22%3A%22page10%22%7D)

L’onglet **« Relations complètes — PK, FK et cardinalités »** montre les 34 tables et leurs 365 colonnes avec les **77 connecteurs réels**, y compris les liens entre domaines. Les repères PK et FK identifient les clés. Chaque trait part de la clé du parent et arrive sur la clé étrangère correspondante de l’enfant.

Les symboles aux extrémités se lisent ainsi : côté parent, une ligne enfant a un parent requis (1) ou facultatif (0..1); côté enfant, un parent peut avoir zéro ou une ligne (0..1), ou plusieurs lignes (0..N). Le numéro R01 à R77 permet de retrouver la clé complète dans le [registre de cette page](RELATIONS_PAGE11.md), notamment lorsqu’elle contient plusieurs colonnes.

Les liens bleus pointillés rattachent chaque table à la version du rapport. Les autres liens reprennent la couleur du domaine parent. Tous sont visibles à l’ouverture. Le panneau des calques permet de masquer temporairement « Liens vers la version du rapport » si vous voulez suivre plus facilement les relations métier. Les tables restent des blocs de texte uniques et modifiables.

Les références de rôles vers DEFINITION utilisent la clé unique composite `(str_report_id, type_code, ref_id)`. Le trait est attaché à une ligne de cette clé; il ne signifie pas que `type_code` est unique à lui seul. Les autres références à des sous-objets sont également contrôlées dans la même version du rapport. Les règles d’exclusivité des comptes et les obligations avant envoi restent celles du dictionnaire.

[Voir l’aperçu PNG](../diagrams/images/11-relations-completes.png). L’image montre le parcours des liens; les symboles de cardinalité ER sont affichés dans le fichier draw.io.

Les modifications faites dans votre copie draw.io ne changent pas automatiquement le dictionnaire ni le catalogue du dépôt. Si une colonne ou une relation change réellement dans le modèle, mettre aussi à jour sa documentation.

## Pages 12 et 13 — une lecture plus aérée

La [page 12 — modèle complet aéré](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD_EDITION_SIMPLE.drawio#%7B%22pageId%22%3A%22page11%22%7D) contient toutes les colonnes. La [page 13 — PK et FK seulement](https://app.diagrams.net/?splash=0#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fkhojasahil%2Fprojetdod%2Fmain%2Fdiagrams%2FCANAFE_DOD_EDITION_SIMPLE.drawio#%7B%22pageId%22%3A%22page12%22%7D) retire les attributs descriptifs pour concentrer la lecture sur les relations. La disposition et les couleurs restent les mêmes entre ces deux pages.

Pour présenter le modèle, commencez par le dossier et les envois, puis les personnes et les organisations. Terminez par une opération, ses actions, ses rôles et ses comptes. Les neuf domaines sont toujours indiqués dans les en-têtes des tables; les trois sections sont seulement un ordre de lecture.

Les **37 relations métier** sont visibles à l’ouverture. Les **34 liens vers STR_REPORT** et les **6 références des rôles et titulaires de compte vers STR_DEFINITION** sont conservés dans deux calques masqués au départ. Pour les voir, ouvrez **Vue > Calques**, puis activez l’œil du calque souhaité. Cette présentation ne change aucune relation ni règle du modèle.

Le champ `str_report_id` reste visible dans toutes les tables, même quand son connecteur est masqué. Sur la page des clés, les composants de la clé unique référencée de `STR_DEFINITION` sont aussi présents : `(str_report_id, type_code, ref_id)`. Le repère **UK*** concerne cet ensemble, jamais une colonne seule. Un trait composite est attaché à une de ses lignes; le [registre R01 à R77](RELATIONS_PAGE11.md) donne la clé complète.

Chaque table reste une seule forme éditable. Les clés sont placées en tête et portent les repères PK/FK; la page complète conserve ensuite tous les autres attributs et leurs types. Les traits évitent les tables. La vue d’ensemble sert à se repérer, puis le zoom permet de lire les champs. Les vues métier des premières pages restent utiles pour projeter un sujet à la fois.

[Aperçu complet](../diagrams/images/12-modele-aere.png) · [Aperçu PK/FK](../diagrams/images/13-relations-pk-fk.png). Ces images reproduisent l’état initial avec les 37 liens visibles. Les cardinalités y sont écrites; draw.io utilise les symboles ER aux extrémités des connecteurs.

## Vérifications

Le [rapport de contrôle](../quality/edition-simple.json) confirme la conservation des colonnes, des références et des connecteurs, ainsi que la présence d’une seule forme éditable par table. L’empreinte du fichier original est contrôlée avant et après la création de cette copie.
