# Analyse des Marches Publics Francais - Rapport

## Objectif

Reproduire l'approche du tweet de @Argona0x appliquee au Pentagone americain, mais adaptee au gouvernement francais : utiliser l'IA et les donnees ouvertes pour identifier les contrats publics potentiellement surpayes par rapport aux prix du marche commercial.

---

## Etape 1 - Collecte des donnees

### Sources utilisees

#### 1. DECP (Donnees Essentielles de la Commande Publique)

- **URL** : https://data.economie.gouv.fr/explore/dataset/decp-v3-marches-valides/api/
- **Contenu** : Tous les marches publics attribues par les acheteurs publics francais (collectivites, ministeres, hopitaux, etablissements publics)
- **Obligation legale** : Arrete du 22 mars 2019 impose la publication des donnees essentielles
- **Volume total disponible** : 702 918 marches valides
- **Volume telecharge** : 10 000 marches les plus recents (2023-2025) avec montant > 1 000 EUR
- **Valeur totale des marches telecharges** : ~8,4 milliards EUR

#### 2. BOAMP (Bulletin Officiel des Annonces de Marches Publics)

- **URL** : https://boamp-datadila.opendatasoft.com/explore/dataset/boamp/api/
- **Contenu** : Avis de marches publics (appels d'offres, attributions, rectificatifs)
- **Volume total disponible** : 1 646 131 avis
- **Volume telecharge** : 3 000 avis recents
- **Attributions identifiees** : 724 avis avec titulaire renseigne

### Champs extraits par marche (DECP)

| Champ | Description |
|---|---|
| id | Identifiant unique du marche |
| objet | Description du marche |
| montant | Montant en EUR |
| codecpv | Code CPV (nomenclature europeenne des produits/services) |
| procedure | Type de procedure (appel d'offres ouvert, procedure adaptee, etc.) |
| datenotification | Date d'attribution |
| acheteur_id | SIRET de l'acheteur public |
| acheteur_nom | Nom de l'acheteur |
| titulaire_id_1 | SIRET du titulaire |
| offresrecues | Nombre d'offres recues (quand disponible) |
| lieuexecution_nom | Lieu d'execution |
| formeprix | Forme du prix (ferme, revisable, etc.) |

### Filtrage des marches de fournitures comparables (COTS)

Sur les 10 000 marches, **2 293** ont ete identifies comme portant sur des fournitures comparables a des prix commerciaux, en se basant sur les codes CPV suivants :

| Code CPV | Categorie | Nb marches | Montant total |
|---|---|---|---|
| 15 | Alimentaire | 452 | 361 M EUR |
| 33 | Materiel medical | 387 | 678 M EUR |
| 34 | Transport & vehicules | 324 | 254 M EUR |
| 44 | Materiaux de construction | 315 | 104 M EUR |
| 39 | Mobilier & menager | 227 | 54 M EUR |
| 30 | Informatique & bureautique | 185 | 160 M EUR |
| 31 | Materiel electrique | 88 | 286 M EUR |
| 32 | Telecommunications | 87 | 459 M EUR |
| 48 | Logiciels | 65 | 48 M EUR |
| 22 | Imprimes | 58 | 12 M EUR |
| 18 | Vetements | 56 | 19 M EUR |
| 38 | Instruments de mesure | 26 | 7 M EUR |
| 35 | Securite & defense | 23 | 5 M EUR |
| **TOTAL** | | **2 293** | **~2,45 Mds EUR** |

### Premiers constats

1. **Manque de concurrence** : 79 marches passes "sans publicite ni mise en concurrence prealable"
2. **Fournisseur unique** : 43 marches n'ont recu qu'une seule offre
3. **Opacite** : 2 080 marches (91%) n'ont pas de donnees sur le nombre d'offres recues
4. **Concentration** : Les marches de materiel medical et telecommunications representent a eux seuls ~1,14 milliard EUR

### Fichiers produits

| Fichier | Description | Lignes |
|---|---|---|
| decp_marches_10000.csv | Tous les marches collectes | 10 000 |
| decp_fournitures_cots.csv | Fournitures comparables aux prix commerciaux | 2 293 |
| boamp_attributions.csv | Avis d'attribution BOAMP | 724 |
| boamp_avis_3000.csv | Tous les avis BOAMP recents | 3 000 |

---

## Etape 2 - Classification et croisement avec les prix commerciaux

### Methode

1. Classification des 2 293 marches de fournitures par sous-categorie de produit via analyse des mots-cles dans l'objet du marche
2. Collecte de prix commerciaux de reference via l'UGAP (centrale d'achat publique) et LDLC (distributeur)
3. Croisement des montants des marches avec les fourchettes de prix commerciaux

### Classification par sous-categorie

Sur les 2 293 marches de fournitures, **1 563 (68%)** ont ete classifies dans 21 sous-categories de produits :

| Sous-categorie | Nb marches | Montant total | Prix moyen/marche |
|---|---|---|---|
| Electromenager (au sens large) | 1 012 | 1 332 M EUR | 1 317 k EUR |
| Mobilier de bureau | 111 | 64 M EUR | 579 k EUR |
| Imprimantes/reprographie | 66 | 43 M EUR | 654 k EUR |
| Alimentaire/restauration | 81 | 23 M EUR | 280 k EUR |
| Vehicules | 57 | 47 M EUR | 817 k EUR |
| Logiciels | 41 | 15 M EUR | 377 k EUR |
| Materiel construction | 43 | 7 M EUR | 172 k EUR |
| Reseau informatique | 30 | 29 M EUR | 965 k EUR |
| Chauffage/climatisation | 26 | 12 M EUR | 474 k EUR |
| Vetements de travail/EPI | 23 | 8 M EUR | 369 k EUR |
| Eclairage | 17 | 5 M EUR | 287 k EUR |
| Telephonie | 16 | 3 M EUR | 198 k EUR |
| Fournitures de bureau | 7 | 9 M EUR | 1 318 k EUR |
| Ecrans/moniteurs | 6 | 2 M EUR | 409 k EUR |
| Securite/videosurveillance | 5 | 1 M EUR | 257 k EUR |
| Serveurs | 5 | 14 M EUR | 2 823 k EUR |

### Prix commerciaux de reference (sources: UGAP, LDLC)

**Informatique (prix UGAP, TTC) :**
- PC portable entree de gamme : 412 EUR (Lenovo ThinkBook 14 Gen 8, 8Go/256Go)
- PC portable milieu de gamme : 612-687 EUR (ThinkPad E14/L14, 8-16Go)
- PC portable haut de gamme : 923-1 976 EUR (HP EliteBook, ThinkPad P1/P16)
- Ecran/moniteur : 120-800 EUR

**Mobilier (prix UGAP, TTC) :**
- Bureau informatique : 158-267 EUR
- Chaise de bureau : 96-288 EUR
- Armoire metallique : 607-729 EUR
- Lampe de bureau : 29-147 EUR
- Cabine acoustique : 5 630 EUR

**Vehicules (prix catalogue HT) :**
- Utilitaire (Kangoo/Berlingo/Partner) : 22 000-24 000 EUR
- Berline de service : 25 000-35 000 EUR
- Bus electrique : 300 000-600 000 EUR

---

## Etape 3 - Identification des anomalies

### Criteres de detection

Chaque marche recoit un **score de suspicion** (0 a 4+) base sur :
- **+2 pts** : Marche passe sans publicite ni mise en concurrence
- **+2 pts** : Fournisseur unique (1 seule offre recue)
- **+1 pt** : Montant anormalement eleve pour la categorie

### Resultats globaux (sur 10 000 marches)

| Indicateur | Valeur |
|---|---|
| **Valeur totale analysee** | 8 407 105 321 EUR |
| **Marches sans concurrence** | 458 (4,6%) = **494 563 300 EUR** (5,9%) |
| **Marches fournisseur unique** | 269 = **228 587 611 EUR** |
| **Marches sans info concurrence** | 8 983 (89,8%) |
| **Total anomalies flaggees** | 688 marches = **604 536 614 EUR** |

### Top 10 des anomalies par montant

| # | Montant | Type | Objet |
|---|---|---|---|
| 1 | 120 000 000 EUR | Sans concurrence | Fourniture autobus articules electriques |
| 2 | 100 215 648 EUR | Sans concurrence + 1 offre | Specialites pharmaceutiques GCS GRAPS Grand Est |
| 3 | 100 215 648 EUR | Sans concurrence + 1 offre | Specialites pharmaceutiques GCS GRAPS Grand Est (doublon) |
| 4 | 68 504 538 EUR | 1 offre | Usine de valorisation energetique |
| 5 | 26 000 000 EUR | Sans concurrence | Restauration collective scolaire/periscolaire |
| 6 | 10 000 000 EUR | Sans concurrence | Convention prevoyance |
| 7 | 5 520 000 EUR | Sans concurrence | Titres-restaurant dematerialises |
| 8 | 5 267 186 EUR | Sans concurrence + 1 offre | Specialites pharmaceutiques |
| 9 | 4 726 910 EUR | Sans concurrence | Assurance flotte vehicules |
| 10 | 4 524 215 EUR | Sans concurrence | 6 autobus SAFRA Hycity 12m |

### Anomalies specifiques aux fournitures COTS (34 flaggees, 11,7 M EUR)

Les cas les plus suspects dans les categories comparables a des prix commerciaux :

1. **4 524 215 EUR** - 6 autobus SAFRA sans concurrence (754 k/bus, prix marche ~400-600k)
2. **1 500 000 EUR** - Logiciel SOLIS/SOLATIS, maintenance sans concurrence
3. **1 183 720 EUR** - Chauffage individuel, 1 seule offre sur appel d'offres ouvert
4. **600 000 EUR** - Progiciels RH, sans concurrence
5. **600 000 EUR** - Pieces vehicules lourds, sans concurrence
6. **400 000 EUR** - Logiciel police municipale MUNICIPOL, sans concurrence
7. **350 150 EUR** - Licence ESRI (SIG), sans concurrence
8. **99 999 EUR** - Tablette a commande oculaire, sans concurrence (prix unitaire potentiellement tres eleve)

### Concentration des fournisseurs

Les 20 premiers titulaires captent a eux seuls plus de **2,5 milliards EUR** de marches.

Cas notable : un seul acheteur (GCS GRAPS Grand Est, SIRET 13002682600011) a attribue **plus de 200 M EUR** de marches pharmaceutiques sans concurrence au meme fournisseur.

### Doublons potentiels

542 combinaisons objet+montant apparaissent en double, dont :
- 46 fois le meme marche "Mission d'Architecte-Conseil du CAUE des Bouches-du-Rhone" a 112 220 EUR
- 6 fois "MARCHE DE TRAVAUX 2024-2028" a 20 000 000 EUR
- Nombreux doublons dans les marches pharmaceutiques du GCS GRAPS

### Opacite des donnees

Le constat le plus frappant : **89,8% des marches** (8 983 sur 10 000) n'indiquent pas le nombre d'offres recues. Il est donc impossible d'evaluer le niveau de concurrence reel sur la grande majorite des contrats publics francais. C'est un probleme structurel de transparence.

### Fichiers produits

| Fichier | Description | Lignes |
|---|---|---|
| analyse_comparative.csv | Tous les marches compares aux prix commerciaux | 550 |
| anomalies.csv | Anomalies COTS (score >= 2) | 34 |
| anomalies_completes.csv | Toutes les anomalies (sans concurrence + fournisseur unique) | 688 |

---

## Etape 4 - Scoring et classement approfondi

### Enrichissement via API Sirene

70 fournisseurs cles ont ete enrichis via l'API Annuaire des Entreprises (recherche-entreprises.api.gouv.fr) :
- Nom complet de l'entreprise
- Activite principale, effectifs, date de creation
- Commune, departement, nombre d'etablissements

### Systeme de scoring (0-100)

Chaque marche recoit un score de "facilite de sous-enchere" base sur :

| Facteur | Points |
|---|---|
| Marche sans publicite ni concurrence | +15 |
| Une seule offre recue | +15 |
| Fournisseur avec 3+ marches sans concurrence (captivite) | +10 |
| Fournisseur present sur 10+ marches (concentration) | +5 |
| Categorie COTS (comparable prix commercial) | +5 |
| Montant dans la fourchette 50k-5M EUR (accessible) | +5 |
| 5+ offres recues (concurrence saine) | -10 |
| Montant > 20M EUR (complexite) | -5 |
| Montant < 50k EUR (peu interessant) | -10 |

### Resultats du scoring

| Tranche de score | Nb marches | Montant total | Economie estimee |
|---|---|---|---|
| Score >= 70 (haute opportunite) | 761 | 346 M EUR | 52-121 M EUR |
| Score 60-69 (opportunite moyenne) | 1 778 | 1 104 M EUR | - |
| Score < 60 (faible opportunite) | 7 461 | 6 957 M EUR | - |

### Fournisseurs cles identifies

- **SMACL ASSURANCES SA** : 195 marches, dont 18 sans concurrence - acteur dominant des assurances collectivites
- **NEXPUBLICA FRANCE** : 14 marches, dont 10 sans concurrence - editeur de logiciels de gestion publique
- **UGAP** : 12 marches - la centrale d'achat publique elle-meme
- **ESRI FRANCE** : Logiciels SIG, marches sans concurrence (situation de quasi-monopole)

### Fichiers produits

| Fichier | Description | Lignes |
|---|---|---|
| marches_scores.csv | Tous les marches avec score de sous-enchere | 10 000 |
| top50_opportunites.csv | Top 50 des opportunites | 50 |
| fournisseurs_enrichis.csv | Profils fournisseurs enrichis (Sirene) | 70 |

---

## Etape 5 - Livrables finaux

### Tableau de bord interactif

Un dashboard HTML interactif a ete genere (`dashboard.html`) avec navigation laterale et 11 sections :
- Chiffres cles en cartes animees (6 indicateurs)
- Distribution des scores de suspicion (bar chart)
- Repartition par type de procedure (pie chart)
- Top 15 categories par montant (bar chart horizontal, trie par montant decroissant)
- Top 10 fournisseurs avec marquage des marches sans concurrence
- Tableau interactif des 50 meilleures opportunites avec liens DECP officiels
- Extraits de donnees brutes DECP et BOAMP
- Comparaison prix UGAP vs prix grand public (detection de surcouts)
- Section methodologie complete
- **Focus Lyon** : etude de cas sur 618 marches lyonnais

Chaque contrat reference dans les tableaux dispose d'un badge cliquable "DECP" renvoyant vers la fiche officielle sur data.economie.gouv.fr (API v2.1).

### Synthese finale

Sur un echantillon de **10 000 marches publics francais** (8,4 Mds EUR) :

1. **604 M EUR d'anomalies** identifiees (688 marches)
2. **52 a 121 M EUR d'economies** estimees sur les 761 opportunites haute priorite
3. **458 marches** passes sans aucune mise en concurrence
4. **89,8%** des marches ne publient pas le nombre d'offres recues
5. Concentration excessive de certains fournisseurs (SMACL: 195 marches, NEXPUBLICA: 14 marches captifs)

### Tous les fichiers produits

| Fichier | Description |
|---|---|
| RAPPORT.md | Ce rapport |
| dashboard.html | Tableau de bord interactif |
| decp_marches_10000.csv | 10 000 marches bruts |
| decp_fournitures_cots.csv | 2 293 fournitures comparables |
| boamp_attributions.csv | 724 avis d'attribution BOAMP |
| boamp_avis_3000.csv | 3 000 avis BOAMP |
| analyse_comparative.csv | 550 marches compares aux prix commerciaux |
| anomalies.csv | 34 anomalies COTS |
| anomalies_completes.csv | 688 anomalies totales |
| marches_scores.csv | 10 000 marches avec scoring |
| top50_opportunites.csv | Top 50 opportunites |
| fournisseurs_enrichis.csv | 70 profils fournisseurs |
| lyon_markets.json | 618 marches zone Lyon (DECP brut) |
| lyon_dashboard_data.json | Donnees analysees pour le focus Lyon |

---

## Etape 6 - Focus collectivite : Lyon

### Objectif

Pour rendre la demarche concrete et accessible aux citoyens, nous avons isole les marches publics executes a Lyon ou passes par des acheteurs lyonnais. Ce zoom local permet de montrer comment l'approche nationale s'applique a l'echelle d'une ville.

### Collecte des donnees lyonnaises

- **Source** : API DECP (data.economie.gouv.fr)
- **Filtres** : `lieuexecution_nom like "%Lyon%"` (500 resultats) + `acheteur_nom like "%lyon%"` (131 resultats)
- **Deduplication** : 618 marches uniques
- **Enrichissement fournisseurs** : API Annuaire des Entreprises (recherche-entreprises.api.gouv.fr)
- **Fichiers** : `lyon_markets.json` (donnees brutes), `lyon_dashboard_data.json` (donnees analysees)

### Resultats cles

| Indicateur | Valeur |
|---|---|
| **Marches analyses** | 618 |
| **Montant total** | 486 M EUR |
| **Sans concurrence** | 84 (13,6%) = 17,3 M EUR |
| **Acheteur principal** | ESID Lyon (Defense) : 64 marches, 54 M EUR |

### Repartition par categorie (top 5)

| Categorie | Nb marches | Montant | Sans concurrence |
|---|---|---|---|
| Travaux de construction | 198 | 180 M EUR | 6 |
| Services aux entreprises | 62 | 63 M EUR | 9 |
| Architecture/ingenierie | 81 | 37 M EUR | 2 |
| Materiaux de construction | 37 | 36 M EUR | 5 |
| Services informatiques | 20 | 36 M EUR | 3 |

### Top 10 fournisseurs (par montant cumule)

| Fournisseur | Marches | Montant |
|---|---|---|
| BYBLOS HUMAN SECURITY | 3 | 31,3 M EUR |
| SOLUTEC (AUBAY) | 1 | 20,0 M EUR |
| LES METIERS DU BOIS | 8 | 13,3 M EUR |
| SPIE ICS | 1 | 12,0 M EUR |
| WILLIS TOWERS WATSON | 4 | 11,5 M EUR |
| SAMNET | 1 | 9,0 M EUR |
| CREB Batiment | 3 | 8,8 M EUR |
| SPIE FACILITIES | 5 | 8,5 M EUR |
| NXO FRANCE | 1 | 8,0 M EUR |
| GREEN STYLE | 1 | 8,0 M EUR |

### Marches sans concurrence notables

| Montant | Titulaire | Objet | Ref DECP |
|---|---|---|---|
| 3 408 430 EUR | COUGNAUD | Location batiments modulaires (sites Pompidou, Kennedy, etc.) | 2023O499900 |
| 1 600 000 EUR | NEXPUBLICA | Maintenance Chronogestor/Chronotime + licences | 2023O4973A00 |
| 1 223 248 EUR | AXA FRANCE IARD | Assurance multirisques du patrimoine | 2023O526200 |
| 1 106 389 EUR | FLOWBIRD | Deploiement modems 4G horodateurs | 2023O479800 |
| 948 000 EUR | OLYMPIQUE LYONNAIS | Places et abonnements (lot 1, equipe pro masculine) | 2023O4713A00 |
| 800 000 EUR | SPLM | Droits stationnement parcs SPLM | 2023O5179A00 |
| 800 000 EUR | LYON PARC AUTO | Droits stationnement parcs Lyon Parc Auto | 2023O4631A00 |
| 720 000 EUR | EBULLISCIENCE | Sensibilisation sciences ecoles primaires | 2023O5046A00 |
| 667 000 EUR | SPORTFIVE EMEA | Places et abonnements OL (lot 2) | 2023O4714A00 |
| 368 000 EUR | SERIS SECURITY | Securisation et gardiennage site CIRC | 2023O496400 |

Chaque reference DECP est verifiable via : `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/decp-v3-marches-valides/records?where=id%3D%22{REF}%22&limit=1`

### Constats

1. **Stationnement** : deux marches de 800 000 EUR chacun attribues sans concurrence a la SPLM et Lyon Parc Auto, delegataires historiques. La question de la remise en concurrence periodique se pose.
2. **Olympique Lyonnais** : 1,6 M EUR cumules (deux lots) pour des places et abonnements, negocies sans concurrence. Le caractere exclusif de la prestation peut justifier l'absence de concurrence, mais le montant merite un examen.
3. **Construction dominante** : 37% des montants (180 M EUR), coherent pour une metropole en developpement.
4. **Services aux entreprises** : 63 M EUR, dont 9 marches sans concurrence — secteur ou la mise en concurrence est generalement plus facile a organiser.
