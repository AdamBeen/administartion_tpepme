from langgraph.graph import StateGraph, START, END
from graph.state import AdminTPEState
from graph.nodes.receive_input import node_receive_input
from graph.nodes.validate_input import node_validate_input_basic
from graph.nodes.extract_files import node_extract_files
from graph.nodes.build_dossier_summary import node_build_temporary_dossier_summary
from graph.nodes.classify_request import node_classify_admin_request
from graph.nodes.build_vector_query import node_build_vector_query
from graph.nodes.vector_retrieve import node_vector_retrieve
from graph.nodes.build_graph_query import node_build_graph_query
from graph.nodes.graph_retrieve import node_graph_retrieve_paths
from graph.nodes.merge_contexts import node_merge_contexts
from graph.nodes.admin_analysis import node_administrative_analysis_llm
from graph.nodes.parse_json import node_parse_and_validate_json
from graph.nodes.hitl_router import node_hitl_router
from graph.nodes.clean_response import node_clean_response_for_frontend
from graph.nodes.persist_logs import node_persist_run_logs
from graph.nodes.error_handler import node_error_handler
import logging

logger = logging.getLogger(__name__)


def _has_critical_errors(state: AdminTPEState) -> str:
    errors = state.get("errors", [])
    critical_nodes = {
        "node_build_temporary_dossier_summary",
        "node_administrative_analysis_llm",
        "node_parse_and_validate_json",
    }
    for err in errors:
        if err.get("node_name") in critical_nodes and err.get("error_type") == "llm_error":
            return "error"
    return "continue"


def build_workflow():
    graph = StateGraph(AdminTPEState)

    graph.add_node("node_receive_input", node_receive_input)
    graph.add_node("node_validate_input_basic", node_validate_input_basic)
    graph.add_node("node_extract_files", node_extract_files)
    graph.add_node("node_build_temporary_dossier_summary", node_build_temporary_dossier_summary)
    graph.add_node("node_classify_admin_request", node_classify_admin_request)
    graph.add_node("node_build_vector_query", node_build_vector_query)
    graph.add_node("node_vector_retrieve", node_vector_retrieve)
    graph.add_node("node_build_graph_query", node_build_graph_query)
    graph.add_node("node_graph_retrieve_paths", node_graph_retrieve_paths)
    graph.add_node("node_merge_contexts", node_merge_contexts)
    graph.add_node("node_administrative_analysis_llm", node_administrative_analysis_llm)
    graph.add_node("node_parse_and_validate_json", node_parse_and_validate_json)
    graph.add_node("node_hitl_router", node_hitl_router)
    graph.add_node("node_clean_response_for_frontend", node_clean_response_for_frontend)
    graph.add_node("node_persist_run_logs", node_persist_run_logs)
    graph.add_node("node_error_handler", node_error_handler)

    graph.add_edge(START, "node_receive_input")
    graph.add_edge("node_receive_input", "node_validate_input_basic")
    graph.add_edge("node_validate_input_basic", "node_extract_files")
    graph.add_edge("node_extract_files", "node_build_temporary_dossier_summary")
    graph.add_conditional_edges(
        "node_build_temporary_dossier_summary",
        _has_critical_errors,
        {"continue": "node_classify_admin_request", "error": "node_error_handler"},
    )
    graph.add_edge("node_classify_admin_request", "node_build_vector_query")
    graph.add_edge("node_build_vector_query", "node_vector_retrieve")
    graph.add_edge("node_vector_retrieve", "node_build_graph_query")
    graph.add_edge("node_build_graph_query", "node_graph_retrieve_paths")
    graph.add_edge("node_graph_retrieve_paths", "node_merge_contexts")
    graph.add_edge("node_merge_contexts", "node_administrative_analysis_llm")
    graph.add_conditional_edges(
        "node_administrative_analysis_llm",
        _has_critical_errors,
        {"continue": "node_parse_and_validate_json", "error": "node_error_handler"},
    )
    graph.add_edge("node_parse_and_validate_json", "node_hitl_router")
    graph.add_edge("node_hitl_router", "node_clean_response_for_frontend")
    graph.add_edge("node_clean_response_for_frontend", "node_persist_run_logs")
    graph.add_edge("node_persist_run_logs", END)
    graph.add_edge("node_error_handler", END)

    compiled = graph.compile()
    logger.info("LangGraph workflow compiled successfully")
    return compiled


_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow
