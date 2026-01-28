import csv, json, re
from pathlib import Path

SRC = Path("source")
OUT = Path("public-data")
OUT.mkdir(exist_ok=True)

def pick_latest_season_dir():
    candidates = []
    for p in SRC.rglob("*"):
        if p.is_dir() and re.search(r"\d{4}-\d{2}$", p.name):
            candidates.append(p)

    def key(p):
        m = re.search(r"(\d{4})-(\d{2})", p.name)
        return int(m.group(1)) if m else -1

    return sorted(candidates, key=key)[-1] if candidates else None

def read_largest_csv(folder: Path):
    csv_files = sorted(folder.rglob("*.csv"), key=lambda p: p.stat().st_size, reverse=True)
    if not csv_files:
        return {"file": None, "rows": []}
    f = csv_files[0]
    rows = []
    with f.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return {"file": str(f), "rows": rows}

season_dir = pick_latest_season_dir()
if not season_dir:
    raise SystemExit("No se encontró carpeta de temporada en el dataset.")

data = read_largest_csv(season_dir)

payload = {
    "season_dir": str(season_dir),
    "source_csv": data["file"],
    "matches": data["rows"],
}

with (OUT / "espana_latest.json").open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)
