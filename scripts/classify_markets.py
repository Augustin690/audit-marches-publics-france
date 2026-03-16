import json
import re
from collections import defaultdict, Counter

with open("/workspace/data/decp_fournitures_cots.json", "r", encoding="utf-8") as f:
    marches = json.load(f)

print(f"Analyse de {len(marches)} marches de fournitures\n")

# Define keyword-based sub-categories for COTS products
PRODUCT_KEYWORDS = {
    "ordinateurs_portables": ["ordinateur portable", "laptop", "pc portable", "notebook", "chromebook"],
    "ordinateurs_fixes": ["ordinateur fixe", "poste de travail", "station de travail", "pc fixe", "unité centrale"],
    "ecrans_moniteurs": ["écran", "moniteur", "affichage", "display"],
    "imprimantes": ["imprimante", "impression", "copieur", "multifonction", "reprographie"],
    "tablettes": ["tablette", "ipad", "tablet"],
    "serveurs": ["serveur", "server", "hébergement", "datacenter"],
    "reseau": ["réseau", "switch", "routeur", "firewall", "wifi", "wi-fi", "borne", "câblage réseau"],
    "telephonie": ["téléphone", "téléphonie", "smartphone", "mobile", "standard téléphonique"],
    "logiciels": ["logiciel", "licence", "microsoft", "office", "antivirus", "saas", "progiciel"],
    "mobilier_bureau": ["mobilier", "bureau", "siège", "chaise", "fauteuil", "armoire", "rangement", "étagère", "table"],
    "mobilier_scolaire": ["mobilier scolaire", "table scolaire", "chaise scolaire", "pupitre"],
    "electromenager": ["électroménager", "réfrigérateur", "lave-linge", "lave-vaisselle", "four", "micro-onde"],
    "vehicules": ["véhicule", "voiture", "automobile", "utilitaire", "fourgon", "camion", "bus", "autobus", "autocar"],
    "vehicules_electriques": ["véhicule électrique", "voiture électrique", "bus électrique", "borne de recharge", "irve"],
    "carburant": ["carburant", "gazole", "gasoil", "essence", "gnv", "fuel"],
    "fournitures_bureau": ["fourniture de bureau", "papeterie", "papier", "toner", "cartouche", "encre"],
    "vetements_travail": ["vêtement", "tenue", "uniforme", "epi", "chaussure de sécurité", "gant"],
    "materiel_medical": ["dispositif médical", "consommable médical", "seringue", "gant médical", "compresse", "pansement"],
    "imagerie_medicale": ["imagerie", "scanner", "irm", "radiologie", "échographe", "mammographe"],
    "pharmacie": ["médicament", "pharmaceutique", "spécialité", "pharmacie", "vaccin"],
    "materiel_labo": ["laboratoire", "réactif", "automate", "analyseur", "centrifugeuse", "pipette"],
    "eclairage": ["éclairage", "luminaire", "ampoule", "led", "lampe", "candélabre"],
    "chauffage_clim": ["chauffage", "climatisation", "chaudière", "pompe à chaleur", "pac", "cvc"],
    "electricite_energie": ["électricité", "énergie", "acheminement", "gaz naturel", "photovoltaïque"],
    "alimentaire_restauration": ["denrée", "alimentaire", "restauration", "repas", "cantine", "surgelé", "viande", "fruit", "légume"],
    "materiel_construction": ["matériau", "ciment", "béton", "acier", "bois", "peinture", "quincaillerie"],
    "securite": ["vidéosurveillance", "caméra", "alarme", "contrôle d'accès", "détection incendie", "extincteur"],
    "nettoyage_produits": ["produit d'entretien", "nettoyage", "hygiène", "savon", "désinfectant", "papier toilette"],
}

def classify_market(objet):
    """Classify a market based on its object description."""
    if not objet:
        return "non_classe"
    objet_lower = objet.lower()
    matches = []
    for category, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if kw in objet_lower:
                matches.append(category)
                break
    if matches:
        return matches[0]  # Primary match
    return "non_classe"

# Classify all markets
classified = defaultdict(list)
for m in marches:
    cat = classify_market(m.get("objet", ""))
    m["sous_categorie"] = cat
    classified[cat].append(m)

# Print classification results
print("=" * 80)
print("CLASSIFICATION DES MARCHES PAR SOUS-CATEGORIE DE PRODUIT")
print("=" * 80)

total_classified = sum(len(v) for k, v in classified.items() if k != "non_classe")
print(f"\nMarches classifies: {total_classified} / {len(marches)} ({100*total_classified/len(marches):.1f}%)")
print(f"Non classes: {len(classified['non_classe'])}\n")

results = []
for cat, items in sorted(classified.items(), key=lambda x: -sum(i.get("montant", 0) for i in x[1])):
    total = sum(i.get("montant", 0) for i in items)
    avg = total / len(items) if items else 0
    results.append({
        "categorie": cat,
        "nb": len(items),
        "total_eur": total,
        "moyenne_eur": avg,
    })
    if cat != "non_classe":
        print(f"  {cat:30s} : {len(items):4d} marches | Total: {total:>14,.0f} EUR | Moy: {avg:>12,.0f} EUR")

# Show examples for key categories
print("\n" + "=" * 80)
print("EXEMPLES DE MARCHES PAR CATEGORIE (pour cross-referencing)")
print("=" * 80)

interesting_cats = [
    "ordinateurs_portables", "ordinateurs_fixes", "imprimantes", "tablettes",
    "mobilier_bureau", "vehicules", "fournitures_bureau", "eclairage",
    "logiciels", "telephonie", "ecrans_moniteurs", "vetements_travail",
    "materiel_medical", "alimentaire_restauration"
]

for cat in interesting_cats:
    items = classified.get(cat, [])
    if not items:
        continue
    print(f"\n--- {cat.upper()} ({len(items)} marches) ---")
    # Show 5 examples sorted by amount
    for m in sorted(items, key=lambda x: x.get("montant", 0), reverse=True)[:5]:
        offres = m.get("offres_recues", "?")
        proc = m.get("procedure", "?")[:30]
        print(f"  {m.get('montant', 0):>12,.0f} EUR | Offres: {offres} | {proc}")
        print(f"    -> {m.get('objet', 'N/A')[:120]}")

# Save classified data
with open("/workspace/data/decp_classified.json", "w", encoding="utf-8") as f:
    json.dump(marches, f, ensure_ascii=False, indent=2)

# Save summary
with open("/workspace/data/classification_summary.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\nClassification sauvegardee dans /workspace/data/decp_classified.json")
