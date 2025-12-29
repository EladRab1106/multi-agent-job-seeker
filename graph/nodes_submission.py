import logging
from graph.state import GraphState
from models.submission.form_schema import SubmissionFormSchema
from models.submission.form_field import FormField
from models.submission.form_field_type import FormFieldType
from execution.greenhouse.greenhouse_executor import GreenhouseExecutor


logger = logging.getLogger(__name__)

def _resolve_mapping_hint(state: GraphState, hint: str):
    """
    Resolve mapping hints like:
    - cv.full_name
    - optimized_cv.cover_letter
    
    Returns None if source object is missing or attribute doesn't exist.
    """
    if hint.startswith("cv."):
        if state.cv is None:
            return None
        attr_name = hint.replace("cv.", "")
        return getattr(state.cv, attr_name, None)

    if hint.startswith("optimized_cv."):
        if state.current_optimized_cv is None:
            return None
        attr_name = hint.replace("optimized_cv.", "")
        return getattr(state.current_optimized_cv, attr_name, None)

    # Also support user_profile for backward compatibility
    if hint.startswith("user_profile."):
        if state.user_profile is None:
            return None
        attr_name = hint.replace("user_profile.", "")
        return getattr(state.user_profile, attr_name, None)

    return None



def submit_start_node(state: GraphState) -> GraphState:
    """
    Initialize submission for the current job.
    Deterministic: requires current_job with application_url.
    If missing, sets ats_type to None and returns early.
    """
    job = state.current_job
    if job is None:
        logger.warning("submit_start_node called without current_job")
        state.ats_type = None
        return state

    url = job.application_url
    if not url:
        logger.warning("submit_start_node called with job missing application_url")
        state.ats_type = None
        return state

    url = url.lower()

    if "greenhouse.io" in url:
        state.ats_type = "greenhouse"
    else:
        state.ats_type = "unsupported"
        logger.warning("Unsupported ATS type | url=%s", url)
        return state

    if state.executor is None:
        state.executor = GreenhouseExecutor(
            job_url=job.application_url,
            headless=False,  
        )

    logger.info("Submission started | ats_type=%s | job=%s | company=%s", 
                state.ats_type, job.title, job.company)
    return state



def detect_ats_node(state):
    if state.ats_type is None:
        state.ats_type = "unknown"
    return state



def extract_schema_node(state: GraphState) -> GraphState:
    """
    Extract the submission form schema.

    Deterministic stub for now.
    Will later be replaced by DOM parsing / LLM inference.
    """

    job = state.current_job
    if job is None:
        logger.warning("extract_schema_node called without current_job")
        return state

    if not job.application_url:
        logger.warning("extract_schema_node called with job missing application_url")
        return state

    logger.info(
        "Extracting form schema | title=%s | company=%s | ats=%s",
        job.title,
        job.company,
        state.ats_type,
    )

    schema = SubmissionFormSchema(
        ats_type=state.ats_type,
        form_url=job.application_url,
        fields=[
            # Greenhouse uses separate first_name and last_name fields
            FormField(
                field_id="first_name",
                label="First Name",
                type=FormFieldType.TEXT,
                required=True,
                mapping_hint="cv.full_name",  # Will be split in map_fields_node
            ),
            FormField(
                field_id="last_name",
                label="Last Name",
                type=FormFieldType.TEXT,
                required=True,
                mapping_hint="cv.full_name",  # Will be split in map_fields_node
            ),
            FormField(
                field_id="email",
                label="Email",
                type=FormFieldType.EMAIL,
                required=True,
                mapping_hint="cv.email",
            ),
            FormField(
                field_id="phone",
                label="Phone",
                type=FormFieldType.PHONE,
                required=False,
                mapping_hint="user_profile.phone",
            ),
            FormField(
                field_id="country",
                label="Country",
                type=FormFieldType.TEXT,
                required=False,
                mapping_hint="user_profile.country",
            ),
            FormField(
                field_id="resume",
                label="Resume",
                type=FormFieldType.FILE_UPLOAD,
                required=True,
                mapping_hint="cv.resume_path",  # Map from CV resume_path
            ),
            FormField(
                field_id="question_4576438009",
                label="LinkedIn Profile",
                type=FormFieldType.TEXT,
                required=False,
                mapping_hint="user_profile.linkedin",
            ),
            FormField(
                field_id="question_4576439009",
                label="Website",
                type=FormFieldType.TEXT,
                required=False,
                mapping_hint="user_profile.website",
            ),
            FormField(
                field_id="cover_letter",
                label="Cover Letter",
                type=FormFieldType.TEXTAREA,
                required=False,
                mapping_hint="optimized_cv.cover_letter",
            ),
        ],
    )

    state.form_schema = schema
    return state



