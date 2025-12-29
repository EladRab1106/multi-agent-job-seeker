import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def open_job(page: Page, job_url: str) -> None:
    logger.info("Opening Greenhouse job page")
    page.goto(job_url)

    page.wait_for_timeout(2000)

    # 🔍 Greenhouse signature fields (much more reliable than form)
    selectors = [
        "input[name='first_name']",
        "input[name='last_name']",
        "input[type='file']",
        "section#application",
        "div.application-form",
    ]

    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=5000)
            logger.info(f"✅ Greenhouse application detected using selector: {selector}")
            return
        except:
            pass

    page.screenshot(path="greenhouse_debug.png", full_page=True)
    raise RuntimeError(
        "❌ Greenhouse application not detected. "
        "See greenhouse_debug.png"
    )
