from enum import Enum


class FormFieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    EMAIL = "email"
    PHONE = "phone"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    FILE_UPLOAD = "file_upload"
    DATE = "date"
    NUMBER = "number"
    URL = "url"
