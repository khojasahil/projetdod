# Utiliser le modèle dans draw.io

## Ouvrir le fichier

1. Télécharger [CANAFE_DOD.drawio](../diagrams/CANAFE_DOD.drawio) depuis le dépôt avec l’option de téléchargement du fichier brut.
2. Ouvrir [diagrams.net](https://app.diagrams.net/) ou l’application draw.io de bureau.
3. Choisir **Fichier → Ouvrir depuis → Appareil**, puis sélectionner le fichier.
4. Utiliser les onglets de pages pour passer de la vue d’ensemble aux domaines détaillés.

Le fichier est du XML draw.io non compressé, modifiable. Les tables sont de vrais objets du diagramme; les relations sont des connecteurs. Il n’est pas nécessaire de redessiner une image.

## Lire les pages

La première page présente les 61 tables regroupées par l’ordre des domaines du catalogue, avec le nombre de colonnes. Les autres pages montrent au plus quatre tables détaillées pour éviter une vue unique illisible. Les parents situés sur une autre page apparaissent en gris comme références de contexte. Les liens vers les définitions sont violets dans les pages détaillées et omis de la vue d’ensemble pour réduire l’encombrement.

Les tables détaillées présentent toutes les colonnes, les types logiques et les repères PK/FK. La flèche va du parent vers l’enfant. Une relation peut être composite même si elle porte un seul trait : consulter sa légende et [relationships.csv](../traceability/relationships.csv).

La mention `1 → 0..N` permet les brouillons incomplets. Les minimums avant gel et les choix exclusifs sont explicités dans [REGLES.md](REGLES.md). Le diagramme ne prétend pas encoder à lui seul toutes les règles conditionnelles.

## Recréer ou modifier

Pour recréer manuellement une table, reprendre son bloc dans le [dictionnaire](DICTIONNAIRE.md), puis ses liens dans le fichier des relations. Reproduire les identifiants tels quels; le double soulignement dans une colonne marque un objet JSON imbriqué.

Pour une modification durable, adapter les décisions de génération dans `tools/generate.py`, régénérer avec `python tools/generate.py`, puis exécuter `python tools/verify.py`. Le dictionnaire, le modèle structuré, la traçabilité et le diagramme restent ainsi cohérents. Une modification manuelle du `.drawio` seule est possible pour la présentation, mais sera écrasée par une régénération.

## Suivre un champ jusqu’à la source

Exemple : `STR_STARTING_ACTION.details__amount`.

1. Rechercher cette colonne dans le dictionnaire ou `fields.csv`.
2. Lire le chemin `$.transactions[].startingActions[].details.amount`.
3. Lire le JSON Pointer de la propriété dans `STRReport`.
4. Suivre son `$ref` vers `#/components/schemas/currencyAmount`.
5. Vérifier le type `string` et son `pattern` dans le YAML archivé, à la ligne indiquée.

`fields.csv` distingue le site d’utilisation (`source_pointer`) et la définition réutilisée (`resolved_pointer`). Les variantes sont indiquées séparément. Une même colonne peut avoir plusieurs lignes de correspondance pour les deux variantes d’adresse; ce n’est pas un champ oublié.

Les identifiants et horodatages internes sont justifiés dans le dictionnaire, avec l’origine `TECHNIQUE`. Ils n’ont pas de faux chemin Swagger. Les indicateurs de présence disposent d’un chemin de structure, mais ne sont pas des propriétés à transmettre.
