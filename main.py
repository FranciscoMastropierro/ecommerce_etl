from pathlib import Path
import argparse
from extract import extract, FILES
from transform import validate_and_transform
from load import load_to_sqlite
from utils import save_report

DATA_DIR = Path("data")


def main(step: str):
    print(f"Iniciando ETL - paso: {step}")
    if step == "extract":
        dfs = extract(FILES)
        for k, df in dfs.items():
            out = DATA_DIR / f"{k}_snapshot.csv"
            df.to_csv(out, index=False)
            print(f"[EXTRACT] Snapshot guardado: {out}")
        return
    if step == "transform":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        save_report(report, Path("etl_report_transform.json"))
        for k, df in dfs.items():
            out = DATA_DIR / f"{k}_transformed.csv"
            df.to_csv(out, index=False)
            print(f"[TRANSFORM] Guardado: {out}")
        return
    if step == "load":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        load_to_sqlite(dfs)
        save_report(report, Path("etl_report_load.json"))
        return
    if step == "all":
        dfs = extract(FILES)
        dfs, report = validate_and_transform(dfs)
        load_to_sqlite(dfs)
        save_report(report, Path("etl_report_all.json"))
        return
    print(f"Paso desconocido: {step}. Use extract|transform|load|all")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ETL simple desde Excel a SQLite")
    parser.add_argument("--step", type=str, required=True,
                        help="Paso a ejecutar: extract|transform|load|all")
    args = parser.parse_args()
    main(args.step)
