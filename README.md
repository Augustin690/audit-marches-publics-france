# Audit IA des Marchés Publics Français

Analyse automatisée des marchés publics français pour identifier les contrats potentiellement surpayés par rapport aux prix commerciaux, inspirée de l'approche appliquée aux contrats du Pentagone par [@Argona0x](https://x.com/Argona0x).

## Résultats clés

Sur un échantillon de **10 000 marchés publics** (8,4 Mds EUR) :

| Indicateur | Valeur |
|---|---|
| Anomalies identifiées | **604 M EUR** (688 marchés) |
| Économies estimées (haute priorité) | **52 à 121 M EUR** |
| Marchés sans concurrence | **458** (4,6%) |
| Marchés fournisseur unique | **269** |
| Marchés sans info concurrence | **89,8%** |

## Méthodologie

1. **Collecte** — Données ouvertes DECP (data.economie.gouv.fr) + BOAMP + API Sirene
2. **Classification** — Filtrage des fournitures comparables (COTS) par codes CPV
3. **Comparaison** — Croisement avec les prix commerciaux UGAP/LDLC
4. **Scoring** — Score de "facilité de sous-enchère" (0-100) basé sur concurrence, concentration fournisseur, catégorie
5. **Visualisation** — Dashboard interactif + rapport détaillé

## Structure du projet

```
├── scripts/                    # Scripts Python de collecte et analyse
│   ├── collect_decp.py         # Collecte 10 000 marchés DECP
│   ├── collect_boamp.py        # Collecte avis BOAMP
│   ├── structure_data.py       # Structuration et filtrage CPV
│   ├── classify_markets.py     # Classification par sous-catégorie
│   ├── compare_prices.py       # Comparaison prix commerciaux
│   ├── deep_analysis.py        # Analyse approfondie des anomalies
│   ├── sirene_enrich.py        # Enrichissement Sirene + scoring
│   ├── export_csv.py           # Export CSV
│   └── prepare_dashboard_data.py
├── data/                       # Données CSV produites
│   ├── decp_marches_10000.csv
│   ├── decp_fournitures_cots.csv
│   ├── boamp_attributions.csv
│   ├── boamp_avis_3000.csv
│   ├── analyse_comparative.csv
│   ├── anomalies.csv
│   ├── anomalies_completes.csv
│   ├── marches_scores.csv
│   ├── top50_opportunites.csv
│   └── fournisseurs_enrichis.csv
├── dashboard.html              # Tableau de bord interactif
└── RAPPORT.md                  # Rapport complet d'analyse
```

## Sources de données

- **DECP** — [data.economie.gouv.fr](https://data.economie.gouv.fr/explore/dataset/decp-v3-marches-valides/) (702 918 marchés disponibles)
- **BOAMP** — [boamp-datadila.opendatasoft.com](https://boamp-datadila.opendatasoft.com/explore/dataset/boamp/) (1 646 131 avis)
- **API Sirene** — [recherche-entreprises.api.gouv.fr](https://recherche-entreprises.api.gouv.fr)
- **UGAP** — Prix de référence centrale d'achat publique

## Dashboard

Le fichier `dashboard.html` contient un tableau de bord interactif avec :
- 6 indicateurs clés
- Distribution des scores de suspicion
- Répartition par type de procédure
- Top 15 catégories par montant
- Tableau interactif des 50 meilleures opportunités

## Licence

Ce projet utilise des données ouvertes publiques. L'analyse est fournie à titre informatif.
