from typing import List, Optional
from pydantic import BaseModel

from models.submission.form_field import FormField


class SubmissionFormSchema(BaseModel):
    ats_type: Optional[str] = None            # greenhouse / lever / workday / custom
    form_url: Optional[str] = None

    fields: List[FormField]

    version: str = "1.0"
