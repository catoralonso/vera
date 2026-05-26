"""
Consolida los JSONs de clínicas y filtra las que ofrecen rinoplastia.
Uso: python scripts/consolidar_clinicas.py

Output: data/clinicas_rinoplastia.json
"""

import json
from pathlib import Path

CLINICAS_DIR = Path.home() / "Mi unidad/E. ESTUDIOS/6. DATA SCIENCE/GIT PROJECTS/vera/raw/centros_clinicos"
OUTPUT_FILE  = Path.home() / "Mi unidad/E. ESTUDIOS/6. DATA SCIENCE/GIT PROJECTS/vera/data/clinicas_rinoplastia.json"

RINOPLASTIA_KEYWORDS = ["rinoplastia", "rinoplasty", "nariz", "corrección nasal", "septoplastia"]


def tiene_rinoplastia(clinica: dict) -> bool:
    grupos = clinica.get("treatment_groups", [])
    for grupo in grupos:
        for tratamiento in grupo.get("treatments", []):
            nombre = tratamiento.get("name", "").lower()
            if any(kw in nombre for kw in RINOPLASTIA_KEYWORDS):
                return True
    return False


def extraer_ciudad(clinica: dict) -> str:
    hqs = clinica.get("headquarters", {}).get("parsed", [])
    if hqs:
        return hqs[0].get("area2_canonical", "")
    return clinica.get("location_summary", "")


def limpiar_clinica(clinica: dict) -> dict:
    hqs = clinica.get("headquarters", {}).get("parsed", [])
    hq = hqs[0] if hqs else {}

    phones = clinica.get("phones", {}).get("numbers", [])
    phone = phones[0] if phones else None

    return {
        "name":     clinica.get("name", ""),
        "url":      clinica.get("referer", ""),
        "ciudad":   hq.get("area2_canonical", ""),
        "address":  hq.get("address", ""),
        "phone":    phone,
        "rating":   clinica.get("rating", {}).get("score"),
        "reviews":  clinica.get("rating", {}).get("reviews_count"),
        "recommendation_percent": clinica.get("rating", {}).get("recommendation_percent"),
        "logo":     clinica.get("logo", ""),
        "lat":      hq.get("latitude"),
        "lng":      hq.get("longitude"),
    }


def main():
    archivos = list(CLINICAS_DIR.glob("*.json"))
    print(f"Archivos encontrados: {len(archivos)}")

    clinicas_filtradas = []

    for archivo in archivos:
        try:
            with open(archivo, encoding="utf-8") as f:
                clinica = json.load(f)
            if tiene_rinoplastia(clinica):
                clinicas_filtradas.append(limpiar_clinica(clinica))
        except Exception as e:
            print(f"  Error en {archivo.name}: {e}")

    print(f"Clínicas con rinoplastia: {len(clinicas_filtradas)}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(clinicas_filtradas, f, ensure_ascii=False, indent=2)

    print(f"Guardado en {OUTPUT_FILE}")

    ciudades = sorted(set(c["ciudad"] for c in clinicas_filtradas if c["ciudad"]))
    print(f"\nCiudades cubiertas ({len(ciudades)}):")
    for ciudad in ciudades:
        print(f"  - {ciudad}")


if __name__ == "__main__":
    main()