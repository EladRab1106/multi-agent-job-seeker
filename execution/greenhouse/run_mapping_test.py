from execution.greenhouse.steps.extract_schema import extract_schema_from_page
from execution.greenhouse.session import start_session
from mapping.map_profile_to_schema import map_profile_to_schema
from user.profile import UserProfile


JOB_URL = "https://job-boards.greenhouse.io/rhinofederatedcomputing/jobs/4079601009"


def main():
    session = start_session(headless=False)
    page = session.page

    page.goto(JOB_URL)
    schema = extract_schema_from_page(page)

    profile = UserProfile(
    first_name="Elad",
    last_name="Rabinovitch",
    email="elad@test.com",
    phone="+972501234567",
    country="Israel",
    resume_path="/Users/eladrabinovitch/Desktop/Elad_Rabinovitch_CV_2025_English 2.docx",
    linkedin="https://linkedin.com/in/elad",
    website="https://elad.dev",
    )


    result = map_profile_to_schema(schema, profile)

    print("\n=== MAPPED FIELDS ===\n")
    for f in result.mapped_fields:
        print(f"{f.field_id} → {f.value}")

    print("\nMissing required:", result.missing_required_fields)

    input("\nPress ENTER to exit")
    session.browser.close()


if __name__ == "__main__":
    main()
