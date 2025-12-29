import logging
from typing import Dict
from models.submission.form_field import FormField
from models.submission.form_schema import SubmissionFormSchema

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    return text.lower().strip()


KEYWORD_MAP = {
    "first name": ["first name", "given name"],
    "last name": ["last name", "surname", "family name"],
    "email": ["email", "e-mail"],
    "phone": ["phone", "mobile"],
    "resume": ["resume", "cv"],
    "linkedin": ["linkedin"],
    "website": ["website", "portfolio"],
}


def match_field(label: str, candidate: Dict) -> str | None:
    label_n = normalize(label)

    for target, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in label_n:
                return candidate.get(target)

    return None


def map_fields_node(state):
    """
    Input:
      state.form_schema
      state.cv  (כולל resume_path)

    Output:
      state.field_mapping = { field_id: value }
    """

    schema = state.form_schema
    cv = state.cv

    mapped = {}

    # ===== Pre-handle full name → first_name / last_name =====
    first_name = None
    last_name = None

    if cv.full_name:
        parts = cv.full_name.strip().split(" ", 1)
        first_name = parts[0]
        if len(parts) > 1:
            last_name = parts[1]

    for field in schema.fields:
        field_id = field.field_id
        label = field.label.lower()

        value = None

        # ===== Resume handling (Solution A) =====
        if field_id == "resume" or "resume" in label:
            value = cv.resume_path

            if not value:
                logger.warning(
                    "Resume field detected but cv.resume_path is empty"
                )

        # ===== First / Last name handling =====
        elif field_id == "first_name" or "first" in label:
            value = first_name

        elif field_id == "last_name" or "last" in label:
            value = last_name

        # ===== Other standard fields =====
        elif "email" in label:
            value = cv.email

        elif "location" in label:
            value = cv.location

        elif "summary" in label:
            value = cv.summary

        elif "skill" in label:
            value = ", ".join(cv.skills)

        # ===== Validation =====
        if value is None:
            if field.required:
                logger.warning(
                    f"Required field '{field.label}' could not be mapped"
                )
            else:
                logger.info(f"Skipping optional field: {field.label}")
            continue

        mapped[field_id] = value
        logger.info(f"Mapped '{field.label}' → {value}")

    state.field_mapping = mapped
    return state


