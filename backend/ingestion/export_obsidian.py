import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.kg_store import get_all_nodes, get_all_edges, get_edges_from
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def slugify(label: str) -> str:
    return label.replace(" ", "_").replace("'", "_").replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a").replace("â", "a").replace("ô", "o").replace("û", "u").replace("î", "i").replace("ï", "i").replace("ç", "c").replace("ù", "u")


def export_obsidian(vault_path: str = None):
    if vault_path is None:
        vault_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "admin_tpe",
        )

    nodes_dir = os.path.join(vault_path, "nodes")
    edges_dir = os.path.join(vault_path, "edges")
    maps_dir = os.path.join(vault_path, "maps")

    for d in [nodes_dir, edges_dir, maps_dir]:
        os.makedirs(d, exist_ok=True)

    nodes = get_all_nodes()
    edges = get_all_edges()

    node_map = {n["node_id"]: n for n in nodes}

    for node in nodes:
        slug = slugify(node.get("label", node["node_id"]))
        filepath = os.path.join(nodes_dir, f"{slug}.md")

        outgoing = [e for e in edges if e.get("source_node_id") == node["node_id"]]
        incoming = [e for e in edges if e.get("target_node_id") == node["node_id"]]

        lines = []
        lines.append("---")
        lines.append(f"node_id: {node['node_id']}")
        lines.append(f"node_type: {node.get('node_type', '')}")
        lines.append(f"label: {node.get('label', '')}")
        lines.append("version: v1")
        lines.append("---")
        lines.append("")
        lines.append(f"# {node.get('label', node['node_id'])}")
        lines.append("")
        node_type_lower = node.get("node_type", "").lower()
        lines.append(f"Type : #{node_type_lower}")
        lines.append("")
        lines.append("## Description")
        lines.append(node.get("description", ""))
        lines.append("")

        if outgoing:
            lines.append("## Relations sortantes")
            for e in outgoing:
                target = node_map.get(e.get("target_node_id", ""))
                target_slug = slugify(target.get("label", e.get("target_node_id", ""))) if target else e.get("target_node_id", "")
                lines.append(f"- {e.get('relation_type', 'rel')} -> [[{target_slug}]]")
            lines.append("")

        if incoming:
            lines.append("## Relations entrantes")
            for e in incoming:
                source = node_map.get(e.get("source_node_id", ""))
                source_slug = slugify(source.get("label", e.get("source_node_id", ""))) if source else e.get("source_node_id", "")
                lines.append(f"- [[{source_slug}]] -> {e.get('relation_type', 'rel')}")
            lines.append("")

        tags = node.get("tags", [])
        if tags:
            lines.append("## Tags")
            lines.append(" ".join(f"#{t}" for t in tags))
            lines.append("")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    readme_path = os.path.join(vault_path, "README_GRAPH.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# AdminTPE GraphRAG — Obsidian Vault\n\n")
        f.write("Ce vault contient le Knowledge Graph administratif généré automatiquement.\n\n")
        f.write(f"**{len(nodes)} nœuds** | **{len(edges)} relations**\n\n")

    index_path = os.path.join(maps_dir, "AdminTPE_Graph_Index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# AdminTPE Graph Index\n\n")
        f.write("## Aides\n")
        for n in nodes:
            if n.get("node_type") == "Aide":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")
        f.write("\n## Autorisations\n")
        for n in nodes:
            if n.get("node_type") == "Autorisation":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")
        f.write("\n## Recours\n")
        for n in nodes:
            if n.get("node_type") == "Recours":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")
        f.write("\n## HITL\n")
        for n in nodes:
            if n.get("node_type") == "NiveauHITL":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")
        f.write("\n## Pièces justificatives\n")
        for n in nodes:
            if n.get("node_type") == "PieceJustificative":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")
        f.write("\n## Conditions\n")
        for n in nodes:
            if n.get("node_type") == "Condition":
                f.write(f"- [[{slugify(n.get('label', n['node_id']))}]]\n")

    logger.info("Exported %d nodes and %d edges to %s", len(nodes), len(edges), vault_path)
    print(f"Obsidian export complete: {len(nodes)} nodes, {len(edges)} edges -> {vault_path}")


if __name__ == "__main__":
    export_obsidian()
