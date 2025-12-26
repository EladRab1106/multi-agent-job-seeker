from typing import List, Optional
from pydantic import BaseModel, Field


class Job(BaseModel):
    """
    Immutable representation of a job position.
    Used for matching, CV optimization, and submission.
    """

    id: Optional[str] = None  # platform-specific job ID
    title: str
    company: str

    location: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, part-time, etc.

    required_skills: List[str] = Field(default_factory=list)

    description: Optional[str] = None  # full job description text
    application_url: Optional[str] = None

    source: Optional[str] = "linkedin"  # future-proofing
