from pathlib import Path


def save_report(report: dict, path: Path = Path("etl_report.txt")):
    with open(path, "w", encoding="utf-8") as f:
        f.write("ETL REPORT\n")
        import json
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[REPORT] Guardado en {path}")
