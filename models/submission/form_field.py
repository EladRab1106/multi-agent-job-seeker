from pydantic import BaseModel
from .form_field_type import FormFieldType
from typing import Optional

class FormField(BaseModel):
    field_id: str
    label: str
    type: FormFieldType
    required: bool
    mapping_hint: Optional[str] = None