def map_fields_node(state: GraphState) -> GraphState:
    """
    Map CV + optimized CV to submission form fields.
    
    Greenhouse-specific mapping:
    - Splits cv.full_name into first_name and last_name
    - Maps resume from cv.resume_path (or user_profile.resume_path)
    - Never outputs full_name (Greenhouse doesn't have this field)
    
    Deterministic, schema-driven mapping.
    """

    schema = state.form_schema
    if schema is None:
        logger.warning("map_fields_node called without form_schema")
        state.field_mapping = {}
        return state

    logger.info(
        "Mapping CV to fields | fields=%d",
        len(schema.fields),
    )

    field_mapping = {}
    
    # First pass: resolve all mapping hints
    for field in schema.fields:
        value = None

        if field.mapping_hint:
            value = _resolve_mapping_hint(state, field.mapping_hint)

        field_mapping[field.field_id] = value

        logger.debug(
            "Mapped field | id=%s | value=%s",
            field.field_id,
            "SET" if value is not None else "MISSING",
        )
    
    # Second pass: Handle Greenhouse-specific transformations
    # Priority: user_profile first_name/last_name > split cv.full_name
    
    # If user_profile exists, use its first_name/last_name directly (highest priority)
    if state.user_profile:
        if "first_name" in field_mapping:
            field_mapping["first_name"] = state.user_profile.first_name
        if "last_name" in field_mapping:
            field_mapping["last_name"] = state.user_profile.last_name
    
    # If we still need to split full_name (user_profile not available or fields missing)
    if state.cv and state.cv.full_name:
        full_name_value = state.cv.full_name
        
        # Check if first_name needs splitting (contains full name or is empty)
        if "first_name" in field_mapping:
            first_val = str(field_mapping["first_name"]).strip() if field_mapping["first_name"] else ""
            full_name_str = str(full_name_value).strip()
            
            # If first_name equals full_name or is empty, split it
            if first_val == full_name_str or not first_val:
                parts = full_name_str.split(" ", 1)
                if len(parts) >= 1:
                    field_mapping["first_name"] = parts[0]
                if len(parts) >= 2:
                    field_mapping["last_name"] = parts[1]
                else:
                    field_mapping["last_name"] = ""
        
        # Check if last_name needs to be set (if it's empty or contains full name)
        if "last_name" in field_mapping:
            last_val = str(field_mapping["last_name"]).strip() if field_mapping["last_name"] else ""
            full_name_str = str(full_name_value).strip()
            
            if last_val == full_name_str:
                # Last name contains full name - split it
                parts = full_name_str.split(" ", 1)
                if len(parts) >= 1:
                    field_mapping["first_name"] = parts[0]
                if len(parts) >= 2:
                    field_mapping["last_name"] = parts[1]
            elif not last_val and "first_name" in field_mapping:
                # Last name is empty - try to extract from full_name
                parts = full_name_str.split(" ", 1)
                if len(parts) >= 2:
                    field_mapping["last_name"] = parts[1]
    
    # Handle resume mapping - prioritize cv.resume_path, fallback to user_profile.resume_path
    if "resume" in field_mapping:
        resume_path = field_mapping["resume"]
        
        # If not set or empty, try cv.resume_path
        if not resume_path and state.cv:
            resume_path = getattr(state.cv, 'resume_path', None)
        
        # If still not set, try user_profile.resume_path
        if not resume_path and state.user_profile:
            resume_path = getattr(state.user_profile, 'resume_path', None)
        
        field_mapping["resume"] = resume_path
        
        if resume_path:
            logger.info(f"Resume mapped successfully: {resume_path}")
        else:
            logger.warning("Resume path not found - checked cv.resume_path and user_profile.resume_path")
    
    # Remove full_name if it exists (Greenhouse doesn't use it)
    if "full_name" in field_mapping:
        del field_mapping["full_name"]
        logger.debug("Removed full_name from mapping (Greenhouse uses first_name/last_name)")

    state.field_mapping = field_mapping
    return state



