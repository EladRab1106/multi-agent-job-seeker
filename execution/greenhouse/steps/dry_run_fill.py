from playwright.sync_api import Page
from mapping.mapping_models import FieldMappingResult
from models.submission.form_field_type import FormFieldType
import time

def wait_for_additional_questions(page: Page):
    page.wait_for_selector(
        ".application--questions >> text=LinkedIn Profile",
        timeout=15000
    )


def gentle_scroll(page):
    page.evaluate("""
        () => {
            window.scrollBy(0, 250);
        }
    """)
    time.sleep(0.3)

def find_real_input(page: Page, field_id: str):
    # try direct id
    loc = page.locator(f"#{field_id}")
    if loc.count() == 1 and loc.evaluate("el => el.tagName") in ("INPUT", "TEXTAREA"):
        return loc

    # fallback – search inside wrapper
    wrapper = page.locator(f"#{field_id}")
    if wrapper.count() == 1:
        inner = wrapper.locator("input, textarea")
        if inner.count() == 1:
            return inner

    return None


def dry_run_fill_form(page: Page, mapping: FieldMappingResult):
    print("🧪 Starting Dry-Run Fill")

    # index schema fields by id
    schema_fields = {f.field_id: f for f in mapping.schema.fields}

    for mapped in mapping.mapped_fields:
        field_id = mapped.field_id
        value = mapped.value

        schema_field = schema_fields.get(field_id)
        if not schema_field:
            continue

        field_type = schema_field.type
        print(f"➡ Filling {field_id} ({field_type})")

        # ⏳ LinkedIn / Website מופיעים אחרי טעינה דינמית
        if field_id.startswith("question_"):
            page.wait_for_selector(f"#{field_id}", timeout=15000)

        # ===================== FILE (Resume) =====================
        if field_type == FormFieldType.FILE:
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(value)

            print("📎 Resume uploaded – skipping further actions on this field")
            time.sleep(1)
            continue  # 🚨 חובה – לא לגעת בזה יותר

        # ===================== TEXT / EMAIL / PHONE =====================
        el = page.locator(f"#{field_id}")
        el.wait_for(state="visible", timeout=15000)
        el.scroll_into_view_if_needed()

        # 🔥 Greenhouse חייב fill (לא type)
        el.fill(value)
        el.dispatch_event("blur")

        highlight(el)
        time.sleep(0.4)

    page.evaluate("window.scrollTo(0, 0)")
    print("✅ Dry-Run Fill completed (NO SUBMIT)")



def highlight(el):
    el.evaluate(
        """e => {
            e.style.outline = '3px solid orange';
            e.style.backgroundColor = '#fff3cd';
        }"""
    )



