"""
Run a REAL job application flow for a single Greenhouse job URL.
Opens browser, fills fields, does NOT submit.
"""

import sys
import logging

from graph.state import GraphState
from graph.workflow import build_graph
from models.job import Job
from models.job_queue import JobQueue
from models.cv import CV
from storage.result_store import ResultStore
from agents.cv_optimization_agent import CVOptimizationAgent
from models.optimized_cv import OptimizedCV
from user.profile import UserProfile


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


class StubOptimizer(CVOptimizationAgent):
    def optimize(self, cv: CV, job: Job) -> OptimizedCV:
        logger.info("Stub optimizer: Creating OptimizedCV (no LLM call)")
        return OptimizedCV(
            original_cv=cv,
            job=job,
            tailored_summary=cv.summary,
            tailored_skills=cv.skills,
            full_text=cv.raw_text or "",
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_apply_job.py <job_url>")
        sys.exit(1)

    job_url = sys.argv[1]

    job = Job(
        id="manual-job",
        title="Manual Test Job",
        company="Greenhouse Test",
        application_url=job_url,
    )

    cv = CV(
        full_name="Elad Rabinovitch",
        email="elad@test.com",
        location="Israel",
        summary="Backend / Full-Stack Developer",
        skills=["Python", "Node.js", "React", "Docker"],
        resume_path="/Users/eladrabinovitch/Desktop/Elad_Rabinovitch_CV_2025_English 2.docx"
    )

    user_profile = UserProfile(
        first_name="Elad",
        last_name="Rabinovitch",
        email="elad@test.com",
        phone="+972501234567",
        country="Israel",
        resume_path="/Users/eladrabinovitch/Desktop/Elad_Rabinovitch_CV_2025_English 2.docx",
        linkedin="https://linkedin.com/in/elad",
        website="https://elad.dev",
    )

    state = GraphState(
        job_queue=JobQueue(jobs=[job]),
        cv=cv,
        user_profile=user_profile,
        optimizer=StubOptimizer(),
        result_store=ResultStore(candidate_name=cv.full_name),
    )

    graph = build_graph()

    logger.info("Starting REAL application flow")
    final_state = graph.invoke(state)

    print("\n🛑 Browser is open.")
    print("Inspect the filled form, then press ENTER to close browser...")
    input()

    # Cleanup: Close the executor/browser
    if final_state.executor is not None:
        try:
            logger.info("Closing browser...")
            final_state.executor.close()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")


if __name__ == "__main__":
    main()
