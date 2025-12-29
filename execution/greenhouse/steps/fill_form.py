from playwright.sync_api import Page
from mapping.mapping_models import FieldMappingResult
from models.submission.form_field_type import FormFieldType

def fill_form(page: Page, mapping: FieldMappingResult):
    for field in mapping.mapped_fields:
        if field.type == FormFieldType.FILE:
            page.set_input_files(f"#{field.field_id}", field.value)
        else:
            page.fill(f"#{field.field_id}", str(field.value))
