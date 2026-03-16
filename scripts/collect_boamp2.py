import json
import urllib.request
import urllib.parse
import time

BASE_URL = "https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records"

all_records = []
batch_size = 100
total_to_fetch = 3000

print("Starting BOAMP data collection (no filter)...")

for offset in range(0, total_to_fetch, batch_size):
    params = {
        "limit": batch_size,
        "offset": offset,
        "order_by": "dateparution DESC",
    }
    
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            records = data.get("results", [])
            all_records.extend(records)
            
            if offset % 500 == 0:
                total = data.get("total_count", "?")
                print(f"  Fetched {len(all_records)} / {total} (offset={offset})")
            
            if len(records) < batch_size:
                print(f"  End of data at offset {offset}")
                break
    except Exception as e:
        print(f"  Error at offset {offset}: {e}")
        time.sleep(2)
        continue

print(f"\nTotal BOAMP records collected: {len(all_records)}")

if all_records:
    with open("/workspace/data/boamp_avis_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Saved to /workspace/data/boamp_avis_raw.json")
    
    # Show all available fields
    print(f"\nAll fields: {list(all_records[0].keys())}")
    
    # Show famille distribution
    familles = {}
    for r in all_records:
        f = r.get("famille_libelle", "N/A")
        familles[f] = familles.get(f, 0) + 1
    print(f"\nFamille distribution:")
    for f, c in sorted(familles.items(), key=lambda x: -x[1])[:20]:
        print(f"  {f}: {c}")

