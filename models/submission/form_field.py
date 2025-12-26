from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from models.submission.form_field_type import FormFieldType


class FormField(BaseModel):
    # Identity
    field_id: str                  # internal stable id
    label: str                     # visible label on the form

    # Field behavior
    type: FormFieldType
    required: bool = False

    # Constraints
    options: Optional[List[str]] = None      # for select/multiselect
    placeholder: Optional[str] = None
    max_length: Optional[int] = None

    # Mapping hints (LLM-facing)
    mapping_hint: Optional[str] = None        # "cv.full_name", "cv.email", etc.

    # Runtime
    value: Optional[Any] = None               # value to be filled

    # Metadata
    raw_attributes: Optional[Dict[str, Any]] = None
