import json
import urllib.request
import urllib.parse
import time
import csv
from collections import defaultdict

# Load anomalies
with open("/workspace/data/anomalies.json", "r", encoding="utf-8") as f:
    anomalies_cots = json.load(f)

# Load full dataset for top titulaires
with open("/workspace/data/decp_marches_raw.json", "r", encoding="utf-8") as f:
    all_marches = json.load(f)

# Collect unique SIRETs to query
titulaire_stats = defaultdict(lambda: {"count": 0, "total": 0, "sans_concurrence": 0, "categories": set()})
for m in all_marches:
    tit = m.get("titulaire_id_1")
    if tit:
        tit_str = str(int(tit)) if isinstance(tit, float) else str(tit)
        titulaire_stats[tit_str]["count"] += 1
        titulaire_stats[tit_str]["total"] += m.get("montant", 0)
        proc = (m.get("procedure") or "").lower()
        if "sans publicité" in proc or "négocié sans" in proc:
            titulaire_stats[tit_str]["sans_concurrence"] += 1
        cpv = str(m.get("codecpv", ""))[:2]
        titulaire_stats[tit_str]["categories"].add(cpv)

# Get top titulaires by total amount + all anomaly titulaires
top_sirets = set()

# Top 50 by amount
for siret, s in sorted(titulaire_stats.items(), key=lambda x: -x[1]["total"])[:50]:
    top_sirets.add(siret)

# All anomaly titulaires
for a in anomalies_cots:
    tit = a.get("titulaire_siret")
    if tit:
        tit_str = str(int(tit)) if isinstance(tit, float) else str(tit)
        top_sirets.add(tit_str)

print(f"SIRETs uniques a enrichir: {len(top_sirets)}")

# Query API Sirene (free, no auth needed for basic info)
# Use annuaire-entreprises.data.gouv.fr API
enriched = {}
errors = 0

for i, siret in enumerate(list(top_sirets)[:80]):  # Limit to 80 queries
    # Extract SIREN (first 9 digits)
    siren = siret[:9] if len(siret) >= 9 else siret
    
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siren}&page=1&per_page=1"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            if results:
                r = results[0]
                siege = r.get("siege", {})
                enriched[siret] = {
                    "siren": r.get("siren"),
                    "siret": siret,
                    "nom": r.get("nom_complet", ""),
                    "nature_juridique": r.get("nature_juridique", ""),
                    "activite_principale": siege.get("activite_principale", ""),
                    "libelle_activite": siege.get("libelle_activite_principale", ""),
                    "tranche_effectifs": r.get("tranche_effectif_salarie", ""),
                    "date_creation": r.get("date_creation", ""),
                    "adresse": siege.get("adresse", ""),
                    "commune": siege.get("libelle_commune", ""),
                    "departement": siege.get("departement", ""),
                    "nombre_etablissements": r.get("nombre_etablissements", 0),
                    "est_association": r.get("complements", {}).get("est_association", False),
                    "est_ess": r.get("complements", {}).get("est_ess", False),
                }
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  Error for {siret}: {e}")
    
    if (i + 1) % 20 == 0:
        print(f"  Enriched {i+1}/{len(top_sirets)}...")
        time.sleep(1)

print(f"\nEnriched: {len(enriched)} / {len(top_sirets)} (errors: {errors})")

# Build scoring model
print(f"\n{'='*90}")
print("SCORING DES MARCHES - FACILITE DE SOUS-ENCHERE")
print(f"{'='*90}")

scored_markets = []