def fill_form_node(state: GraphState) -> GraphState:
    """
    Fill Greenhouse form fields using generic, deterministic selectors.
    
    Strategy:
    1. Primary: Label-based selectors (page.get_by_label) - most reliable for Greenhouse
    2. Fallback: Direct ID selectors (#first_name, #last_name, #email, #phone)
    3. File upload: input[type="file"] with set_input_files (no button clicks)
    
    Handles full_name by splitting into first_name/last_name automatically.
    """
    executor = state.executor
    mapping = state.field_mapping
    schema = state.form_schema

    if executor is None:
        logger.warning("fill_form_node called without executor")
        return state

    if mapping is None:
        logger.warning("fill_form_node called without field_mapping")
        return state

    page = executor.get_page()

    # Wait for form to be ready - Greenhouse forms load dynamically
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
        # Wait for Greenhouse application form specifically
        page.wait_for_selector("form#application-form", timeout=10000)
        # Wait for at least one input field to be visible (ensures form is interactive)
        page.wait_for_selector("input#first_name, input#last_name, input#email", timeout=10000, state="visible")
        logger.info("Greenhouse form loaded and ready")
    except Exception as e:
        logger.warning(f"Form wait timeout: {e}")
        return state

    # Fill fields using schema-aware approach
    if schema is None:
        logger.warning("No schema available, using generic Greenhouse field mapping")
        _fill_greenhouse_fields_generic(page, mapping)
    else:
        _fill_greenhouse_fields_with_schema(page, schema, mapping)

    logger.info("Greenhouse form filling completed (no submit)")
    return state


def _fill_greenhouse_fields_generic(page, mapping: dict):
    """
    Fill Greenhouse form fields generically without schema.
    Handles standard Greenhouse fields: first_name, last_name, email, phone, resume.
    """
    # Handle full_name by splitting into first_name and last_name
    if "full_name" in mapping and mapping["full_name"]:
        full_name = str(mapping["full_name"]).strip()
        if " " in full_name:
            parts = full_name.split(" ", 1)
            if "first_name" not in mapping:
                mapping["first_name"] = parts[0]
            if "last_name" not in mapping:
                mapping["last_name"] = parts[1]
        else:
            # If no space, use as first_name
            if "first_name" not in mapping:
                mapping["first_name"] = full_name
    
    # Standard Greenhouse field mappings: (field_id, label_text, id_selector)
    field_configs = [
        ("first_name", "First Name", "#first_name"),
        ("last_name", "Last Name", "#last_name"),
        ("email", "Email", "#email"),
        ("phone", "Phone", "#phone"),
    ]
    
    for field_id, label_text, id_selector in field_configs:
        if field_id not in mapping or not mapping[field_id]:
            continue
        
        value = str(mapping[field_id])
        _fill_greenhouse_text_field(page, field_id, label_text, id_selector, value)
    
    # Handle resume file upload (CRITICAL - must use set_input_files)
    if "resume" in mapping and mapping["resume"]:
        file_path = str(mapping["resume"]).strip()
        if file_path:
            success = _fill_greenhouse_file_field(page, file_path)
            if not success:
                logger.error(f"Failed to upload resume: {file_path}")
        else:
            logger.warning("Resume path is empty")
    else:
        logger.warning("Resume not found in field mapping")


