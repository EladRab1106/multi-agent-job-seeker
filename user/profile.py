from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    country: str
    resume_path: str

    linkedin: Optional[str] = None
    website: Optional[str] = None
