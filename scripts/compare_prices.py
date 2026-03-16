import json
import csv
import re
from collections import defaultdict

# =============================================================================
# PRIX COMMERCIAUX DE REFERENCE
# Sources: UGAP (centrale d'achat publique), LDLC, prix marche connus
# =============================================================================

COMMERCIAL_PRICES = {
    # INFORMATIQUE & BUREAUTIQUE (prix unitaires HT)
    "ordinateurs_portables": {
        "prix_min": 400,
        "prix_moyen": 700,
        "prix_max": 2000,
        "unite": "unite",
        "source": "UGAP: 412-1976 EUR | LDLC: 500-1500 EUR",
        "references": [
            ("Lenovo ThinkBook 14 Gen 8 (8Go/256Go)", 412, "UGAP"),
            ("Lenovo ThinkPad E14 Gen 7 (8Go/256Go)", 612, "UGAP"),
            ("Lenovo ThinkPad L14 Gen 6 Ryzen 5 (8Go/256Go)", 687, "UGAP"),
            ("HP EliteBook 8 G1i (16Go/256Go)", 923, "UGAP"),
            ("Lenovo ThinkPad P16 G3 (16Go/256Go)", 1533, "UGAP"),
            ("Lenovo ThinkPad P1 G7 (16Go/256Go)", 1976, "UGAP"),
        ]
    },
    "ordinateurs_fixes": {
        "prix_min": 350,
        "prix_moyen": 600,
        "prix_max": 1500,
        "unite": "unite",
        "source": "Prix marche pro 2024-2025",
    },
    "ecrans_moniteurs": {
        "prix_min": 120,
        "prix_moyen": 250,
        "prix_max": 800,
        "unite": "unite",
        "source": "Prix marche LDLC/Amazon",
    },
    "imprimantes": {
        "prix_min": 200,
        "prix_moyen": 800,
        "prix_max": 5000,
        "unite": "unite",
        "source": "Imprimante laser pro: 200-5000 EUR selon capacite",
    },
    "tablettes": {
        "prix_min": 300,
        "prix_moyen": 600,
        "prix_max": 1500,
        "unite": "unite",
        "source": "iPad/Surface/Samsung Tab prix pro",
    },
    "serveurs": {
        "prix_min": 2000,
        "prix_moyen": 8000,
        "prix_max": 50000,
        "unite": "unite",
        "source": "Dell PowerEdge / HPE ProLiant prix catalogue",
    },
    "reseau": {
        "prix_min": 100,
        "prix_moyen": 2000,
        "prix_max": 20000,
        "unite": "lot",
        "source": "Switch/routeur/firewall pro",
    },
    "telephonie": {
        "prix_min": 50,
        "prix_moyen": 500,
        "prix_max": 5000,
        "unite": "unite/lot",
        "source": "Standard telephonique / smartphones pro",
    },
    "logiciels": {
        "prix_min": 50,
        "prix_moyen": 500,
        "prix_max": 10000,
        "unite": "licence",
        "source": "Microsoft 365: 150-400/an, antivirus: 30-80/poste",
    },
    # MOBILIER
    "mobilier_bureau": {
        "prix_min": 80,
        "prix_moyen": 400,
        "prix_max": 2000,
        "unite": "piece",
        "source": "UGAP: bureau 158-267 EUR, chaise 96-288 EUR, armoire 607-729 EUR",
        "references": [
            ("Bureau informatique Dana 80x70", 267, "UGAP"),
            ("Bureau informatique Soft 120x70", 208, "UGAP"),
            ("Chaise bureau Dallas roulettes", 120, "UGAP"),
            ("Armoire metallique Fusion h198", 729, "UGAP"),
            ("Fauteuil Club Dream", 273, "UGAP"),
            ("Cabine acoustique Cocon", 5630, "UGAP"),
        ]
    },
    # VEHICULES
    "vehicules": {
        "prix_min": 15000,
        "prix_moyen": 30000,
        "prix_max": 120000,
        "unite": "vehicule",
        "source": "Renault Kangoo: ~22k, Peugeot Partner: ~24k, Citroen Berlingo: ~23k (prix catalogue HT)",
    },
    "vehicules_electriques": {
        "prix_min": 25000,
        "prix_moyen": 45000,
        "prix_max": 300000,
        "unite": "vehicule",
        "source": "Bus electrique: 300-600k, utilitaire elec: 30-45k",
    },
    # AUTRES
    "eclairage": {
        "prix_min": 20,
        "prix_moyen": 100,
        "prix_max": 1000,
        "unite": "unite/lot",
        "source": "UGAP: lampe bureau 29-147 EUR",
    },
    "chauffage_clim": {
        "prix_min": 2000,
        "prix_moyen": 15000,
        "prix_max": 100000,
        "unite": "installation",
        "source": "PAC: 8-20k, chaudiere: 3-10k, clim: 2-15k",
    },
    "vetements_travail": {
        "prix_min": 10,
        "prix_moyen": 50,
        "prix_max": 200,
        "unite": "piece",
        "source": "EPI: gants 5-30 EUR, chaussures secu 50-150 EUR, tenue 30-100 EUR",
    },
    "fournitures_bureau": {
        "prix_min": 5,
        "prix_moyen": 30,
        "prix_max": 200,
        "unite": "lot",
        "source": "Ramette papier A4: 4-8 EUR, toner: 30-150 EUR",
    },
    "alimentaire_restauration": {
        "prix_min": 2,
        "prix_moyen": 8,
        "prix_max": 20,
        "unite": "repas/kg",
        "source": "Cout moyen repas collectif: 5-12 EUR/repas",
    },
    "materiel_medical": {
        "prix_min": 100,
        "prix_moyen": 5000,
        "prix_max": 500000,
        "unite": "unite/lot",
        "source": "Tres variable: consommables 0.5-50 EUR, equipements lourds 50k-500k",
    },
    "materiel_construction": {
        "prix_min": 50,
        "prix_moyen": 500,
        "prix_max": 10000,
        "unite": "lot",
        "source": "Prix negoce: variable selon materiaux",
    },
    "carburant": {
        "prix_min": 1.4,
        "prix_moyen": 1.6,
        "prix_max": 1.8,
        "unite": "litre",
        "source": "Prix pompe 2024-2025: gazole 1.45-1.65 EUR/L",
    },
    "securite": {
        "prix_min": 200,
        "prix_moyen": 2000,
        "prix_max": 20000,
        "unite": "installation/lot",
        "source": "Camera IP: 100-500 EUR, systeme complet: 5-20k",
    },
    "nettoyage_produits": {
        "prix_min": 2,
        "prix_moyen": 20,
        "prix_max": 100,
        "unite": "unite/bidon",
        "source": "Produits entretien: 2-50 EUR/unite",
    },
    "materiel_labo": {
        "prix_min": 500,
        "prix_moyen": 5000,
        "prix_max": 50000,
        "unite": "unite",
        "source": "Equipement labo: 500-50k selon complexite",
    },
}

