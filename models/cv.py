from typing import List, Optional
from pydantic import BaseModel, Field


class Experience(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CV(BaseModel):
    """
    Immutable representation of a user's CV.
    This object is READ-ONLY throughout the system.
    """

    full_name: str
    email: Optional[str] = None
    location: Optional[str] = None

    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)

    raw_text: Optional[str] = None  # original extracted CV text