def _fill_greenhouse_fields_with_schema(page, schema: SubmissionFormSchema, mapping: dict):
    """
    Fill Greenhouse form fields using schema information.
    Uses label-based selectors with ID fallback for reliability.
    """
    for field in schema.fields:
        field_id = field.field_id
        value = mapping.get(field_id)
        
        if not value:
            if field.required:
                logger.warning(f"Required field '{field_id}' has no value")
            continue
        
        try:
            # Handle file uploads (resume) - CRITICAL: use set_input_files only
            if field.type in (FormFieldType.FILE, FormFieldType.FILE_UPLOAD):
                file_path = str(value).strip()
                if file_path:
                    success = _fill_greenhouse_file_field(page, file_path)
                    if not success:
                        logger.error(f"Failed to upload resume for field '{field_id}': {file_path}")
                else:
                    logger.warning(f"Resume path is empty for field '{field_id}'")
                continue
            
            # Handle country dropdown (special case - it's a select/combobox)
            if field_id == "country":
                _fill_greenhouse_country_field(page, str(value))
                continue
            
            # Handle text fields (first_name, last_name, email, phone, LinkedIn, website, etc.)
            # For question_* fields, use the field_id directly as selector
            if field_id.startswith("question_"):
                _fill_greenhouse_text_field(page, field_id, field.label, f"#{field_id}", str(value))
            else:
                _fill_greenhouse_text_field(page, field_id, field.label, f"#{field_id}", str(value))
                
        except Exception as e:
            logger.warning(f"Error filling field {field_id}: {e}")


def _fill_greenhouse_text_field(page, field_id: str, label_text: str, id_selector: str, value: str) -> bool:
    """
    Fill a Greenhouse text field using label-based selector with ID fallback.
    
    Strategy:
    1. Primary: Direct ID selector (#first_name, #last_name, etc.) - most reliable
    2. Fallback: Label-based selector (page.get_by_label) - uses label[for] connection
    
    Returns True if field was filled, False otherwise.
    """
    # Strategy 1: Direct ID selector (primary - Greenhouse uses standard IDs)
    try:
        locator = page.locator(id_selector)
        # Wait for the element to be visible and ready
        locator.wait_for(state="visible", timeout=5000)
        if locator.count() > 0:
            # Clear any existing value first
            locator.first.clear()
            # Fill with the value
            locator.first.fill(value)
            # Verify the value was set
            filled_value = locator.first.input_value()
            if filled_value == value:
                logger.info(f"Filled '{field_id}' using ID selector '{id_selector}' with value: {value[:50]}")
                return True
            else:
                logger.warning(f"Value mismatch for '{field_id}': expected '{value[:50]}', got '{filled_value[:50] if filled_value else 'empty'}'")
    except Exception as e:
        logger.debug(f"ID selector failed for '{field_id}': {e}")
    
    # Strategy 2: Label-based selector (fallback - uses label[for] connection)
    try:
        locator = page.get_by_label(label_text, exact=False)
        if locator.count() > 0:
            locator.first.wait_for(state="visible", timeout=5000)
            locator.first.clear()
            locator.first.fill(value)
            # Verify
            filled_value = locator.first.input_value()
            if filled_value == value:
                logger.info(f"Filled '{field_id}' using label '{label_text}' with value: {value[:50]}")
                return True
    except Exception as e:
        logger.debug(f"Label-based selector failed for '{field_id}': {e}")
    
    logger.warning(f"Could not fill field '{field_id}' (tried ID '{id_selector}' and label '{label_text}')")
    return False


def _fill_greenhouse_country_field(page, country_value: str):
    """
    Fill Greenhouse country dropdown field.
    
    The country field is a React Select component, so we need to:
    1. Click the country selector
    2. Type the country name
    3. Select from dropdown
    """
    if not country_value:
        return False
    
    try:
        # Try to find the country input (it's inside a select component)
        country_input = page.locator("input#country")
        if country_input.count() > 0:
            # Click to open dropdown
            country_input.first.click()
            # Type the country name
            country_input.first.fill(country_value)
            # Wait a bit for dropdown to appear
            page.wait_for_timeout(500)
            # Try to select the first matching option
            # The dropdown items have role="option"
            option = page.locator(f'[role="option"]:has-text("{country_value}")').first
            if option.count() > 0:
                option.click()
                logger.info(f"Selected country: {country_value}")
                return True
            else:
                # Try pressing Enter to select
                country_input.first.press("Enter")
                logger.info(f"Selected country via Enter: {country_value}")
                return True
        else:
            logger.warning("Country input not found")
            return False
    except Exception as e:
        logger.warning(f"Country selection failed: {e}")
        return False