# =============================================================================
# ANALYSE COMPARATIVE
# =============================================================================

with open("/workspace/data/decp_classified.json", "r", encoding="utf-8") as f:
    marches = json.load(f)

print("=" * 90)
print("ETAPE 2 - CROISEMENT MARCHES PUBLICS vs PRIX COMMERCIAUX")
print("=" * 90)

# For each market, estimate if the amount seems reasonable
# We need to estimate quantity from the contract to get unit price
# Since DECP doesn't give quantity, we'll flag contracts where the total amount
# divided by typical unit count seems high

results = []
anomalies = []
stats_by_cat = defaultdict(lambda: {"count": 0, "total": 0, "flagged": 0, "flagged_amount": 0})

for m in marches:
    cat = m.get("sous_categorie", "non_classe")
    if cat == "non_classe" or cat not in COMMERCIAL_PRICES:
        continue
    
    montant = m.get("montant", 0)
    if not montant or montant <= 0:
        continue
    
    ref = COMMERCIAL_PRICES[cat]
    prix_moyen = ref["prix_moyen"]
    prix_max = ref["prix_max"]
    
    stats_by_cat[cat]["count"] += 1
    stats_by_cat[cat]["total"] += montant
    
    # Estimate potential units based on total amount
    estimated_units_at_avg = montant / prix_moyen if prix_moyen > 0 else 0
    estimated_units_at_max = montant / prix_max if prix_max > 0 else 0
    
    # Flag: high amount markets with few/no competition
    offres = m.get("offres_recues")
    procedure = m.get("procedure", "")
    
    # Determine suspicion level
    suspicion = 0
    reasons = []
    
    # Flag 1: negotiated without competition
    if "sans publicité" in procedure.lower() or "négocié sans" in procedure.lower():
        suspicion += 2
        reasons.append("Sans mise en concurrence")
    
    # Flag 2: single supplier
    if offres and offres <= 1:
        suspicion += 2
        reasons.append(f"Fournisseur unique ({offres} offre)")
    
    # Flag 3: very high amount for the category (top percentile)
    # We flag if the amount is suspiciously high for what seems like a standard purchase
    category_thresholds = {
        "ordinateurs_portables": 500000,
        "ordinateurs_fixes": 500000,
        "ecrans_moniteurs": 200000,
        "imprimantes": 1000000,
        "tablettes": 200000,
        "mobilier_bureau": 500000,
        "fournitures_bureau": 500000,
        "logiciels": 500000,
        "telephonie": 300000,
        "eclairage": 500000,
        "vetements_travail": 500000,
        "vehicules": 5000000,
        "alimentaire_restauration": 2000000,
        "chauffage_clim": 2000000,
        "reseau": 2000000,
        "securite": 500000,
        "carburant": 2000000,
        "materiel_medical": 5000000,
        "materiel_construction": 1000000,
        "nettoyage_produits": 200000,
        "materiel_labo": 1000000,
        "serveurs": 5000000,
    }
    
    threshold = category_thresholds.get(cat, 1000000)
    if montant > threshold:
        suspicion += 1
        reasons.append(f"Montant eleve ({montant:,.0f} > seuil {threshold:,.0f})")
    
    # Flag 4: for specific categories, check if unit price seems absurd
    # (e.g., a single laptop contract for 500k could mean 1000 units at 500 each = OK
    #  or it could mean overpriced small batch)
    
    result = {
        "id": m.get("id"),
        "objet": m.get("objet", "")[:150],
        "montant": montant,
        "categorie": cat,
        "procedure": procedure[:50],
        "offres_recues": offres,
        "acheteur_nom": m.get("acheteur_nom", ""),
        "titulaire_siret": m.get("titulaire_siret"),
        "date": m.get("datenotification"),
        "prix_ref_moyen": prix_moyen,
        "prix_ref_max": prix_max,
        "unites_estimees_prix_moyen": round(estimated_units_at_avg),
        "unites_estimees_prix_max": round(estimated_units_at_max),
        "suspicion_score": suspicion,
        "raisons_alerte": " | ".join(reasons) if reasons else "",
    }
    results.append(result)
    
    if suspicion >= 2:
        anomalies.append(result)
        stats_by_cat[cat]["flagged"] += 1
        stats_by_cat[cat]["flagged_amount"] += montant

