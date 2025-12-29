from langgraph.graph import StateGraph, END
from graph.state import GraphState

from graph.nodes_submission import (
    submit_start_node,
    detect_ats_node,
    extract_schema_node,
    map_fields_node,
    fill_form_node,
)

def build_submission_graph():
    g = StateGraph(GraphState)

    g.add_node("SUBMIT_START", submit_start_node)
    g.add_node("DETECT_ATS", detect_ats_node)
    g.add_node("EXTRACT_SCHEMA", extract_schema_node)
    g.add_node("MAP_FIELDS", map_fields_node)
    g.add_node("FILL_FORM", fill_form_node)

    g.set_entry_point("SUBMIT_START")

    g.add_edge("SUBMIT_START", "DETECT_ATS")
    g.add_edge("DETECT_ATS", "EXTRACT_SCHEMA")
    g.add_edge("EXTRACT_SCHEMA", "MAP_FIELDS")
    g.add_edge("MAP_FIELDS", "FILL_FORM")
    g.add_edge("FILL_FORM", END)

    return g.compile()
