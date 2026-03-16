import json
import csv
from collections import Counter, defaultdict

# CPV code descriptions (main categories)
CPV_CATEGORIES = {
    "03": "Produits agricoles et d'élevage",
    "09": "Produits pétroliers et énergie",
    "14": "Produits miniers et carrières",
    "15": "Denrées alimentaires et boissons",
    "18": "Vêtements et accessoires",
    "22": "Imprimés et produits connexes",
    "24": "Produits chimiques",
    "30": "Machines de bureau, matériel informatique",
    "31": "Machines, appareils et matériel électriques",
    "32": "Équipements de radio, télévision, communication",
    "33": "Matériel médical et pharmaceutique",
    "34": "Équipements et fournitures de transport",
    "35": "Équipements de sécurité et de défense",
    "37": "Instruments de musique, articles de sport",
    "38": "Équipements de laboratoire et de mesure",
    "39": "Mobilier, aménagement, appareils ménagers",
    "42": "Machines industrielles",
    "43": "Machines pour mines et carrières",
    "44": "Structures et matériaux de construction",
    "45": "Travaux de construction",
    "48": "Logiciels et systèmes d'information",
    "50": "Services de réparation et maintenance",
    "55": "Services d'hôtellerie et de restauration",
    "60": "Services de transport",
    "64": "Services postaux et télécommunications",
    "66": "Services financiers et d'assurance",
    "70": "Services immobiliers",
    "71": "Services d'architecture et d'ingénierie",
    "72": "Services informatiques",
    "73": "Services de R&D",
    "75": "Services d'administration publique",
    "77": "Services agricoles et forestiers",
    "79": "Services aux entreprises",
    "80": "Services d'éducation et de formation",
    "85": "Services de santé et sociaux",
    "90": "Services d'assainissement et environnement",
    "92": "Services récréatifs, culturels et sportifs",
    "98": "Autres services communautaires"
}

# Categories of interest for price comparison (COTS-comparable)
COTS_CPV_PREFIXES = {
    "30": "Informatique & bureautique",
    "31": "Matériel électrique",
    "32": "Télécommunications",
    "33": "Matériel médical",
    "34": "Transport & véhicules",
    "35": "Sécurité & défense",
    "38": "Instruments de mesure",
    "39": "Mobilier & ménager",
    "44": "Matériaux de construction",
    "48": "Logiciels",
    "18": "Vêtements",
    "22": "Imprimés",
    "15": "Alimentaire",
}

print("=" * 70)
print("STRUCTURATION DES DONNÉES - MARCHÉS PUBLICS FRANÇAIS")
print("=" * 70)

# Load DECP data
with open("/workspace/data/decp_marches_raw.json", "r", encoding="utf-8") as f:
    decp = json.load(f)

print(f"\n📊 DECP: {len(decp)} marchés chargés")

# Categorize by CPV
cpv_groups = defaultdict(list)
fournitures = []  # Markets for goods (most comparable to commercial prices)

for r in decp:
    cpv = str(r.get("codecpv", ""))[:2]
    cpv_groups[cpv].append(r)
    
    if cpv in COTS_CPV_PREFIXES:
        fournitures.append(r)

print(f"\n📦 Marchés de fournitures comparables (COTS): {len(fournitures)}")
print(f"   Valeur totale: {sum(r['montant'] for r in fournitures if r.get('montant')):,.2f} EUR")

print(f"\n🏷️ Répartition par catégorie CPV (fournitures COTS):")
cots_by_cat = Counter()
cots_amount_by_cat = defaultdict(float)
for r in fournitures:
    cpv = str(r.get("codecpv", ""))[:2]
    cat_name = COTS_CPV_PREFIXES.get(cpv, cpv)
    cots_by_cat[cat_name] += 1
    cots_amount_by_cat[cat_name] += r.get("montant", 0)

for cat, count in cots_by_cat.most_common():
    amount = cots_amount_by_cat[cat]
    print(f"   {cat}: {count} marchés ({amount:,.0f} EUR)")

# Analyze single-supplier markets (no competition)
single_supplier = [r for r in fournitures if r.get("offresrecues") and r["offresrecues"] == 1]
no_competition_data = [r for r in fournitures if not r.get("offresrecues")]

print(f"\n🚩 Marchés à fournisseur unique (1 offre reçue): {len(single_supplier)}")
print(f"   Marchés sans données de concurrence: {len(no_competition_data)}")

# Analyze by procedure type
procedures = Counter(r.get("procedure", "N/A") for r in fournitures)
print(f"\n📋 Types de procédures (fournitures):")
for proc, count in procedures.most_common(10):
    print(f"   {proc}: {count}")

# Identify high-value single items
high_value = sorted(fournitures, key=lambda r: r.get("montant", 0), reverse=True)[:50]

print(f"\n💰 Top 20 marchés de fournitures par montant:")
for i, r in enumerate(high_value[:20], 1):
    cpv = str(r.get("codecpv", ""))[:2]
    cat = COTS_CPV_PREFIXES.get(cpv, cpv)
    print(f"   {i}. {r.get('montant', 0):>14,.2f} EUR | {cat} | {r.get('objet', 'N/A')[:80]}")

# Save structured fournitures data
structured = []
for r in fournitures:
    cpv = str(r.get("codecpv", ""))
    structured.append({
        "id": r.get("id"),
        "objet": r.get("objet"),
        "montant": r.get("montant"),
        "codecpv": cpv,
        "categorie_cpv": COTS_CPV_PREFIXES.get(cpv[:2], CPV_CATEGORIES.get(cpv[:2], "Autre")),
        "procedure": r.get("procedure"),
        "datenotification": r.get("datenotification"),
        "acheteur_id": r.get("acheteur_id"),
        "acheteur_nom": r.get("acheteur_nom"),
        "titulaire_siret": r.get("titulaire_id_1"),
        "offres_recues": r.get("offresrecues"),
        "lieu": r.get("lieuexecution_nom"),
        "formeprix": r.get("formeprix"),
    })

with open("/workspace/data/decp_fournitures_cots.json", "w", encoding="utf-8") as f:
    json.dump(structured, f, ensure_ascii=False, indent=2)

# Also save as CSV for easy viewing
with open("/workspace/data/decp_fournitures_cots.csv", "w", encoding="utf-8", newline="") as f:
    if structured:
        writer = csv.DictWriter(f, fieldnames=structured[0].keys())
        writer.writeheader()
        writer.writerows(structured)

print(f"\n✅ Données structurées sauvegardées:")
print(f"   - /workspace/data/decp_fournitures_cots.json ({len(structured)} marchés)")
print(f"   - /workspace/data/decp_fournitures_cots.csv")

# BOAMP analysis
print(f"\n{'=' * 70}")
print("ANALYSE BOAMP")
print("=" * 70)

with open("/workspace/data/boamp_avis_raw.json", "r", encoding="utf-8") as f:
    boamp = json.load(f)

print(f"\n📊 BOAMP: {len(boamp)} avis chargés")

# Type d'avis
types = Counter(r.get("type_avis", "N/A") for r in boamp)
print(f"\nTypes d'avis:")
for t, c in types.most_common():
    print(f"   {t}: {c}")

# Nature
natures = Counter(r.get("nature_categorise_libelle", r.get("nature_libelle", "N/A")) for r in boamp)
print(f"\nNatures:")
for n, c in natures.most_common(10):
    print(f"   {n}: {c}")

# Type marche
type_marches = Counter(r.get("type_marche", "N/A") for r in boamp)
print(f"\nType de marché:")
for t, c in type_marches.most_common():
    print(f"   {t}: {c}")

# Attribution notices with titulaire info
with_titulaire = [r for r in boamp if r.get("titulaire")]
print(f"\nAvis avec titulaire renseigné: {len(with_titulaire)}")

# Save BOAMP attributions
boamp_attributions = []
for r in boamp:
    if r.get("type_avis") in ["Attribution", "Résultat de marché"] or r.get("titulaire"):
        boamp_attributions.append({
            "id": r.get("id"),
            "objet": r.get("objet"),
            "famille": r.get("famille_libelle"),
            "nature": r.get("nature_categorise_libelle"),
            "type_marche": r.get("type_marche"),
            "type_avis": r.get("type_avis"),
            "procedure": r.get("procedure_libelle"),
            "acheteur": r.get("nomacheteur"),
            "titulaire": r.get("titulaire"),
            "departement": r.get("code_departement"),
            "date_parution": r.get("dateparution"),
            "url_avis": r.get("url_avis"),
        })

with open("/workspace/data/boamp_attributions.json", "w", encoding="utf-8") as f:
    json.dump(boamp_attributions, f, ensure_ascii=False, indent=2)

print(f"\n✅ Attributions BOAMP sauvegardées: {len(boamp_attributions)} avis")

# Final summary
print(f"\n{'=' * 70}")
print("RÉSUMÉ ÉTAPE 1")
print("=" * 70)
print(f"""
Sources collectées:
  1. DECP (Données Essentielles de la Commande Publique)
     - {len(decp)} marchés publics validés (2023-2025)
     - Valeur totale: {sum(r['montant'] for r in decp if r.get('montant')):,.2f} EUR
     
  2. BOAMP (Bulletin Officiel des Annonces de Marchés Publics)
     - {len(boamp)} avis récents
     - {len(boamp_attributions)} avis d'attribution

Données structurées pour analyse:
  - {len(structured)} marchés de fournitures COTS-comparables
  - Valeur: {sum(r['montant'] for r in structured if r.get('montant')):,.2f} EUR
  - Catégories: {len(cots_by_cat)} types de fournitures

Champs extraits par marché:
  id, objet, montant, code CPV, catégorie, procédure,
  date notification, acheteur (SIRET + nom), titulaire (SIRET),
  nombre d'offres reçues, lieu d'exécution, forme de prix
""")

