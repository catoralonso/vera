"""
Indexa experiencias y preguntas de rinoplastia en JSONs ligeros.
Solo guarda: título, resumen, URL, ciudad, fecha, likes.

Uso:
    python scripts/index_content.py

Output:
    data/index_experiencias.json
    data/index_preguntas.json
"""

import json
from pathlib import Path

BASE = Path.home() / "Mi unidad/E. ESTUDIOS/6. DATA SCIENCE/GIT PROJECTS/vera"
EXP_DIR   = BASE / "raw" / "experiences"
QUEST_DIR = BASE / "raw" / "questions"
OUT_EXP   = BASE / "data" / "index_experiencias.json"
OUT_QUEST = BASE / "data" / "index_preguntas.json"


def clean(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    return text.strip().replace("\n", " ")[:max_len]


def index_experiences():
    files = list(EXP_DIR.glob("*.json"))
    print(f"Experiencias encontradas: {len(files)}")
    items = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fp:
                d = json.load(fp)
            items.append({
                "title":   d.get("title", ""),
                "url":     d.get("url", ""),
                "resume":  clean(d.get("resume") or d.get("text", ""), 200),
                "city":    d.get("city") or d.get("patient", {}).get("city", ""),
                "date":    d.get("date", ""),
                "likes":   d.get("likes", 0) or 0,
            })
        except Exception as e:
            print(f"  Error en {f.name}: {e}")

    # Ordenar por likes descendente
    items.sort(key=lambda x: x["likes"], reverse=True)
    print(f"  → {len(items)} experiencias indexadas")
    return items


def index_questions():
    files = list(QUEST_DIR.glob("*.json"))
    print(f"Preguntas encontradas: {len(files)}")
    items = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fp:
                d = json.load(fp)
            # Extraer texto de structured_data si existe
            question_text = ""
            for sd in d.get("structured_data", []):
                me = sd.get("mainEntity", {})
                if me.get("@type") == "Question":
                    question_text = me.get("text", "")
                    break

            items.append({
                "title":   d.get("slug", "").replace("-", " ").title(),
                "url":     d.get("url", ""),
                "resume":  clean(question_text or d.get("slug", ""), 200),
                "answers": 0,
            })
        except Exception as e:
            print(f"  Error en {f.name}: {e}")

    print(f"  → {len(items)} preguntas indexadas")
    return items


def search_index(query: str, items: list, top_k: int = 3) -> list:
    """Búsqueda por keywords — para usar en rag.py"""
    query_lower = query.lower()
    words = [w for w in query_lower.split() if len(w) > 3]
    scored = []
    for item in items:
        text = (item.get("title", "") + " " + item.get("resume", "")).lower()
        score = sum(1 for w in words if w in text)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def main():
    OUT_EXP.parent.mkdir(exist_ok=True)

    experiences = index_experiences()
    with open(OUT_EXP, "w", encoding="utf-8") as f:
        json.dump(experiences, f, ensure_ascii=False, indent=2)
    print(f"Guardado: {OUT_EXP} ({OUT_EXP.stat().st_size // 1024} KB)\n")

    questions = index_questions()
    with open(OUT_QUEST, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Guardado: {OUT_QUEST} ({OUT_QUEST.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()