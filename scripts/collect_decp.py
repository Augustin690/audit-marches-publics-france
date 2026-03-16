import json
import urllib.request
import urllib.parse
import time
import sys

BASE_URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/decp-v3-marches-valides/records"

# We want to collect markets focused on supplies (fournitures) that are comparable to commercial prices
# CPV codes starting with 30 (IT equipment), 31 (electrical), 32 (telecom), 33 (medical), 
# 39 (furniture), 48 (software), 22 (printed matter), 34 (transport equipment)
# These are the categories most likely to have COTS equivalents

# Strategy: download in batches of 100 (API limit), paginate with offset
# Focus on recent markets (2023-2025) with significant amounts

all_records = []
total_to_fetch = 10000  # Get a large sample
batch_size = 100

# Fields to select
fields = "id,objet,montant,codecpv,procedure,nature,datenotification,dureemois,acheteur_id,acheteur_nom,titulaire_id_1,titulaire_denominationsociale_2,formeprix,source,lieuexecution_nom,offresrecues"

print(f"Starting DECP data collection... Target: {total_to_fetch} records")
print(f"Total available in dataset: 702,918 validated markets")

for offset in range(0, total_to_fetch, batch_size):
    params = {
        "select": fields,
        "limit": batch_size,
        "offset": offset,
        "order_by": "datenotification DESC",
        "where": "montant > 1000 AND datenotification >= '2023-01-01'"
    }
    
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            records = data.get("results", [])
            all_records.extend(records)
            
            if offset % 1000 == 0:
                print(f"  Fetched {len(all_records)} records... (offset={offset})")
            
            if len(records) < batch_size:
                print(f"  No more records at offset {offset}")
                break
    except Exception as e:
        print(f"  Error at offset {offset}: {e}")
        time.sleep(2)
        continue
    
    # Small delay to be polite
    if offset % 500 == 0 and offset > 0:
        time.sleep(0.5)

print(f"\nTotal records collected: {len(all_records)}")

# Save raw data
with open("/workspace/data/decp_marches_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)

print(f"Saved to /workspace/data/decp_marches_raw.json")

# Quick stats
amounts = [r["montant"] for r in all_records if r.get("montant")]
print(f"\nQuick stats:")
print(f"  Records with amount: {len(amounts)}")
print(f"  Min amount: {min(amounts):,.2f} EUR")
print(f"  Max amount: {max(amounts):,.2f} EUR")
print(f"  Median amount: {sorted(amounts)[len(amounts)//2]:,.2f} EUR")
print(f"  Total value: {sum(amounts):,.2f} EUR")

# CPV distribution
cpv_counts = {}
for r in all_records:
    cpv = r.get("codecpv", "unknown")
    if cpv:
        prefix = cpv[:2] if len(str(cpv)) >= 2 else "unknown"
        cpv_counts[prefix] = cpv_counts.get(prefix, 0) + 1

print(f"\nTop CPV categories (first 2 digits):")
for cpv, count in sorted(cpv_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cpv}: {count} markets")

