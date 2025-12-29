from enum import Enum

class FormFieldType(Enum):
    """Enum representing ATS form field types."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    FILE = "file"
    FILE_UPLOAD = "file_upload"  # Explicit resume/file upload field type
    TEXTAREA = "textarea"
