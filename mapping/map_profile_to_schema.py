from mapping.mapping_models import FieldMappingResult, MappedField
from models.submission.form_schema import SubmissionFormSchema
from user.profile import UserProfile


def map_profile_to_schema(
    schema: SubmissionFormSchema,
    profile: UserProfile,
) -> FieldMappingResult:

    mapped_fields = []          
    missing_required = []

    for field in schema.fields:
        value = None

        if field.field_id == "first_name":
            value = profile.first_name
        elif field.field_id == "last_name":
            value = profile.last_name
        elif field.field_id == "email":
            value = profile.email
        elif field.field_id == "phone":
            value = profile.phone
        elif field.field_id == "country":
            value = profile.country
        elif field.field_id == "resume":
            value = profile.resume_path
        elif "linkedin" in field.label.lower():
            value = profile.linkedin
        elif "website" in field.label.lower():
            value = profile.website

        if value:
            mapped_fields.append(
                MappedField(
                    field_id=field.field_id,
                    value=value,
                )
            )
        elif field.required:
            missing_required.append(field.field_id)

    return FieldMappingResult(
        schema=schema,                           # 🔑 חשוב
        mapped_fields=mapped_fields,
        missing_required_fields=missing_required,
    )