for m in all_marches:
    montant = m.get("montant", 0)
    if montant <= 0:
        continue
    
    tit = m.get("titulaire_id_1")
    tit_str = str(int(tit)) if isinstance(tit, (float, int)) and tit else str(tit) if tit else ""
    proc = (m.get("procedure") or "").lower()
    offres = m.get("offresrecues")
    cpv = str(m.get("codecpv", ""))[:2]
    
    # Calculate undercut score (0-100)
    score = 50  # Base score
    reasons = []
    
    # Factor 1: Competition level
    if "sans publicité" in proc or "négocié sans" in proc:
        score += 15
        reasons.append("Sans concurrence (+15)")
    if offres and offres == 1:
        score += 15
        reasons.append("1 seule offre (+15)")
    elif offres and offres <= 2:
        score += 8
        reasons.append(f"{int(offres)} offres (+8)")
    elif offres and offres >= 5:
        score -= 10
        reasons.append(f"{int(offres)} offres (-10)")
    
    # Factor 2: Supplier concentration
    tit_info = titulaire_stats.get(tit_str, {})
    if tit_info.get("count", 0) >= 10:
        score += 5
        reasons.append(f"Fournisseur captif {tit_info['count']} marches (+5)")
    if tit_info.get("sans_concurrence", 0) >= 3:
        score += 10
        reasons.append(f"{tit_info['sans_concurrence']} marches sans concurrence (+10)")
    
    # Factor 3: Category comparability (COTS-friendly categories score higher)
    cots_categories = {"30", "31", "32", "33", "34", "39", "44", "48", "18", "22", "38", "35"}
    if cpv in cots_categories:
        score += 5
        reasons.append("Categorie COTS (+5)")
    
    # Factor 4: Amount sweet spot (not too small to bother, not too large to be complex)
    if 50000 <= montant <= 5000000:
        score += 5
        reasons.append("Montant accessible (+5)")
    elif montant < 50000:
        score -= 10
        reasons.append("Montant trop faible (-10)")
    elif montant > 20000000:
        score -= 5
        reasons.append("Montant tres eleve (-5)")
    
    # Factor 5: Enriched company info
    company = enriched.get(tit_str, {})
    if company:
        # Small company with big contract = potential vulnerability
        effectifs = company.get("tranche_effectifs", "")
        if effectifs and effectifs in ["0", "1", "2", "3", "5"]:  # < 50 employees
            score += 5
            reasons.append("Petite entreprise (+5)")
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Estimate potential savings (conservative: 20-40% undercut)
    if score >= 60:
        savings_low = montant * 0.15
        savings_high = montant * 0.35
    elif score >= 50:
        savings_low = montant * 0.10
        savings_high = montant * 0.25
    else:
        savings_low = 0
        savings_high = montant * 0.10
    
    scored_markets.append({
        "id": m.get("id"),
        "objet": (m.get("objet") or "")[:150],
        "montant": montant,
        "codecpv": m.get("codecpv"),
        "procedure": (m.get("procedure") or "")[:60],
        "offres_recues": offres,
        "acheteur_id": m.get("acheteur_id"),
        "acheteur_nom": m.get("acheteur_nom"),
        "titulaire_siret": tit_str,
        "titulaire_nom": company.get("nom", ""),
        "titulaire_activite": company.get("libelle_activite", ""),
        "titulaire_effectifs": company.get("tranche_effectifs", ""),
        "titulaire_commune": company.get("commune", ""),
        "date": m.get("datenotification"),
        "score_sous_enchere": score,
        "raisons_score": " | ".join(reasons),
        "economie_estimee_basse": round(savings_low),
        "economie_estimee_haute": round(savings_high),
    })

# Sort by score
scored_markets.sort(key=lambda x: (-x["score_sous_enchere"], -x["montant"]))

# Stats
high_score = [s for s in scored_markets if s["score_sous_enchere"] >= 70]
medium_score = [s for s in scored_markets if 60 <= s["score_sous_enchere"] < 70]

print(f"\nMarches scores: {len(scored_markets)}")
print(f"Score >= 70 (haute opportunite): {len(high_score)} marches")
print(f"  Montant total: {sum(s['montant'] for s in high_score):,.0f} EUR")
print(f"  Economie estimee: {sum(s['economie_estimee_basse'] for s in high_score):,.0f} - {sum(s['economie_estimee_haute'] for s in high_score):,.0f} EUR")
print(f"Score 60-69 (opportunite moyenne): {len(medium_score)} marches")
print(f"  Montant total: {sum(s['montant'] for s in medium_score):,.0f} EUR")

print(f"\nTOP 25 opportunites de sous-enchere:")
for i, s in enumerate(scored_markets[:25], 1):
    print(f"  {i:2d}. [Score {s['score_sous_enchere']:3d}] {s['montant']:>14,.0f} EUR | Eco: {s['economie_estimee_basse']:>10,.0f}-{s['economie_estimee_haute']:>10,.0f}")
    print(f"      {s['objet'][:100]}")
    print(f"      Titulaire: {s['titulaire_nom'][:60]} | {s['raisons_score'][:80]}")

# Save enriched company data
with open("/workspace/data/fournisseurs_enrichis.json", "w", encoding="utf-8") as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

# Save scored markets
with open("/workspace/data/scored_markets.json", "w", encoding="utf-8") as f:
    json.dump(scored_markets, f, ensure_ascii=False, indent=2)

# CSV exports
with open("/workspace/output/marches_scores.csv", "w", encoding="utf-8", newline="") as f:
    if scored_markets:
        writer = csv.DictWriter(f, fieldnames=scored_markets[0].keys())
        writer.writeheader()
        writer.writerows(scored_markets)

# Top 50 opportunities CSV
top50 = scored_markets[:50]
with open("/workspace/output/top50_opportunites.csv", "w", encoding="utf-8", newline="") as f:
    if top50:
        writer = csv.DictWriter(f, fieldnames=top50[0].keys())
        writer.writeheader()
        writer.writerows(top50)

# Fournisseurs enrichis CSV
fournisseurs_list = []
for siret, info in enriched.items():
    stats = titulaire_stats.get(siret, {})
    info_copy = dict(info)
    info_copy["nb_marches"] = stats.get("count", 0)
    info_copy["total_marches_eur"] = stats.get("total", 0)
    info_copy["marches_sans_concurrence"] = stats.get("sans_concurrence", 0)
    fournisseurs_list.append(info_copy)

fournisseurs_list.sort(key=lambda x: -x["total_marches_eur"])

with open("/workspace/output/fournisseurs_enrichis.csv", "w", encoding="utf-8", newline="") as f:
    if fournisseurs_list:
        writer = csv.DictWriter(f, fieldnames=fournisseurs_list[0].keys())
        writer.writeheader()
        writer.writerows(fournisseurs_list)

print(f"\n\nFichiers sauvegardes:")
print(f"  - marches_scores.csv ({len(scored_markets)} marches)")
print(f"  - top50_opportunites.csv (50 marches)")
print(f"  - fournisseurs_enrichis.csv ({len(fournisseurs_list)} fournisseurs)")

