import json
import csv

# 1. Export DECP full (10,000 markets)
print("Exporting DECP full...")
with open("/workspace/data/decp_marches_raw.json", "r", encoding="utf-8") as f:
    decp = json.load(f)

decp_fields = [
    "id", "objet", "montant", "codecpv", "procedure", "nature",
    "datenotification", "dureemois", "formeprix",
    "acheteur_id", "acheteur_nom",
    "titulaire_id_1", "titulaire_denominationsociale_2",
    "offresrecues", "lieuexecution_nom", "lieuexecution_code",
    "lieuexecution_typecode", "source"
]

with open("/workspace/output/decp_marches_10000.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=decp_fields, extrasaction="ignore")
    writer.writeheader()
    for r in decp:
        writer.writerow(r)
print(f"  -> decp_marches_10000.csv ({len(decp)} lignes)")

# 2. Copy filtered COTS fournitures CSV
import shutil
shutil.copy("/workspace/data/decp_fournitures_cots.csv", "/workspace/output/decp_fournitures_cots.csv")
print(f"  -> decp_fournitures_cots.csv (2,293 lignes)")

# 3. Export BOAMP attributions
print("Exporting BOAMP attributions...")
with open("/workspace/data/boamp_attributions.json", "r", encoding="utf-8") as f:
    boamp = json.load(f)

boamp_fields = [
    "id", "objet", "famille", "type_marche", "type_avis",
    "procedure", "acheteur", "titulaire", "departement",
    "date_parution", "url_avis"
]

with open("/workspace/output/boamp_attributions.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=boamp_fields, extrasaction="ignore")
    writer.writeheader()
    for r in boamp:
        row = dict(r)
        # Flatten list fields to string
        for k, v in row.items():
            if isinstance(v, list):
                row[k] = " | ".join(str(x) for x in v)
        writer.writerow(row)
print(f"  -> boamp_attributions.csv ({len(boamp)} lignes)")

# 4. Export full BOAMP raw as CSV
print("Exporting BOAMP full...")
with open("/workspace/data/boamp_avis_raw.json", "r", encoding="utf-8") as f:
    boamp_full = json.load(f)

boamp_full_fields = [
    "id", "idweb", "objet", "famille_libelle", "type_marche",
    "nature_categorise_libelle", "procedure_libelle",
    "nomacheteur", "titulaire", "code_departement",
    "code_departement_prestation", "dateparution",
    "datelimitereponse", "datefindiffusion",
    "type_avis", "url_avis"
]

with open("/workspace/output/boamp_avis_3000.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=boamp_full_fields, extrasaction="ignore")
    writer.writeheader()
    for r in boamp_full:
        row = dict(r)
        for k, v in row.items():
            if isinstance(v, list):
                row[k] = " | ".join(str(x) for x in v)
        writer.writerow(row)
print(f"  -> boamp_avis_3000.csv ({len(boamp_full)} lignes)")

print("\nDone. All CSV files in /workspace/output/")
