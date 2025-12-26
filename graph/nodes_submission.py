import logging
from graph.state import GraphState
from models.submission.form_schema import SubmissionFormSchema
from models.submission.form_field import FormField
from models.submission.form_field_type import FormFieldType


logger = logging.getLogger(__name__)

def _resolve_mapping_hint(state: GraphState, hint: str):
    """
    Resolve mapping hints like:
    - cv.full_name
    - optimized_cv.cover_letter
    """

    if hint.startswith("cv."):
        return getattr(state.cv, hint.replace("cv.", ""), None)

    if hint.startswith("optimized_cv."):
        if state.current_optimized_cv is None:
            return None
        return getattr(
            state.current_optimized_cv,
            hint.replace("optimized_cv.", ""),
            None,
        )

    return None



def submit_start_node(state: GraphState) -> GraphState:
    logger.info(
        "Submission started | title=%s | company=%s",
        state.current_job.title,
        state.current_job.company,
    )
    state.submission_attempts = 0
    return state


def detect_ats_node(state: GraphState) -> GraphState:
    logger.info("Detecting ATS (stub)")
    state.ats_type = "unknown"  # placeholder
    return state


def extract_schema_node(state: GraphState) -> GraphState:
    """
    Extract the submission form schema.

    Deterministic stub for now.
    Will later be replaced by DOM parsing / LLM inference.
    """

    job = state.current_job
    assert job is not None, "extract_schema_node called without current_job"

    logger.info(
        "Extracting form schema | title=%s | company=%s | ats=%s",
        job.title,
        job.company,
        state.ats_type,
    )

    schema = SubmissionFormSchema(
        ats_type=state.ats_type,
        form_url=getattr(job, "apply_url", None),
        fields=[
            FormField(
                field_id="full_name",
                label="Full Name",
                type=FormFieldType.TEXT,
                required=True,
                mapping_hint="cv.full_name",
            ),
            FormField(
                field_id="email",
                label="Email",
                type=FormFieldType.EMAIL,
                required=True,
                mapping_hint="cv.email",
            ),
            FormField(
                field_id="resume",
                label="Resume",
                type=FormFieldType.FILE_UPLOAD,
                required=True,
                mapping_hint="optimized_cv.file",
            ),
            FormField(
                field_id="cover_letter",
                label="Cover Letter",
                type=FormFieldType.TEXTAREA,
                required=False,
                mapping_hint="optimized_cv.cover_letter",
            ),
        ],
    )

    state.form_schema = schema
    return state



def map_fields_node(state: GraphState) -> GraphState:
    """
    Map CV + optimized CV to submission form fields.

    Deterministic, schema-driven mapping.
    """

    schema = state.form_schema
    assert schema is not None, "map_fields_node called without form_schema"

    logger.info(
        "Mapping CV to fields | fields=%d",
        len(schema.fields),
    )

    field_mapping = {}

    for field in schema.fields:
        value = None

        if field.mapping_hint:
            value = _resolve_mapping_hint(state, field.mapping_hint)

        field_mapping[field.field_id] = value

        logger.debug(
            "Mapped field | id=%s | value=%s",
            field.field_id,
            "SET" if value is not None else "MISSING",
        )

    state.field_mapping = field_mapping
    return state



def fill_form_node(state: GraphState) -> GraphState:
    logger.info("Filling form (stub)")
    return state


def validate_form_node(state: GraphState) -> GraphState:
    """
    Validate that all required fields have values.

    Deterministic validation:
    - Required fields must be present and non-empty
    """

    schema = state.form_schema
    mapping = state.field_mapping

    assert schema is not None, "validate_form_node called without form_schema"
    assert mapping is not None, "validate_form_node called without field_mapping"

    missing_fields = []

    for field in schema.fields:
        if not field.required:
            continue

        value = mapping.get(field.field_id)

        if value is None or value == "" or value == []:
            missing_fields.append(field.field_id)

    if missing_fields:
        logger.warning(
            "Form validation failed | missing_fields=%s | attempt=%d",
            missing_fields,
            state.submission_attempts + 1,
        )

        state.submission_attempts += 1

        # Let graph routing decide retry vs fail
        return state

    logger.info("Form validation successful")
    return state



def confirm_submission_node(state: GraphState) -> GraphState:
    logger.info("Confirming submission (stub)")
    state.submission_attempts += 1
    return state


def submit_success_node(state: GraphState) -> GraphState:
    logger.info(
        "Submission success | title=%s | company=%s",
        state.current_job.title,
        state.current_job.company,
    )

    state.result_store.record_success(
        state.current_job.company,
        state.current_job.title,
    )

    state.current_job = None
    state.current_optimized_cv = None
    return state


def submit_failed_node(state: GraphState) -> GraphState:
    logger.error(
        "Submission failed | title=%s | company=%s",
        state.current_job.title,
        state.current_job.company,
    )

    state.result_store.record_failure(
        state.current_job.company,
        state.current_job.title,
        "Submission failed",
    )

    state.current_job = None
    state.current_optimized_cv = None
    return state
