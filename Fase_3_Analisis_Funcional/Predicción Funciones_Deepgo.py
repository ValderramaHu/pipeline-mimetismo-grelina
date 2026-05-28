import requests
import json
import time
import csv
import re
from functools import lru_cache
from pathlib import Path
from collections import defaultdict, Counter

# ===========================
# CONFIG
# ===========================
DEEPGO_URL = "https://deepgo.cbrc.kaust.edu.sa/deepgo/api/create"
QUICKGO_BASE = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/"
UNIPROT_FASTA_ENDPOINT = "https://rest.uniprot.org/uniprotkb/{}.fasta"

# Carpeta destino
OUT_DIR = Path("/Users/hugoadrianjuarezvalderrama/Desktop/Codigos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================
# TRADUCCIONES LOCALES (diccionario)
# ===========================
PHRASE_TRANSLATIONS = {
    "cellular anatomical structure": "estructura anatómica celular",
    "intracellular anatomical structure": "estructura anatómica intracelular",
    "cytoplasm": "citoplasma",
    "binding": "unión",
    "catalytic activity": "actividad catalítica",
    "transferase activity": "actividad transferasa",
    "catalytic activity, acting on a protein": "actividad catalítica sobre proteínas",
    "protein-containing complex": "complejo que contiene proteínas",
    "catalytic complex": "complejo catalítico",
    "transferase complex": "complejo transferasa",
    "nucleotide-activated protein kinase complex": "complejo quinasa activado por nucleótido",
    "protein kinase complex": "complejo quinasa de proteínas",
    "membrane-enclosed lumen": "lumen encierrado por membrana",
    "organelle lumen": "lumen del orgánulo",
    "cellular process": "proceso celular",
    "metabolic process": "proceso metabólico",
    "developmental process": "proceso de desarrollo",  # corrección solicitada
    "biological regulation": "regulación biológica",
    "regulation of biological process": "regulación de procesos biológicos",
    "regulation of cellular process": "regulación del proceso celular",
    "response to stimulus": "respuesta a un estímulo",
    "cellular response to stimulus": "respuesta celular a un estímulo",
    "membrane": "membrana",
    "organelle": "orgánulo",
    "intracellular organelle": "orgánulo intracelular",
    "membrane-bounded organelle": "orgánulo delimitado por membrana",
    "intracellular membrane-bounded organelle": "orgánulo intracelular delimitado por membrana",
    "cytosol": "citosol",
    "nucleus": "núcleo",
    "transferase complex, transferring phosphorus-containing groups": "complejo transferasa que transfiere grupos con fósforo",
    "extracellular region": "región extracelular",
    "integral component of membrane": "componente integral de membrana",
    # correcciones específicas
    "structural molecule activity": "actividad de molécula estructural",
    "structural constituent of ribosome": "constituyente estructural del ribosoma",
}

TOKEN_TRANSLATIONS = {
    "cellular": "celular", "cell": "célula", "anatomical": "anatómica", "structure": "estructura",
    "intracellular": "intracelular", "cytoplasm": "citoplasma", "binding": "unión",
    "activity": "actividad", "catalytic": "catalítica", "transferase": "transferasa",
    "protein": "proteína", "protein-containing": "contiene proteínas", "complex": "complejo",
    "nucleotide-activated": "activado por nucleótido", "kinase": "quinasa", "membrane": "membrana",
    "organelle": "orgánulo", "lumen": "lumen", "process": "proceso", "metabolic": "metabólico",
    "biological": "biológica", "regulation": "regulación", "response": "respuesta",
    "stimulus": "estímulo", "extracellular": "extracelular", "integral": "integral",
    "component": "componente", "transferring": "transferencia", "phosphorus-containing": "conteniendo fósforo",
    "to": "a", "acting": "que actúa", "on": "sobre", "and": "y", "structural": "estructural",
    "molecule": "molécula", "constituent": "constituyente", "of": "de", "ribosome": "ribosoma",
}

@lru_cache(maxsize=2000)
def traducir_local(texto_en):
    if not texto_en:
        return texto_en
    txt = texto_en.strip()
    key_lower = txt.lower()
    if key_lower in PHRASE_TRANSLATIONS:
        return PHRASE_TRANSLATIONS[key_lower]
    for phrase_en in sorted(PHRASE_TRANSLATIONS.keys(), key=lambda x: -len(x)):
        if phrase_en in key_lower:
            key_lower = key_lower.replace(phrase_en, PHRASE_TRANSLATIONS[phrase_en])
    parts = key_lower.split()
    translated_parts = []
    for tok in parts:
        bare = tok.strip(",;:.()[]{}")
        low = bare.lower()
        translated = TOKEN_TRANSLATIONS.get(low, bare)
        translated_parts.append(translated)
    resultado = " ".join(translated_parts)
    return resultado

# ===========================
# QuickGO: nombre oficial y ancestros (cacheado)
# ===========================
@lru_cache(maxsize=2000)
def obtener_nombre_quickgo(go_id):
    url = QUICKGO_BASE + go_id
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (Python Script)"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    try:
        data = r.json()
        results = data.get("results")
        if not results:
            return None
        return results[0].get("name")
    except Exception:
        return None

@lru_cache(maxsize=4000)
def obtener_ancestros_quickgo(go_id):
    if not go_id:
        return []
    url = QUICKGO_BASE + f"{go_id}/ancestors"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code != 200:
            return []
        data = r.json()
        res0 = data.get("results", [])
        if not res0:
            return []
        entry = res0[0]
        anc = []
        if "ancestors" in entry and isinstance(entry["ancestors"], list):
            for a in entry["ancestors"]:
                if isinstance(a, str):
                    anc.append(a)
                elif isinstance(a, dict):
                    if "id" in a:
                        anc.append(a["id"])  
                    elif "goId" in a:
                        anc.append(a["goId"])
                    elif "key" in a:
                        anc.append(a["key"])
        if go_id not in anc:
            anc.append(go_id)
        anc = [str(x).upper() for x in anc if x]
        return anc
    except Exception:
        return []

def is_descendant_of(go_id, ancestor_go):
    if not go_id or not ancestor_go:
        return False
    anc = obtener_ancestros_quickgo(go_id)
    return ancestor_go.upper() in anc

# ===========================
# UniProt FASTA
# ===========================
def fetch_fasta_from_uniprot(accession, timeout=20):
    url = UNIPROT_FASTA_ENDPOINT.format(accession)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    fasta_text = r.text.strip()
    if not fasta_text.startswith(">"):
        return None
    return fasta_text

# ===========================
# Limpiar nombre de proteína
# ===========================
def clean_protein_name(protein_info):
    if not protein_info:
        return ""
    text = protein_info.strip()
    if '|' in text:
        text = text.split('|')[-1].strip()
    text = re.sub(r'\s+OS=.*', '', text)
    text = re.sub(r'\s+OX=[^\s]+', '', text)
    text = re.sub(r'\s+GN=[^\s]+', '', text)
    text = re.sub(r'\s+PE=[^\s]+', '', text)
    text = re.sub(r'\s+SV=[^\s]+', '', text)
    text = re.sub(r'^[A-Z0-9]{4,12}_[A-Za-z0-9]{2,10}\s+', '', text)
    text = re.sub(r'^[Pp]rotein\s+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ===========================
# DeepGO call
# ===========================
def predict_deepgo_json(sequence_fasta, threshold=0.3):
    payload = {"version": "1.0.26", "data_format": "fasta", "data": sequence_fasta, "threshold": threshold}
    headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    r = requests.post(DEEPGO_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()

# ===========================
# parse term entry
# ===========================
def parse_term_entry(entry):
    if not entry or len(entry) < 3:
        return None, None, 0.0
    if isinstance(entry[0], str) and entry[0].upper().startswith("GO:"):
        go_id = entry[0]; name = entry[1]; score = float(entry[2])
    elif isinstance(entry[1], str) and entry[1].upper().startswith("GO:"):
        go_id = entry[1]; name = entry[0]; score = float(entry[2])
    else:
        go_id = entry[0]; name = entry[1]; score = float(entry[2])
    return go_id, name, score

# ===========================
# Contadores
# ===========================
def make_counter_struct():
    return defaultdict(lambda: {"count": 0, "sum_score": 0.0, "name_en": None})

def update_counters_from_prediction(pred, counters, count_top_n=1):
    # kept for backward compatibility but not used for main counters per-request
    for bloque in pred.get("functions", []):
        cat_name = bloque.get("name", "")
        entries = sorted(bloque.get("functions", []), key=lambda x: x[2], reverse=True)
        for entry in entries[:count_top_n]:
            go_id, name_en, score = parse_term_entry(entry)
            if not go_id:
                continue
            struct = counters[cat_name]
            struct[go_id]["count"] += 1
            struct[go_id]["sum_score"] += float(score)
            if not struct[go_id]["name_en"] and name_en:
                struct[go_id]["name_en"] = name_en

# Nuevo: actualizar contadores sólo con los términos seleccionados (uno por categoría)
def update_counters_with_selected(counters, category_name, go_id, name_en, score):
    if not go_id:
        return
    struct = counters.get(category_name)
    if struct is None:
        return
    struct[go_id]["count"] += 1
    struct[go_id]["sum_score"] += float(score if score is not None else 0.0)
    if not struct[go_id]["name_en"] and name_en:
        struct[go_id]["name_en"] = name_en

# ===========================
# Extraer TOP-K por categoría
# ===========================
def extract_topk_from_prediction(prediction, k=3):
    out = {"protein_info": prediction.get("protein_info", ""), "length": len(prediction.get("sequence", "")),
           "CC": [], "MF": [], "BP": []}
    for bloque in prediction.get("functions", []):
        cat = bloque.get("name", "")
        entries = sorted(bloque.get("functions", []), key=lambda x: x[2], reverse=True)
        topk = []
        for entry in entries[:k]:
            go_id, name_en, score = parse_term_entry(entry)
            if not go_id:
                continue
            topk.append((name_en, go_id, float(score)))
        if cat.lower().startswith("cellular"):
            out["CC"] = topk
        elif cat.lower().startswith("molecular"):
            out["MF"] = topk
        elif cat.lower().startswith("biological"):
            out["BP"] = topk
    return out

# ===========================
# Heurísticas y evaluate_coherence_multi (igual que antes)
# ===========================
MF_KEYWORD_MAP = {
    "kinase": {"bp": ["signal", "regulation", "phosphor", "metabol"], "cc": ["cytoplasm", "membran", "nucleus", "membrane", "complex"]},
    "transferase": {"bp": ["metabol", "biosynthe", "transfer"], "cc": ["cytoplasm", "membran", "membrane"]},
    "hydrolase": {"bp": ["catabol", "metabol"], "cc": ["lysosom", "cytoplasm", "membrane"]},
    "oxidoreductase": {"bp": ["metabol", "oxidat", "redox"], "cc": ["mitochondr", "cytoplasm"]},
    "binding": {"bp": ["regulation", "transport", "translation", "replicat", "metabol"], "cc": ["nucleus", "cytoplasm", "membran", "ribosom"]},
    "structural": {"bp": ["translation", "assembly", "structure"], "cc": ["ribosom", "cytoskelet", "extracellular"]},
    "transporter": {"bp": ["transport"], "cc": ["membran", "plasma membrane", "extracellular", "vesicle"]},
    "motor": {"bp": ["transport", "movement"], "cc": ["cytoskelet", "axoneme", "cilium"]},
    "enzyme": {"bp": ["metabol", "biosynthe"], "cc": ["cytoplasm", "mitochondr", "peroxisom"]},
}

def contains_any(token_list, text):
    if not text:
        return False
    text_l = text.lower()
    return any(tok in text_l for tok in token_list)

# GO constants
CATALYTIC_GO = "GO:0003824"
STRUCTURAL_GO = "GO:0005198"
BINDING_GO = "GO:0005488"


def evaluate_coherence_multi(mf_items, bp_items, cc_items):
    points = 0.0
    reasons = []

    mf_names = [t[0] for t in mf_items if t and t[0]]
    mf_gos = [t[1] for t in mf_items if t and t[1]]
    bp_names = [t[0] for t in bp_items if t and t[0]]
    bp_gos = [t[1] for t in bp_items if t and t[1]]
    cc_names = [t[0] for t in cc_items if t and t[0]]
    cc_gos = [t[1] for t in cc_items if t and t[1]]

    try:
        for mg in mf_gos:
            if mg and is_descendant_of(mg, CATALYTIC_GO):
                reasons.append("Algún MF es actividad catalítica (por GO)")
                matched_bp = False
                for bg in bp_gos:
                    if bg and is_descendant_of(bg, "GO:0008152"):
                        points += 1.5
                        matched_bp = True
                        reasons.append("BP específico metabólico (por GO) coincide")
                        break
                if not matched_bp and any('cellular process' in (bn or '').lower() for bn in bp_names):
                    points += 0.75
                    reasons.append("BP es genérico ('cellular process') -> crédito parcial")
                for cg in cc_gos:
                    if cg and any(is_descendant_of(cg, g) for g in ["GO:0005737","GO:0005777","GO:0005886"]):
                        points += 0.5
                        reasons.append("Algún CC es localización compatible (citoplasma/mito/membrana)")
                        break

            if mg and is_descendant_of(mg, STRUCTURAL_GO):
                reasons.append("Algún MF es structural (por GO)")
                matched_bp = any((bg and is_descendant_of(bg, "GO:0006412")) for bg in bp_gos)
                if matched_bp:
                    points += 1.5
                    reasons.append("BP relacionado con traducción (por GO) -> fuerte")
                elif any('translation' in (bn or '').lower() for bn in bp_names):
                    points += 0.75
                    reasons.append("BP contiene 'translation' -> parcial")
                if any((cg and is_descendant_of(cg, "GO:0005840")) for cg in cc_gos):
                    points += 1.0
                    reasons.append("CC es ribosoma (por GO) -> fuerte")

            if mg and is_descendant_of(mg, BINDING_GO):
                reasons.append("Algún MF es binding (por GO)")
                if any((bg and is_descendant_of(bg, "GO:0050789")) for bg in bp_gos):
                    points += 1.0
                    reasons.append("BP es regulación/response (por GO)")
                if any((cg and is_descendant_of(cg, g)) for cg in cc_gos for g in ["GO:0005634","GO:0005737","GO:0005622"]):
                    points += 0.5
                    reasons.append("CC intracelular (por GO) -> parcial")
    except Exception:
        pass

    mf_text = " ".join(mf_names).lower()
    bp_text = " ".join(bp_names).lower()
    cc_text = " ".join(cc_names).lower()

    for mf_kw, expect in MF_KEYWORD_MAP.items():
        if mf_kw in mf_text:
            reasons.append(f"MF contiene '{mf_kw}' (texto)")
            if contains_any(expect["bp"], bp_text):
                points += 0.6
                reasons.append(f"Alguna BP top coincide con patrón para '{mf_kw}' (texto)")
            if contains_any(expect["cc"], cc_text):
                points += 0.6
                reasons.append(f"Alguna CC top coincide con patrón para '{mf_kw}' (texto)")

    if ("cellular process" in bp_text or "biological process" in bp_text) and contains_any(["cytoplasm","mitochondr","ribosom","membran"], cc_text):
        points += 0.5
        reasons.append("BP genérica pero CC específica -> crédito parcial")

    if contains_any(["nuclear","nucleus","dna"], mf_text) and contains_any(["extracellular","secret"], cc_text):
        points -= 1.5
        reasons.append("Incoherencia fuerte: actividad nuclear vs localización extracelular (texto)")

    if points >= 2.5:
        nivel = "ALTA"
    elif points >= 1.0:
        nivel = "MEDIA"
    else:
        nivel = "BAJA"

    reason = "; ".join(reasons) if reasons else "Sin evidencia de coherencia (términos genéricos o no relacionados)"
    return nivel, reason, round(points, 3)

# ===========================
# Selección del mejor término a partir del TOP-K (soporte entre top-k)
# (se mantiene el cálculo interno de soporte pero no se exporta como columnas)
# ===========================
def select_best_from_topk(items_en):
    if not items_en:
        return (None, None, 0.0, 0.0, "")

    total_scores = sum((t[2] for t in items_en if t and t[2]), 0.0)

    best = None
    best_support = -1.0
    best_reason = ""

    for i, (name_i, go_i, score_i) in enumerate(items_en):
        if not (name_i or go_i):
            continue
        support = float(score_i if score_i else 0.0)
        reasons = [f"base_score={score_i:.4f}"]
        for j, (name_j, go_j, score_j) in enumerate(items_en):
            if i == j:
                continue
            s_j = float(score_j if score_j else 0.0)
            added = 0.0
            if go_i and go_j:
                try:
                    if is_descendant_of(go_j, go_i) or is_descendant_of(go_i, go_j):
                        added = 0.6 * s_j
                        reasons.append(f"+{added:.3f} (related GO {go_j})")
                except Exception:
                    pass
            if added == 0.0:
                if name_i and name_j:
                    toks_i = set(re.findall(r"\w{4,}", name_i.lower()))
                    toks_j = set(re.findall(r"\w{4,}", name_j.lower()))
                    if toks_i and toks_j and (toks_i & toks_j):
                        added = 0.4 * s_j
                        reasons.append(f"+{added:.3f} (name overlap {name_j})")
            support += added
        if support > best_support:
            best_support = support
            best = (name_i, go_i, score_i)
            best_reason = "; ".join(reasons)

    if best is None:
        return (None, None, 0.0, 0.0, "")
    name_use, go_use, score_use = best
    return (name_use, go_use, float(score_use if score_use else 0.0), round(float(best_support), 4), best_reason)

# ===========================
# Extraer top1 para fila (usaremos top1 seleccionado)
# ===========================
def extract_top1_from_topk_selected(topk_dict):
    cc_items = topk_dict.get("CC", [])
    mf_items = topk_dict.get("MF", [])
    bp_items = topk_dict.get("BP", [])

    cc_selected = select_best_from_topk(cc_items)
    mf_selected = select_best_from_topk(mf_items)
    bp_selected = select_best_from_topk(bp_items)
    return cc_selected, mf_selected, bp_selected

# ===========================
# Guardar resultados (ahora con hoja de counters en el mismo Excel)
# ===========================
def save_results_table(rows, counters, filename="deepgo_uniprot_results_selected.xlsx"):
    cols = [
        "Nombre de la proteína", "ID / Accession", "Longitud (aa)",
        "Componente celular", "ID Componente celular", "Score Componente celular",
        "Función molecular", "ID Función molecular", "Score Función molecular",
        "Proceso biológico", "ID Proceso biológico", "Score Proceso biológico",
        "Coherencia", "Coherence_points", "Razon_coherencia",
        # Diagnostics (optional short top3 strings)
        "Top3_CC_summary", "Top3_MF_summary", "Top3_BP_summary",
        "Status"
    ]
    normalized = []
    for r in rows:
        nr = {c: r.get(c, "") for c in cols}
        normalized.append(nr)
    try:
        import pandas as pd
        fn = Path(filename)
        if fn.suffix.lower() != ".xlsx":
            fn = fn.with_suffix(".xlsx")
        df_main = pd.DataFrame(normalized, columns=cols)

        # build counters dataframe using only selected terms (already populated)
        counter_rows = []
        for category_name, struct in counters.items():
            for go_id, data in struct.items():
                count = data["count"]
                mean_score = data["sum_score"] / count if count > 0 else 0.0
                name_en = data["name_en"] or ""
                name_es = traducir_local(name_en) if name_en else ""
                counter_rows.append({
                    "Categoria": category_name,
                    "GO_id": go_id,
                    "Name_EN": name_en,
                    "Name_ES": name_es,
                    "Count": count,
                    "Mean_score": round(mean_score, 4)
                })
        df_counters = pd.DataFrame(counter_rows, columns=["Categoria","GO_id","Name_EN","Name_ES","Count","Mean_score"]) 

        with pd.ExcelWriter(str(fn), engine="openpyxl") as writer:
            df_main.to_excel(writer, sheet_name="Predictions", index=False)
            df_counters.to_excel(writer, sheet_name="Counters", index=False)
        return True
    except Exception:
        # Fallback: guardar main en CSV y counters en CSV
        try:
            main_csv = Path(filename).with_suffix(".csv")
            with open(main_csv, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=cols)
                writer.writeheader()
                for r in normalized:
                    writer.writerow(r)
            counters_csv = Path(filename).with_suffix("_counters.csv")
            with open(counters_csv, "w", newline="", encoding="utf-8") as fh:
                fieldnames = ["Categoria","GO_id","Name_EN","Name_ES","Count","Mean_score"]
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                writer.writeheader()
                for category_name, struct in counters.items():
                    for go_id, data in struct.items():
                        count = data["count"]
                        mean_score = data["sum_score"] / count if count > 0 else 0.0
                        name_en = data["name_en"] or ""
                        name_es = traducir_local(name_en) if name_en else ""
                        writer.writerow({"Categoria": category_name, "GO_id": go_id, "Name_EN": name_en, "Name_ES": name_es, "Count": count, "Mean_score": round(mean_score,4)})
            return True
        except Exception:
            return False

# ===========================
# Helper: format topk for short summary (not exported as main CC/MF/BP)
# ===========================
def format_topk_short(items):
    parts = []
    for name, go_id, score in items:
        if not name and not go_id:
            continue
        label = name if name else go_id
        parts.append(f"{label} ({go_id},{score:.3f})")
    return " | ".join(parts)

# ===========================
# Procesar lista de accessions -> filas + contadores + coherencia usando TOP-K pero exportar SOLO seleccionados
# ===========================
def process_accessions_to_table(accessions, pause_between_requests=1.0, count_top_n_per_protein=3):
    rows = []
    counters = {
        "Cellular Component": make_counter_struct(),
        "Molecular Function": make_counter_struct(),
        "Biological Process": make_counter_struct()
    }

    for acc in accessions:
        acc = acc.strip()
        if not acc:
            continue
        # Minimal console output: start
        print(f"Procesando ({acc}) ...")

        fasta = fetch_fasta_from_uniprot(acc)
        if fasta is None:
            # failed: append row with minimal info and print processed (failed)
            row = {
                "Nombre de la proteína": "",
                "ID / Accession": acc,
                "Longitud (aa)": "",
                "Componente celular": "", "ID Componente celular": "", "Score Componente celular": "",
                "Función molecular": "", "ID Función molecular": "", "Score Función molecular": "",
                "Proceso biológico": "", "ID Proceso biológico": "", "Score Proceso biológico": "",
                "Coherencia": "BAJA", "Coherence_points": 0.0, "Razon_coherencia": "No se pudo descargar FASTA",
                "Top3_CC_summary": "", "Top3_MF_summary": "", "Top3_BP_summary": "",
                "Status": "FAILED"
            }
            rows.append(row)
            print(f"Procesado ({acc}) ❌  - Coherencia: BAJA (puntos 0.0)")
            continue

        time.sleep(pause_between_requests)
        try:
            result = predict_deepgo_json(fasta)
        except Exception:
            row = {
                "Nombre de la proteína": "",
                "ID / Accession": acc,
                "Longitud (aa)": "",
                "Componente celular": "", "ID Componente celular": "", "Score Componente celular": "",
                "Función molecular": "", "ID Función molecular": "", "Score Función molecular": "",
                "Proceso biológico": "", "ID Proceso biológico": "", "Score Proceso biológico": "",
                "Coherencia": "BAJA", "Coherence_points": 0.0, "Razon_coherencia": "Error al llamar DeepGO",
                "Top3_CC_summary": "", "Top3_MF_summary": "", "Top3_BP_summary": "",
                "Status": "FAILED"
            }
            rows.append(row)
            print(f"Procesado ({acc}) ❌  - Coherencia: BAJA (puntos 0.0)")
            continue

        pred = result.get("predictions", [None])[0]
        if pred is None:
            row = {
                "Nombre de la proteína": "",
                "ID / Accession": acc,
                "Longitud (aa)": "",
                "Componente celular": "", "ID Componente celular": "", "Score Componente celular": "",
                "Función molecular": "", "ID Función molecular": "", "Score Función molecular": "",
                "Proceso biológico": "", "ID Proceso biológico": "", "Score Proceso biológico": "",
                "Coherencia": "BAJA", "Coherence_points": 0.0, "Razon_coherencia": "Respuesta DeepGO vacía",
                "Top3_CC_summary": "", "Top3_MF_summary": "", "Top3_BP_summary": "",
                "Status": "FAILED"
            }
            rows.append(row)
            print(f"Procesado ({acc}) ❌  - Coherencia: BAJA (puntos 0.0)")
            continue

        # extract top-k tuples
        topk = extract_topk_from_prediction(pred, k=count_top_n_per_protein)

        protein_info_raw = topk["protein_info"]
        length = topk["length"]
        clean_name = clean_protein_name(protein_info_raw)

        # prepare lists for coherence (use the topk lists), enrich names
        def enrich_names(items):
            enriched = []
            for name_en, go_id, score in items:
                name_use = name_en if name_en else ""
                if go_id:
                    qn = obtener_nombre_quickgo(go_id)
                    if qn:
                        name_use = qn
                enriched.append((name_use, go_id, score))
            return enriched

        cc_items_en = enrich_names(topk.get("CC", []))
        mf_items_en = enrich_names(topk.get("MF", []))
        bp_items_en = enrich_names(topk.get("BP", []))

        # evaluate coherence using lists
        coherencia_nivel, coherencia_reason, coherencia_points = evaluate_coherence_multi(
            mf_items_en, bp_items_en, cc_items_en
        )

        # select best candidate per category using top-k support
        cc_name_use, cc_go_use, cc_score_use, _, _ = select_best_from_topk(cc_items_en)
        mf_name_use, mf_go_use, mf_score_use, _, _ = select_best_from_topk(mf_items_en)
        bp_name_use, bp_go_use, bp_score_use, _, _ = select_best_from_topk(bp_items_en)

        # translate selected for Excel display
        cc_name_es = traducir_local(cc_name_use) if cc_name_use else ""
        mf_name_es = traducir_local(mf_name_use) if mf_name_use else ""
        bp_name_es = traducir_local(bp_name_use) if bp_name_use else ""

        # Update counters USING ONLY the selected best terms (requested change)
        update_counters_with_selected(counters, "Cellular Component", cc_go_use, cc_name_use, cc_score_use)
        update_counters_with_selected(counters, "Molecular Function", mf_go_use, mf_name_use, mf_score_use)
        update_counters_with_selected(counters, "Biological Process", bp_go_use, bp_name_use, bp_score_use)

        # short top3 summaries (for diagnostics) - not replacing the single selection
        top3_cc_short = format_topk_short(cc_items_en)
        top3_mf_short = format_topk_short(mf_items_en)
        top3_bp_short = format_topk_short(bp_items_en)

        row = {
            "Nombre de la proteína": clean_name,
            "ID / Accession": acc,
            "Longitud (aa)": length,

            "Componente celular": cc_name_es,
            "ID Componente celular": cc_go_use if cc_go_use else "",
            "Score Componente celular": round(cc_score_use, 4) if cc_score_use else "",

            "Función molecular": mf_name_es,
            "ID Función molecular": mf_go_use if mf_go_use else "",
            "Score Función molecular": round(mf_score_use, 4) if mf_score_use else "",

            "Proceso biológico": bp_name_es,
            "ID Proceso biológico": bp_go_use if bp_go_use else "",
            "Score Proceso biológico": round(bp_score_use, 4) if bp_score_use else "",

            "Coherencia": coherencia_nivel,
            "Coherence_points": coherencia_points,
            "Razon_coherencia": coherencia_reason,

            # Diagnostics (optional short top3 strings)
            "Top3_CC_summary": top3_cc_short,
            "Top3_MF_summary": top3_mf_short,
            "Top3_BP_summary": top3_bp_short,

            "Status": "OK"
        }
        rows.append(row)
        # Minimal console output: finished
        print(f"Procesado ({acc}) ✅  - Coherencia: {coherencia_nivel} (puntos {coherencia_points})")
        time.sleep(pause_between_requests)

    # save counters summary (we will include in same Excel when saving)
    return rows, counters

# ===========================
# MAIN
# ===========================
if __name__ == "__main__":
    ACCESSIONS = ["P80386"]
    try:
        with open("/Users/hugoadrianjuarezvalderrama/Desktop/Codigos/AccessionEncontrados.txt", "r", encoding="utf-8") as fh:
            file_accs = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
            if file_accs:
                ACCESSIONS = file_accs
    except FileNotFoundError:
        pass

    rows, counters = process_accessions_to_table(ACCESSIONS, pause_between_requests=1.0, count_top_n_per_protein=3)
    if rows:
        out_xlsx = OUT_DIR / "deepgo_uniprot_results_selected_top3_support.xlsx"
        save_results_table(rows, counters, filename=str(out_xlsx))


