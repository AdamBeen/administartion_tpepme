import os
import sys
import json
import hashlib
import logging
import io
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.astra_client import get_collection
from db.schema import init_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GRAPH_RAG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "contexte_graphrag",
)

GRAPH_RAG_FILES = [
    "01_cas_aides_eligibilite_tpe_pme.csv",
    "01_conditions_detaillees_aides_tpe_pme_maroc_2026.pdf",
    "01_emails_administratifs_eligibilite_2026.xlsx",
    "02_cas_autorisations_activites_pieces.csv",
    "02_conditions_autorisations_activites_commerciales_maroc_2026.pdf",
    "02_evenements_dossiers_simules_admin_2026.xlsx",
    "03_cas_recours_reclamations_decisions.csv",
    "03_conditions_recours_reclamations_chikaya_maroc_2026.pdf",
    "03_matrice_conditions_pieces_decisions_2026.xlsx",
]


def _extract_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n"
    return text.strip()


def _extract_csv(path: str) -> list[dict]:
    import pandas as pd
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def _extract_xlsx(path: str) -> dict[str, list[dict]]:
    import pandas as pd
    xls = pd.ExcelFile(path)
    sheets = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        sheets[sheet] = df.to_dict(orient="records")
    return sheets


def _slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _build_nodes_from_csv_rows(rows: list[dict], source_file: str, category: str) -> list[dict]:
    nodes = []
    now = datetime.now(timezone.utc).isoformat()
    for i, row in rows:
        label = str(row.get("label") or row.get("nom") or row.get("type_demande") or row.get("intitule") or f"{category}_{i}")
        node_id = _slugify(f"{category}_{label}_{i}")
        node = {
            "node_id": node_id,
            "node_type": category,
            "label": label,
            "description": str(row.get("description") or row.get("detail") or row.get("motif") or label),
            "tags": [category, source_file],
            "source_file": source_file,
            "source_type": "csv",
            "source_row_index": str(i),
            "raw_data": {k: str(v) for k, v in row.items() if pd_notna(v)},
            "metadata": {
                "ingested_at": now,
                "source": source_file,
                "category": category,
            },
            "created_at": now,
            "updated_at": now,
        }
        nodes.append(node)
    return nodes


def pd_notna(v):
    try:
        import pandas as pd
        return pd.notna(v)
    except Exception:
        return v is not None


def _build_nodes_from_pdf(text: str, source_file: str, category: str) -> list[dict]:
    import re
    nodes = []
    now = datetime.now(timezone.utc).isoformat()
    sections = re.split(r"\n(?=[A-Z][A-Za-z\s]{5,}:)", text)
    for i, section in enumerate(sections):
        section = section.strip()
        if len(section) < 20:
            continue
        first_line = section.split("\n")[0][:100]
        node_id = _slugify(f"{category}_pdf_{i}_{first_line}")
        node = {
            "node_id": node_id,
            "node_type": category,
            "label": first_line,
            "description": section[:500],
            "tags": [category, source_file, "pdf"],
            "source_file": source_file,
            "source_type": "pdf",
            "source_section_index": str(i),
            "raw_data": {"full_text": section[:2000]},
            "metadata": {
                "ingested_at": now,
                "source": source_file,
                "category": category,
            },
            "created_at": now,
            "updated_at": now,
        }
        nodes.append(node)
    return nodes


def _build_nodes_from_xlsx(sheets: dict[str, list[dict]], source_file: str, category: str) -> list[dict]:
    nodes = []
    now = datetime.now(timezone.utc).isoformat()
    for sheet_name, rows in sheets.items():
        for i, row in enumerate(rows):
            label = str(row.get("label") or row.get("nom") or row.get("intitule") or row.get("objet") or f"{sheet_name}_{i}")
            node_id = _slugify(f"{category}_{sheet_name}_{label}_{i}")
            node = {
                "node_id": node_id,
                "node_type": category,
                "label": label,
                "description": str(row.get("description") or row.get("detail") or row.get("contenu") or label),
                "tags": [category, source_file, sheet_name],
                "source_file": source_file,
                "source_type": "xlsx",
                "source_sheet": sheet_name,
                "source_row_index": str(i),
                "raw_data": {k: str(v) for k, v in row.items() if pd_notna(v)},
                "metadata": {
                    "ingested_at": now,
                    "source": source_file,
                    "category": category,
                    "sheet": sheet_name,
                },
                "created_at": now,
                "updated_at": now,
            }
            nodes.append(node)
    return nodes


