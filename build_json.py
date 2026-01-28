import csv
import json
import re
from pathlib import Path

# El workflow clona el dataset aquí:
SRC = Path("source")

# Aquí guardamos el JSON final (y el workflow hace git add public-data/*.json):
OUT = Path("public-data")
OUT.mkdir(exist_ok=True)

def pick_latest_season_dir():
    """
    Busca carpetas tipo '2024-25', '2023-24', etc. y elige la más reciente.
    """
    candidates = []
    for p in SRC.rglob("*"):
        if p.is_dir() and re.search(r"\d{4}-\d{2}$", p.name):
            candidates.append(p)

    def key(p):
        m = re.search(r"(\d{4})-(\d{2})", p.name)
        return int(m.group(1)) if m else -1

    return sorted(candidates, key=key)[-1] if candidates else None

def read_best_csv(folder: Path):
    """
    Carga un CSV razonable de la temporada.
    Preferimos ficheros cuyo nombre parezca de partidos/resultados.
    Si no hay, elegimos el más grande como fallback.
    """
    csv_files = list(folder.rglob("*.csv"))
    if not csv_files:
        return {"file": None, "rows": []}

    # Preferir nombres típicos si existen
    preferred = [
        p for p in csv_files
        if re.search(r"(match|matches|result|results|games|fixtures)", p.name, re.I)
    ]

    target = preferred[0] if preferred else max(csv_files, key=lambda p: p.stat().st_size)

    rows = []
    with target.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)

    return {"file": str(target), "rows": rows}

def main():
    season_dir = pick_latest_season_dir()
    if not season_dir:
        raise SystemExit("No se encontró carpeta de temporada en el dataset (source).")

    data = read_best_csv(season_dir)

    payload = {
        "season_dir": str(season_dir),
        "source_csv": data["file"],
        "matches": data["rows"],
    }

    out_file = OUT / "espana_latest.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    print(f"OK: generado {out_file} con {len(payload['matches'])} filas")

if __name__ == "__main__":
    main()
