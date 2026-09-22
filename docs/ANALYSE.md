# Choix de conception

Le modèle reprend les 34 tables de [projet-io](https://github.com/khojasahil/projet-io), réparties dans les neuf domaines déjà présentés. Les renseignements du Swagger sont répartis dans ces tables. Les schémas JSON réutilisables ne deviennent pas automatiquement autant de tables.

## Une ligne de rapport représente une version

`STR_REPORT.str_report_id` identifie une version. `report_group_id` regroupe les versions d’une déclaration. Le couple `(report_group_id, version_number)` est unique. `previous_report_id` relie une correction à sa version précédente dans le même groupe. La première version n’a pas de prédécesseur.

Chaque ligne enfant possède `str_report_id`. Les liens sont contrôlés dans cette même version. Le contenu gelé reste immuable; une correction copie le contenu dans une nouvelle version avec de nouvelles clés internes. Les métadonnées de cycle de vie et le journal suivent les décisions sans réécrire le contenu transmis.

Cette solution garde une seule table REPORT. Elle demande un contrôle explicite de la chaîne : pas de cycle, de branche ou de changement de groupe. Le dernier numéro de version ne prouve pas que cette version a été acceptée : l’état de transmission provient du domaine Audit.

## Une PERSON et une ENTITY, selon le type de définition

`STR_DEFINITION` porte `ref_id` et `type_code`. Les types 1, 3 et 5 ont exactement une ligne PERSON; les types 2, 4 et 6 ont exactement une ligne ENTITY. Les colonnes partagées se trouvent dans la même table; la variante détermine les champs applicables.

L’unicité de `definition_id` dans chaque table et le contrôle du code empêchent de créer simultanément une personne et une entité pour la même définition. EMPLOYER_INFO ne s’applique qu’au type 5. Les sept listes de direction et de propriété ne s’appliquent qu’au type 6.

Les références des rôles utilisent `(str_report_id, type_code, ref_id)`. Les types permis varient selon le rôle. Une fiche n’est pas automatiquement une identité client globale : la même personne réelle peut avoir plusieurs définitions déclaratives.

## Adresses, comptes et listes

Chaque propriétaire d’adresse possède une clé `address_id` facultative. L’adresse appartient à une seule ligne propriétaire et à la même version. Ce choix évite une clé polymorphe qui pourrait pointer indifféremment vers plusieurs tables. L’unicité du propriétaire, toutes tables confondues, reste un contrôle applicatif à implanter.

ACCOUNT et VC_DATA possèdent deux clés d’action : exactement une doit être renseignée. ACCOUNT est unique pour chaque action. Dans VC_DATA, `data_type` distingue les trois listes, et `ordinal` préserve la position dans chacune d’elles.

Toutes les listes conservent leur ordre avec un rang. Deux valeurs identiques peuvent être présentes si le Swagger ne l’interdit pas. Les numéros de comptes, de pièces et les montants restent du texte pour respecter le format source.

## Quatre tables pour les transmissions

API_SUBMISSION représente un appel : soumission, correction, suppression ou consultation. SUBMITTED_PAYLOAD conserve le corps exact envoyé. La réponse exacte est archivée dans `API_SUBMISSION.api_response_body`. VALIDATION_ERROR projette les erreurs et avertissements utiles à l’utilisateur. AUDIT_EVENT documente les actions internes.

Il n’y a pas de table par forme de réponse API. Les champs de réponse non projetés restent accessibles par leur chemin dans l’archive, avec une traçabilité explicite « JSON archivé ». C’est le compromis qui permet de conserver les quatre tables d’Audit. Une réponse de lot sans message, un accusé non rapproché ou un champ inattendu ne sont pas perdus.

Les traitements de lot sont documentés pour le suivi, mais le modèle n’invente pas une enveloppe d’entrée que le Swagger ne décrit pas complètement. Voir [ALIMENTATION.md](ALIMENTATION.md).

## Ce qui est livré

Les neuf vues métier montrent les colonnes nécessaires à l’explication. L’annexe draw.io contient toutes les colonnes, et le registre des relations permet de tracer les liens complets. Le dictionnaire explique chaque colonne; les fichiers de traçabilité conservent les contraintes exactes du Swagger.

Il s’agit d’un modèle logique : les types physiques, index, contraintes de base et règles de conservation opérationnelles seront choisis lors de l’implantation. Aucun script SQL ni connecteur d’envoi n’est fourni.
