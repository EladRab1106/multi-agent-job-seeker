import logging
from playwright.sync_api import Page

from models.submission.form_schema import SubmissionFormSchema
from models.submission.form_field import FormField
from models.submission.form_field_type import FormFieldType

logger = logging.getLogger(__name__)


def extract_schema_from_page(page: Page) -> SubmissionFormSchema:
    logger.info("🔍 Searching for Greenhouse application form")

    form = page.query_selector("form#application-form")
    if not form:
        raise RuntimeError("❌ Greenhouse application form not found")

    fields = []

    for el in form.query_selector_all("input, textarea, select"):
        field_id = el.get_attribute("id")
        if not field_id:
            continue  # Greenhouse real fields always have id

        # 🚫 Skip internal / helper inputs (React widgets, hidden fields)
        input_type = el.get_attribute("type") or ""
        if field_id.startswith("iti-"):
            continue
        if input_type == "hidden":
            continue

        label = _extract_label(el)
        field_type = _detect_field_type(el)
        required = _is_required(el, label)

        fields.append(
            FormField(
                field_id=field_id,
                label=label,
                type=field_type,
                required=required,
            )
        )

    logger.info("✅ Extracted %d Greenhouse fields", len(fields))

    return SubmissionFormSchema(
        ats_type="greenhouse",
        form_url=page.url,
        fields=fields,
    )


# ---------- helpers ----------

def _extract_label(el) -> str:
    label = el.evaluate(
        """el => {
            if (el.id) {
                const label = document.querySelector(`label[for="${el.id}"]`);
                if (label) return label.innerText.trim();
            }
            return el.getAttribute("aria-label") ||
                   el.getAttribute("placeholder") ||
                   el.id;
        }"""
    )
    return label


def _detect_field_type(el) -> FormFieldType:
    t = (el.get_attribute("type") or "").lower()
    el_id = (el.get_attribute("id") or "").lower()
    aria = (el.get_attribute("aria-label") or "").lower()

    if t == "file" or "resume" in el_id or "cv" in el_id:
        return FormFieldType.FILE

    if "email" in el_id or "email" in aria:
        return FormFieldType.EMAIL

    if "phone" in el_id or "phone" in aria:
        return FormFieldType.PHONE

    if el.evaluate("el => el.tagName") == "TEXTAREA":
        return FormFieldType.TEXTAREA

    # 👇 LinkedIn / Website יפלו לכאן
    return FormFieldType.TEXT







def _is_required(el, label: str) -> bool:
    # Direct aria-required
    if el.get_attribute("aria-required") == "true":
        return True

    # Required attribute
    if el.get_attribute("required"):
        return True

    # Check parent containers (important for file upload)
    parent_required = el.evaluate(
        """el => {
            let node = el.parentElement;
            while (node) {
                if (node.getAttribute && node.getAttribute("aria-required") === "true") {
                    return true;
                }
                node = node.parentElement;
            }
            return false;
        }"""
    )
    if parent_required:
        return True

    # Label asterisk fallback
    if label and "*" in label:
        return True

    return False