def _fill_greenhouse_file_field(page, file_path: str):
    """
    Fill Greenhouse resume file upload field.
    
    Uses input#resume or input[type="file"] selector and set_input_files() - no button clicks needed.
    Greenhouse file inputs are typically hidden (class="visually-hidden") but accessible via Playwright.
    
    This is the ONLY way to upload files in Greenhouse - DO NOT click buttons.
    """
    import os
    
    if not file_path:
        logger.warning("Resume file path not provided")
        return False
    
    # Normalize the file path: remove escape sequences and normalize
    # Handle cases where path has escaped backslashes like "file\\ name.docx"
    normalized_path = str(file_path).strip()
    # Replace escaped backslashes with spaces (common in Python string literals)
    normalized_path = normalized_path.replace("\\ ", " ").replace("\\", "")
    # Use os.path.normpath to normalize path separators
    normalized_path = os.path.normpath(normalized_path)
    
    # Verify file exists before attempting upload
    if not os.path.exists(normalized_path):
        logger.error(f"Resume file not found: {normalized_path} (original: {file_path})")
        return False
    
    if not os.path.isfile(normalized_path):
        logger.error(f"Resume path is not a file: {normalized_path}")
        return False
    
    try:
        # Strategy 1: Try specific resume input by ID (Greenhouse standard)
        file_input = page.locator("input#resume[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(normalized_path)
            logger.info(f"Resume uploaded successfully via #resume: {normalized_path}")
            return True
        
        # Strategy 2: Fallback to any file input
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(normalized_path)
            logger.info(f"Resume uploaded successfully via input[type='file']: {normalized_path}")
            return True
        else:
            logger.warning("No file input found on page (tried #resume and input[type='file'])")
            return False
    except Exception as e:
        logger.warning(f"Resume upload failed: {e}")
        return False



def validate_form_node(state: GraphState) -> GraphState:
    """
    Validate that all required fields have values.

    Deterministic validation:
    - Required fields must be present and non-empty
    """

    schema = state.form_schema
    mapping = state.field_mapping

    if schema is None:
        logger.warning("validate_form_node called without form_schema")
        state.submission_attempts += 1
        return state

    if mapping is None:
        logger.warning("validate_form_node called without field_mapping")
        state.submission_attempts += 1
        return state

    missing_fields = []

    for field in schema.fields:
        if not field.required:
            continue

        value = mapping.get(field.field_id)

        if value is None or value == "" or value == []:
            missing_fields.append(field.field_id)

    if missing_fields:
        logger.warning(
            "Form validation failed | missing_fields=%s | attempt=%d",
            missing_fields,
            state.submission_attempts + 1,
        )

        state.submission_attempts += 1

        # Let graph routing decide retry vs fail
        return state

    logger.info("Form validation successful")
    return state



def confirm_submission_node(state: GraphState) -> GraphState:
    logger.info("Confirming submission (stub)")
    state.submission_attempts += 1
    return state


def submit_success_node(state: GraphState) -> GraphState:
    """
    Handle successful submission.
    Records success if result_store is available, then clears current job.
    """
    job = state.current_job
    if job:
        logger.info(
            "Submission success | title=%s | company=%s",
            job.title,
            job.company,
        )

        if state.result_store is not None:
            state.result_store.record_success(
                job.company,
                job.title,
            )

    state.current_job = None
    state.current_optimized_cv = None
    return state


def submit_failed_node(state: GraphState) -> GraphState:
    """
    Handle failed submission.
    Records failure if result_store is available, then clears current job.
    """
    job = state.current_job
    if job:
        logger.error(
            "Submission failed | title=%s | company=%s",
            job.title,
            job.company,
        )

        if state.result_store is not None:
            state.result_store.record_failure(
                job.company,
                job.title,
                "Submission failed",
            )

    state.current_job = None
    state.current_optimized_cv = None
    return state
