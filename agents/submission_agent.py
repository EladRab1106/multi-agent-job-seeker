from typing import List
import logging

from storage.result_store import ResultStore

from models.cv import CV
from models.job import Job
from models.job_queue import JobQueue
from models.optimized_cv import OptimizedCV
from agents.cv_optimization_agent import CVOptimizationAgent

logger = logging.getLogger(__name__)


class SubmissionAgent:
    """
    The Submission Agent is the execution controller.
    It owns the job-processing loop and coordinates
    CV optimization and application submission.
    """

    def __init__(self, optimizer: CVOptimizationAgent):
        self.optimizer = optimizer

    def process_jobs(self, cv: CV, job_queue: JobQueue) -> List[OptimizedCV]:
        total_jobs = len(job_queue.jobs)
        logger.info(
            "Starting submission process | candidate=%s | jobs=%d",
            cv.full_name,
            total_jobs,
        )

        result_store = ResultStore(cv.full_name)
        optimized_results: List[OptimizedCV] = []

        while not job_queue.is_empty():
            job: Job = job_queue.pop_next()

            logger.info(
                "Processing job | title=%s | company=%s",
                job.title,
                job.company,
            )

            try:
                optimized_cv = self.optimizer.optimize(cv, job)
                self._submit_application(optimized_cv)

                optimized_results.append(optimized_cv)
                result_store.record_success(job.company, job.title)

            except Exception as e:
                logger.error(
                    "Job processing failed | title=%s | company=%s | error=%s",
                    job.title,
                    job.company,
                    str(e),
                )
                result_store.record_failure(job.company, job.title, str(e))
                continue

        result_store.save()

        logger.info(
            "Submission process completed | candidate=%s | jobs_processed=%d",
            cv.full_name,
            total_jobs,
        )

        return optimized_results

    def _submit_application(self, optimized_cv: OptimizedCV) -> None:
        """
        Stub for application submission.

        Real implementation will:
        - Open browser
        - Fill forms
        - Upload CV
        - Submit application
        """

        logger.info(
            "Submitted application | company=%s | role=%s",
            optimized_cv.job.company,
            optimized_cv.job.title,
        )
