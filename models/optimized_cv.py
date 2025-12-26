from typing import List, Optional
from pydantic import BaseModel, Field

from models.cv import CV
from models.job import Job


class OptimizedCV(BaseModel):
    """
    Derived CV artifact optimized for a specific job.
    This object is created per application and is NOT persisted
    as a source of truth.
    """

    original_cv: CV
    job: Job

    tailored_summary: Optional[str] = None
    tailored_skills: List[str] = Field(default_factory=list)
    tailored_experience: Optional[str] = None

    full_text: Optional[str] = None  # final rendered CV text (for submission)
