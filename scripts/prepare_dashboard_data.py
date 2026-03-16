import json

# Load all data needed for dashboard
with open("/workspace/data/scored_markets.json", "r", encoding="utf-8") as f:
    scored = json.load(f)

with open("/workspace/data/fournisseurs_enrichis.json", "r", encoding="utf-8") as f:
    fournisseurs = json.load(f)

with open("/workspace/data/classification_summary.json", "r", encoding="utf-8") as f:
    classification = json.load(f)

# Prepare compact data for dashboard
# 1. Top 50 opportunities
top50 = []
for s in scored[:50]:
    top50.append({
        "o": s["objet"][:100],
        "m": s["montant"],
        "s": s["score_sous_enchere"],
        "p": s["procedure"][:40],
        "t": s["titulaire_nom"][:40] if s["titulaire_nom"] else "Non identifie",
        "r": s["raisons_score"][:100],
        "eb": s["economie_estimee_basse"],
        "eh": s["economie_estimee_haute"],
        "d": s["date"],
        "c": str(s.get("codecpv", ""))[:8],
    })

# 2. Score distribution
score_dist = {}
for s in scored:
    bucket = (s["score_sous_enchere"] // 10) * 10
    score_dist[bucket] = score_dist.get(bucket, 0) + 1

# 3. Category breakdown
cat_data = {}
for s in scored:
    cpv = str(s.get("codecpv", ""))[:2]
    if cpv not in cat_data:
        cat_data[cpv] = {"count": 0, "total": 0, "high_score": 0}
    cat_data[cpv]["count"] += 1
    cat_data[cpv]["total"] += s["montant"]
    if s["score_sous_enchere"] >= 70:
        cat_data[cpv]["high_score"] += 1

# 4. Top fournisseurs
top_fourn = []
for siret, info in sorted(fournisseurs.items(), key=lambda x: -x[1].get("nb_marches", 0) if isinstance(x[1], dict) and "nb_marches" in x[1] else 0)[:20]:
    top_fourn.append({
        "nom": info.get("nom", "")[:50],
        "siret": siret,
        "commune": info.get("commune", ""),
        "activite": info.get("libelle_activite", "")[:50],
    })

# 5. Procedure breakdown
proc_data = {}
for s in scored:
    p = s["procedure"][:40] if s["procedure"] else "Non renseigne"
    if p not in proc_data:
        proc_data[p] = {"count": 0, "total": 0}
    proc_data[p]["count"] += 1
    proc_data[p]["total"] += s["montant"]

# 6. Key stats
total_amount = sum(s["montant"] for s in scored)
high_opp = [s for s in scored if s["score_sous_enchere"] >= 70]
total_savings_low = sum(s["economie_estimee_basse"] for s in high_opp)
total_savings_high = sum(s["economie_estimee_haute"] for s in high_opp)
sans_conc = sum(1 for s in scored if "Sans concurrence" in s.get("raisons_score", ""))
fournisseur_unique = sum(1 for s in scored if "1 seule offre" in s.get("raisons_score", ""))

stats = {
    "total_marches": len(scored),
    "total_amount": total_amount,
    "high_opportunities": len(high_opp),
    "high_opp_amount": sum(s["montant"] for s in high_opp),
    "savings_low": total_savings_low,
    "savings_high": total_savings_high,
    "sans_concurrence": sans_conc,
    "fournisseur_unique": fournisseur_unique,
}

dashboard_data = {
    "stats": stats,
    "top50": top50,
    "score_distribution": score_dist,
    "categories": cat_data,
    "procedures": proc_data,
}

with open("/workspace/data/dashboard_data.json", "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, ensure_ascii=False)

print("Dashboard data prepared")
print(f"Stats: {json.dumps(stats, indent=2)}")
