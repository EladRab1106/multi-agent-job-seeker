from pydantic import BaseModel
from typing import List
from .form_field import FormField

class SubmissionFormSchema(BaseModel):
    ats_type: str        # "greenhouse"
    form_url: str
    fields: List[FormField]
