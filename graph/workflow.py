from langgraph.graph import StateGraph, END

from graph.state import GraphState
from graph.nodes import (
    pop_job_node,
    optimize_cv_node,
    optimization_failed_node,
)

from graph.nodes_submission import (
    submit_start_node,
    detect_ats_node,
    extract_schema_node,
    map_fields_node,
    fill_form_node,
    validate_form_node,
    confirm_submission_node,
    submit_success_node,
    submit_failed_node,
)


def build_graph():
    graph = StateGraph(GraphState)

    # ===== Core job loop =====
    graph.add_node("POP_JOB", pop_job_node)
    graph.add_node("OPTIMIZE", optimize_cv_node)
    graph.add_node("OPT_FAILED", optimization_failed_node)

    # ===== Submission sub-graph =====
    graph.add_node("SUBMIT_START", submit_start_node)
    graph.add_node("DETECT_ATS", detect_ats_node)
    graph.add_node("EXTRACT_SCHEMA", extract_schema_node)
    graph.add_node("MAP_FIELDS", map_fields_node)
    graph.add_node("FILL_FORM", fill_form_node)
    graph.add_node("VALIDATE_FORM", validate_form_node)
    graph.add_node("CONFIRM_SUBMIT", confirm_submission_node)
    graph.add_node("SUBMIT_SUCCESS", submit_success_node)
    graph.add_node("SUBMIT_FAILED", submit_failed_node)

    # Entry point
    graph.set_entry_point("POP_JOB")

    # ===== Job existence check =====
    graph.add_conditional_edges(
        "POP_JOB",
        lambda state: "END" if state.current_job is None else "OPTIMIZE",
        {
            "OPTIMIZE": "OPTIMIZE",
            "END": END,
        },
    )

    # ===== Optimization with retries =====
    graph.add_conditional_edges(
        "OPTIMIZE",
        lambda state: (
            "SUBMIT_START"
            if state.current_optimized_cv is not None
            else "OPTIMIZE"
            if state.retry_count < state.max_retries
            else "OPT_FAILED"
        ),
        {
            "SUBMIT_START": "SUBMIT_START",
            "OPTIMIZE": "OPTIMIZE",
            "OPT_FAILED": "OPT_FAILED",
        },
    )

    # ===== Optimization failure =====
    graph.add_edge("OPT_FAILED", "POP_JOB")

    # ===== Submission sub-graph wiring =====
    graph.add_edge("SUBMIT_START", "DETECT_ATS")
    graph.add_edge("DETECT_ATS", "EXTRACT_SCHEMA")
    graph.add_edge("EXTRACT_SCHEMA", "MAP_FIELDS")
    graph.add_edge("MAP_FIELDS", "FILL_FORM")
    graph.add_edge("FILL_FORM", "VALIDATE_FORM")

    # ===== Form validation decision =====
    def _is_form_valid(state):
        """Check if all required fields have valid values."""
        schema = state.form_schema
        mapping = state.field_mapping

        if schema is None or mapping is None:
            return False

        for field in schema.fields:
            if field.required:
                value = mapping.get(field.field_id)
                if value is None or value == "" or value == []:
                    return False

        return True

    graph.add_conditional_edges(
        "VALIDATE_FORM",
        lambda state: (
            "CONFIRM_SUBMIT"
            if _is_form_valid(state)
            else "MAP_FIELDS"
            if state.submission_attempts < state.max_submission_attempts
            else "SUBMIT_FAILED"
        ),
        {
            "CONFIRM_SUBMIT": "CONFIRM_SUBMIT",
            "MAP_FIELDS": "MAP_FIELDS",
            "SUBMIT_FAILED": "SUBMIT_FAILED",
        },
    )

    # ===== Submission decision =====
    graph.add_conditional_edges(
        "CONFIRM_SUBMIT",
        lambda state: (
            "SUBMIT_SUCCESS"
            if state.submission_attempts <= state.max_submission_attempts
            else "SUBMIT_FAILED"
        ),
        {
            "SUBMIT_SUCCESS": "SUBMIT_SUCCESS",
            "SUBMIT_FAILED": "SUBMIT_FAILED",
        },
    )



    # ===== Loop back =====
    graph.add_edge("SUBMIT_SUCCESS", "POP_JOB")
    graph.add_edge("SUBMIT_FAILED", "POP_JOB")

    return graph.compile()