def _build_edges_from_nodes(nodes: list[dict]) -> list[dict]:
    edges = []
    now = datetime.now(timezone.utc).isoformat()
    by_type = {}
    for n in nodes:
        t = n.get("node_type", "")
        by_type.setdefault(t, []).append(n)

    edge_id_counter = 0
    for node_type, group in by_type.items():
        for i in range(len(group) - 1):
            edge_id_counter += 1
            edges.append({
                "edge_id": f"auto_e{edge_id_counter:04d}",
                "source_node_id": group[i]["node_id"],
                "target_node_id": group[i + 1]["node_id"],
                "relation_type": "related_to",
                "description": f"Relation automatique entre {group[i]['label']} et {group[i+1]['label']}",
                "source_file": group[i].get("source_file", ""),
                "metadata": {
                    "ingested_at": now,
                    "auto_generated": True,
                },
                "created_at": now,
            })

    type_list = list(by_type.keys())
    for i in range(len(type_list) - 1):
        t1_nodes = by_type[type_list[i]]
        t2_nodes = by_type[type_list[i + 1]]
        for n1 in t1_nodes[:5]:
            for n2 in t2_nodes[:5]:
                edge_id_counter += 1
                edges.append({
                    "edge_id": f"auto_cross_e{edge_id_counter:04d}",
                    "source_node_id": n1["node_id"],
                    "target_node_id": n2["node_id"],
                    "relation_type": "cross_category_link",
                    "description": f"Lien cross-category: {n1['node_type']} -> {n2['node_type']}",
                    "source_file": "auto_generated",
                    "metadata": {
                        "ingested_at": now,
                        "auto_generated": True,
                    },
                    "created_at": now,
                })

    return edges


def ingest_graphrag():
    init_schema()

    all_nodes = []
    all_edges = []

    for filename in GRAPH_RAG_FILES:
        path = os.path.join(GRAPH_RAG_DIR, filename)
        if not os.path.isfile(path):
            logger.warning("File not found: %s", path)
            continue

        ext = os.path.splitext(filename)[1].lower()
        category = "Aide" if "01" in filename else ("Autorisation" if "02" in filename else "Recours")

        logger.info("Processing %s (category=%s, ext=%s)...", filename, category, ext)

        if ext == ".csv":
            rows = _extract_csv(path)
            nodes = _build_nodes_from_csv_rows(list(enumerate(rows)), filename, category)
        elif ext == ".pdf":
            text = _extract_pdf(path)
            nodes = _build_nodes_from_pdf(text, filename, category)
        elif ext == ".xlsx":
            sheets = _extract_xlsx(path)
            nodes = _build_nodes_from_xlsx(sheets, filename, category)
        else:
            logger.warning("Unsupported extension: %s for %s", ext, filename)
            continue

        logger.info("Built %d nodes from %s", len(nodes), filename)
        all_nodes.extend(nodes)

    logger.info("Building edges from %d nodes...", len(all_nodes))
    all_edges = _build_edges_from_nodes(all_nodes)
    logger.info("Built %d edges", len(all_edges))

    by_source_docs = [
        {
            "source_node_id": e["source_node_id"],
            "relation_type": e["relation_type"],
            "target_node_id": e["target_node_id"],
            "edge_id": e["edge_id"],
        }
        for e in all_edges
    ]
    by_target_docs = [
        {
            "target_node_id": e["target_node_id"],
            "relation_type": e["relation_type"],
            "source_node_id": e["source_node_id"],
            "edge_id": e["edge_id"],
        }
        for e in all_edges
    ]

    logger.info("Inserting %d nodes in batch...", len(all_nodes))
    nodes_col = get_collection("kg_nodes")
    nodes_col.delete_many({})
    if all_nodes:
        nodes_col.insert_many(all_nodes)

    logger.info("Inserting %d edges in batch...", len(all_edges))
    edges_col = get_collection("kg_edges")
    edges_col.delete_many({})
    if all_edges:
        edges_col.insert_many(all_edges)

    by_source_col = get_collection("kg_edges_by_source")
    by_source_col.delete_many({})
    if by_source_docs:
        by_source_col.insert_many(by_source_docs)

    by_target_col = get_collection("kg_edges_by_target")
    by_target_col.delete_many({})
    if by_target_docs:
        by_target_col.insert_many(by_target_docs)

    print(f"GraphRAG ingestion complete: {len(all_nodes)} nodes, {len(all_edges)} edges (from user files).")


if __name__ == "__main__":
    ingest_graphrag()
