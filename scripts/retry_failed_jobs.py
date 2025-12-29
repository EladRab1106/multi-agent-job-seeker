from storage.result_store import ResultStore
from models.cv import CV
from models.job import Job
from models.job_queue import JobQueue
from agents.cv_optimization_agent import OpenAICVOptimizationAgent
from agents.submission_agent import SubmissionAgent


def retry_failed(filepath: str, cv: CV):
    run = ResultStore.load(filepath)

    failed_jobs = [
        Job(
            title=j["title"],
            company=j["company"],
            description="",
            location=""
        )
        for j in run["jobs"]
        if j["status"] == "failed"
    ]

    if not failed_jobs:
        print("No failed jobs to retry.")
        return

    job_queue = JobQueue(failed_jobs)
    optimizer = OpenAICVOptimizationAgent()
    submission_agent = SubmissionAgent(optimizer)

    submission_agent.process_jobs(cv, job_queue)


if __name__ == "__main__":
    cv = CV(
        full_name="Test User",
        skills=["Python", "FastAPI", "SQL"],
        location="Remote",
        summary="Backend developer",
    )

    retry_failed("results/run_2025-12-26_15-06-28.json", cv)
