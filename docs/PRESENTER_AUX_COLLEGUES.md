# Présenter le modèle en une dizaine de minutes

Ces notes accompagnent les neuf pages du fichier principal. Elles donnent une trame à adapter à votre vocabulaire; il n’est pas nécessaire de lire toutes les colonnes à l’écran.

## Page 1 — retrouver ce qui a déjà été présenté · 1 minute

« On reprend les neuf domaines du modèle précédent et les mêmes 34 tables. Je vais suivre le parcours d’une déclaration : son contexte, les personnes, les opérations, puis l’envoi. Les noms techniques restent visibles pour que chacun puisse faire le lien avec le modèle déjà présenté. »

Montrer les trois repères : Rapport, Transactions et Audit. Expliquer que les autres domaines apportent les renseignements nécessaires autour de ce parcours.

## Page 2 — le rapport · 1 minute

« Le rapport contient le récit et les références du dossier. On peut le relier à des projets ou à d’autres déclarations. Une correction conserve la version précédente : on pourra toujours retrouver ce qui avait été déclaré à une date donnée. »

Si la question des clés arrive, montrer seulement `str_report_id` et `report_group_id` : le premier identifie une version, le second rassemble ses versions successives.

## Page 3 — les fiches et l’identité · 1 minute 30

« Une personne ou une entreprise possède une fiche dans le rapport. Les rôles vont citer cette fiche. On évite ainsi de recopier ses renseignements à chaque opération. Les adresses et les pièces d’identité sont rangées à part, car elles ont leur propre structure. »

Ajouter la nuance si nécessaire : une même personne réelle peut avoir plusieurs fiches déclaratives lorsque les rôles demandent des niveaux de détail différents. Ce modèle n’est pas un outil de rapprochement de tous les clients de l’organisation.

## Page 4 — les renseignements sur l’entité · 45 secondes

« Pour une entreprise, on décrit son enregistrement et les personnes autorisées à agir. Une autorisation n’est pas une preuve de propriété. C’est pour cela que ces renseignements ne sont pas mélangés avec les propriétaires et les dirigeants. »

## Page 5 — la direction et la propriété · 45 secondes

« Les sept listes reprennent les catégories du Swagger. Elles distinguent les administrateurs, les détenteurs d’actions et les différents intervenants d’une fiducie. Toutes sont rattachées à l’entité concernée. »

Il suffit de donner un exemple, puis de signaler que le bénéficiaire d’une fiducie n’est pas le bénéficiaire d’une opération.

## Page 6 — les opérations · 1 minute 30

« Une opération comporte un contexte et des actions. Prenons un change de devises : nous décrivons ce qui est remis au départ puis ce qui est remis à l’arrivée. Une opération peut comporter plusieurs actions initiales et finales. »

Suivre les deux flèches. `0..N` veut dire « aucun, un ou plusieurs » dans la structure du modèle. La présence des listes et les obligations de déclaration sont contrôlées au moment de préparer l’envoi.

## Page 7 — les rôles · 1 minute 30

« Camille effectue l’opération pour la société A. Camille est l’exécutante; A est le tiers représenté. Nous renseignons séparément la source des fonds et les personnes concernées par l’action finale. On ne déduit pas tous les rôles du simple fait que Camille se présente. »

Montrer le lien de l’exécutant vers le tiers représenté. Revenir brièvement à la page 3 si quelqu’un demande où se trouvent leurs noms et adresses.

## Page 8 — les comptes · 45 secondes

« Le compte décrit le support utilisé pour une action. Ses titulaires sont identifiés séparément. Pour la monnaie virtuelle, nous conservons les identifiants et les adresses utiles. Chaque renseignement reste lié à l’action à laquelle il se rapporte. »

## Page 9 — l’envoi et les retours · 1 minute

« Nous gardons le document exact transmis et les réponses reçues. Si on renvoie le même contenu après un problème technique, c’est une nouvelle tentative. Si on corrige le contenu, c’est une nouvelle version du rapport. Cette séparation nous permet d’expliquer précisément ce qui s’est passé. »

Pour terminer la discussion, demander aux collègues si les faits qu’ils manipulent au quotidien trouvent leur place dans ces domaines. Les questions sur les colonnes peuvent ensuite être traitées avec le dictionnaire.

## Réponses aux questions probables

**Pourquoi autant de tables ?** Plusieurs renseignements peuvent se répéter : opérations, titulaires, pièces, propriétaires. Une table distincte permet de conserver toutes les occurrences sans inventer des colonnes « titulaire 1 », « titulaire 2 », etc.

**Pourquoi ne pas tout mettre dans PERSON ?** Le nom d’une personne est une information sur sa fiche. Le fait qu’elle exécute une opération est une information sur cette opération. La même personne peut intervenir de façons différentes.

**Est-ce que toutes les colonnes sont obligatoires ?** Non. Cela dépend de l’objet, de la variante et du contexte. Le dictionnaire distingue les champs du Swagger et les colonnes internes. Les règles s’appliquent au rapport complet avant l’envoi.

**Est-ce le même modèle que la présentation précédente ?** Les 34 tables et les neuf domaines sont repris. Les liens sont précisés, et les versions ainsi que le suivi des envois sont explicités. Le [comparatif](COMPARAISON_PROJET_IO.md) détaille ces précisions.

**Peut-on charger ce modèle directement dans une base ?** C’est un modèle logique, indépendant du système de base de données. Il donne les colonnes, les clés et les règles à mettre en œuvre. Les scripts de création et le connecteur CANAFE ne font pas partie de ce livrable.
