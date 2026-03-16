import json
import urllib.request
import urllib.parse
import time

BASE_URL = "https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records"

all_records = []
batch_size = 100
total_to_fetch = 5000

print("Starting BOAMP data collection (avis de marches publics)...")

for offset in range(0, total_to_fetch, batch_size):
    params = {
        "limit": batch_size,
        "offset": offset,
        "order_by": "dateparution DESC",
        "where": "typeavis='Attribution' OR typeavis='Résultat de marché'"
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
                print(f"  Fetched {len(all_records)} records (total available: {total})...")
            
            if len(records) < batch_size:
                print(f"  End of data at offset {offset}")
                break
    except Exception as e:
        print(f"  Error at offset {offset}: {e}")
        # Try without filter
        if offset == 0:
            print("  Retrying without type filter...")
            params2 = {
                "limit": batch_size,
                "offset": 0,
                "order_by": "dateparution DESC",
            }
            url2 = BASE_URL + "?" + urllib.parse.urlencode(params2)
            try:
                req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req2, timeout=30) as resp2:
                    data2 = json.loads(resp2.read().decode())
                    sample = data2.get("results", [])
                    if sample:
                        print(f"  Got {len(sample)} records without filter")
                        print(f"  Sample fields: {list(sample[0].keys())[:10]}")
                        # Check what typeavis values exist
                        types = set(r.get("typeavis", "N/A") for r in sample)
                        print(f"  Available typeavis values: {types}")
            except Exception as e2:
                print(f"  Retry also failed: {e2}")
        time.sleep(2)
        continue
    
    if offset % 500 == 0 and offset > 0:
        time.sleep(0.5)

print(f"\nTotal BOAMP records collected: {len(all_records)}")

if all_records:
    with open("/workspace/data/boamp_avis_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Saved to /workspace/data/boamp_avis_raw.json")
    
    # Show sample
    print(f"\nSample record keys: {list(all_records[0].keys())}")

