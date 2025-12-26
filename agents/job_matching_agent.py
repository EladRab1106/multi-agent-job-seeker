from typing import List

import logging


from models.cv import CV
from models.job import Job
from models.job_queue import JobQueue

logger = logging.getLogger(__name__)


class JobMatchingAgent:
    """
    The Job Matching Agent is responsible for finding
    relevant job positions based on a job query and CV.

    v1 implementation is a stub (mocked jobs).
    Real job searching (LinkedIn, etc.) will be added later.
    """

    def find_matching_jobs(self, job_query: str, cv: CV) -> JobQueue:
        """
        Return a JobQueue of matched jobs.

        For v1:
        - Return deterministic mock jobs
        - Use job_query only for labeling
        """

        mock_jobs: List[Job] = [
            Job(
                id="mock-1",
                title=job_query,
                company="ExampleCorp",
                location=cv.location or "Remote",
                required_skills=cv.skills[:3],
                description=f"Looking for a {job_query} with relevant experience.",
                application_url="https://example.com/jobs/1",
            ),
            Job(
                id="mock-2",
                title=job_query,
                company="AnotherTech",
                location=cv.location or "Remote",
                required_skills=cv.skills[:3],
                description=f"Hiring a skilled {job_query} to join our team.",
                application_url="https://example.com/jobs/2",
            ),
        ]

        return JobQueue(jobs=mock_jobs)