# Sort anomalies by suspicion score and amount
anomalies.sort(key=lambda x: (-x["suspicion_score"], -x["montant"]))

print(f"\nMarches analyses: {len(results)}")
print(f"Anomalies flaggees (score >= 2): {len(anomalies)}")
print(f"Montant total des anomalies: {sum(a['montant'] for a in anomalies):,.0f} EUR")

print(f"\n{'='*90}")
print("RESUME PAR CATEGORIE")
print(f"{'='*90}")
print(f"{'Categorie':<30s} {'Marches':>8s} {'Total EUR':>16s} {'Flagges':>8s} {'Montant flagge':>16s}")
print("-" * 90)
for cat, s in sorted(stats_by_cat.items(), key=lambda x: -x[1]["flagged_amount"]):
    print(f"{cat:<30s} {s['count']:>8d} {s['total']:>16,.0f} {s['flagged']:>8d} {s['flagged_amount']:>16,.0f}")

print(f"\n{'='*90}")
print("TOP 30 ANOMALIES (score suspicion >= 2)")
print(f"{'='*90}")
for i, a in enumerate(anomalies[:30], 1):
    print(f"\n{i:2d}. [{a['suspicion_score']}] {a['montant']:>14,.0f} EUR | {a['categorie']}")
    print(f"    Objet: {a['objet'][:120]}")
    print(f"    Alerte: {a['raisons_alerte']}")
    print(f"    Procedure: {a['procedure']}")
    print(f"    Offres: {a['offres_recues']} | Date: {a['date']}")

# Save all results
with open("/workspace/data/analyse_comparative.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("/workspace/data/anomalies.json", "w", encoding="utf-8") as f:
    json.dump(anomalies, f, ensure_ascii=False, indent=2)

# Save CSVs
for filename, data in [("analyse_comparative.csv", results), ("anomalies.csv", anomalies)]:
    if data:
        with open(f"/workspace/output/{filename}", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

print(f"\n\nFichiers sauvegardes:")
print(f"  - /workspace/output/analyse_comparative.csv ({len(results)} marches)")
print(f"  - /workspace/output/anomalies.csv ({len(anomalies)} anomalies)")

