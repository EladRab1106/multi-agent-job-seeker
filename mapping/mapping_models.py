from typing import List
from pydantic import BaseModel
from models.submission.form_schema import SubmissionFormSchema


class MappedField(BaseModel):
    field_id: str
    value: str


class FieldMappingResult(BaseModel):
    schema: SubmissionFormSchema
    mapped_fields: List[MappedField]
    missing_required_fields: List[str]
