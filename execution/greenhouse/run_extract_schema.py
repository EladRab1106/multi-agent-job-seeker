from execution.greenhouse.session import start_session
from execution.greenhouse.steps.open_job import open_job
from execution.greenhouse.steps.extract_schema import extract_schema_from_page

JOB_URL = "https://job-boards.greenhouse.io/rhinofederatedcomputing/jobs/4079601009"


def main():
    session = start_session(headless=False)
    page = session.page

    print("🔍 Opening job page...")
    open_job(page, JOB_URL)

    print("🧠 Extracting form schema...")
    schema = extract_schema_from_page(page)

    print("\n=== EXTRACTED SCHEMA ===\n")
    for f in schema.fields:
        print(
            f"- {f.label} | id={f.field_id} | "
            f"type={f.type} | required={f.required}"
        )

    input("\n✅ Inspect output. Press ENTER to close browser...")
    session.context.close()
    session.browser.close()


if __name__ == "__main__":
    main()
