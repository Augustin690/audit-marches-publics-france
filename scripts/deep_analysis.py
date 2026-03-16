import json
import csv
from collections import defaultdict, Counter

# Load full DECP dataset
with open("/workspace/data/decp_marches_raw.json", "r", encoding="utf-8") as f:
    all_marches = json.load(f)

print("=" * 90)
print("ANALYSE APPROFONDIE - 10,000 MARCHES PUBLICS")
print("=" * 90)

# 1. Marches sans concurrence (tous types)
sans_concurrence = [m for m in all_marches if 
    "sans publicité" in (m.get("procedure", "") or "").lower() or
    "négocié sans" in (m.get("procedure", "") or "").lower()]

print(f"\n1. MARCHES SANS CONCURRENCE: {len(sans_concurrence)}")
total_sc = sum(m.get("montant", 0) for m in sans_concurrence)
print(f"   Montant total: {total_sc:,.0f} EUR")

# Top 20 biggest no-competition contracts
sans_concurrence.sort(key=lambda x: x.get("montant", 0), reverse=True)
print(f"\n   Top 20 marches sans concurrence par montant:")
for i, m in enumerate(sans_concurrence[:20], 1):
    print(f"   {i:2d}. {m.get('montant', 0):>14,.0f} EUR | CPV {str(m.get('codecpv', ''))[:8]}")
    print(f"       {(m.get('objet', '') or 'N/A')[:110]}")
    print(f"       Acheteur: {(m.get('acheteur_nom', '') or m.get('acheteur_id', 'N/A'))[:60]}")

# 2. Marches avec 1 seule offre
une_offre = [m for m in all_marches if m.get("offresrecues") and m["offresrecues"] == 1]
print(f"\n2. MARCHES AVEC UNE SEULE OFFRE: {len(une_offre)}")
total_1o = sum(m.get("montant", 0) for m in une_offre)
print(f"   Montant total: {total_1o:,.0f} EUR")

une_offre.sort(key=lambda x: x.get("montant", 0), reverse=True)
print(f"\n   Top 15 marches fournisseur unique:")
for i, m in enumerate(une_offre[:15], 1):
    print(f"   {i:2d}. {m.get('montant', 0):>14,.0f} EUR | CPV {str(m.get('codecpv', ''))[:8]}")
    print(f"       {(m.get('objet', '') or 'N/A')[:110]}")

# 3. Concentration des titulaires (memes fournisseurs qui raflent plusieurs marches)
titulaire_stats = defaultdict(lambda: {"count": 0, "total": 0, "marches": []})
for m in all_marches:
    tit = m.get("titulaire_id_1")
    if tit:
        titulaire_stats[tit]["count"] += 1
        titulaire_stats[tit]["total"] += m.get("montant", 0)
        if len(titulaire_stats[tit]["marches"]) < 5:
            titulaire_stats[tit]["marches"].append(m.get("objet", "")[:80])

print(f"\n3. CONCENTRATION DES TITULAIRES")
print(f"   Titulaires uniques: {len(titulaire_stats)}")
multi_marches = {k: v for k, v in titulaire_stats.items() if v["count"] >= 5}
print(f"   Titulaires avec 5+ marches: {len(multi_marches)}")

top_tit = sorted(titulaire_stats.items(), key=lambda x: -x[1]["total"])[:20]
print(f"\n   Top 20 titulaires par montant total:")
for i, (siret, s) in enumerate(top_tit, 1):
    print(f"   {i:2d}. SIRET {siret} : {s['count']} marches | {s['total']:>14,.0f} EUR")
    for obj in s["marches"][:2]:
        print(f"       -> {obj}")

# 4. Marches doublons potentiels (meme objet, meme montant)
from collections import Counter
doublon_keys = Counter()
for m in all_marches:
    key = f"{m.get('objet', '')[:50]}|{m.get('montant', 0)}"
    doublon_keys[key] += 1

doublons = {k: v for k, v in doublon_keys.items() if v > 1 and "|0" not in k}
print(f"\n4. DOUBLONS POTENTIELS (meme objet + meme montant)")
print(f"   Combinaisons dupliquees: {len(doublons)}")

top_doublons = sorted(doublons.items(), key=lambda x: -x[1])[:15]
for k, count in top_doublons:
    objet, montant = k.split("|")
    print(f"   x{count} | {float(montant):>14,.0f} EUR | {objet}")

# 5. Summary stats
print(f"\n{'='*90}")
print("STATISTIQUES GENERALES")
print(f"{'='*90}")

total_all = sum(m.get("montant", 0) for m in all_marches)
print(f"Valeur totale analysee: {total_all:,.0f} EUR")
print(f"Marches sans concurrence: {len(sans_concurrence)} ({100*len(sans_concurrence)/len(all_marches):.1f}%) = {total_sc:,.0f} EUR ({100*total_sc/total_all:.1f}%)")
print(f"Marches fournisseur unique: {len(une_offre)} = {total_1o:,.0f} EUR")
print(f"Marches sans info concurrence: {sum(1 for m in all_marches if not m.get('offresrecues')):,d}")

# Save consolidated anomalies
all_anomalies = []
for m in sans_concurrence:
    all_anomalies.append({
        "type_anomalie": "Sans concurrence",
        "id": m.get("id"),
        "objet": (m.get("objet", "") or "")[:150],
        "montant": m.get("montant", 0),
        "codecpv": m.get("codecpv"),
        "procedure": m.get("procedure"),
        "acheteur_id": m.get("acheteur_id"),
        "acheteur_nom": m.get("acheteur_nom"),
        "titulaire_siret": m.get("titulaire_id_1"),
        "date": m.get("datenotification"),
        "offres_recues": m.get("offresrecues"),
    })

for m in une_offre:
    # Avoid duplicates
    if not any(a["id"] == m.get("id") for a in all_anomalies):
        all_anomalies.append({
            "type_anomalie": "Fournisseur unique",
            "id": m.get("id"),
            "objet": (m.get("objet", "") or "")[:150],
            "montant": m.get("montant", 0),
            "codecpv": m.get("codecpv"),
            "procedure": m.get("procedure"),
            "acheteur_id": m.get("acheteur_id"),
            "acheteur_nom": m.get("acheteur_nom"),
            "titulaire_siret": m.get("titulaire_id_1"),
            "date": m.get("datenotification"),
            "offres_recues": m.get("offresrecues"),
        })

all_anomalies.sort(key=lambda x: -x["montant"])

with open("/workspace/output/anomalies_completes.csv", "w", encoding="utf-8", newline="") as f:
    if all_anomalies:
        writer = csv.DictWriter(f, fieldnames=all_anomalies[0].keys())
        writer.writeheader()
        writer.writerows(all_anomalies)

print(f"\nAnomalies completes sauvegardees: {len(all_anomalies)} marches")
print(f"Montant total des anomalies: {sum(a['montant'] for a in all_anomalies):,.0f} EUR")

