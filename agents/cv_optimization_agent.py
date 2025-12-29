import logging
import time
from abc import ABC, abstractmethod
from openai import OpenAI, OpenAIError

from models.cv import CV
from models.job import Job
from models.optimized_cv import OptimizedCV

logger = logging.getLogger(__name__)


class CVOptimizationAgent(ABC):
    """
    Abstract base class for CV optimization agents.
    All optimizers must implement the optimize() method.
    """

    @abstractmethod
    def optimize(self, cv: CV, job: Job) -> OptimizedCV:
        """
        Optimize a CV for a specific job.
        
        Args:
            cv: The original CV to optimize
            job: The target job description
            
        Returns:
            OptimizedCV: A job-specific optimized version of the CV
        """
        pass


class OpenAICVOptimizationAgent(CVOptimizationAgent):
    """
    CV optimization agent using OpenAI.
    Responsible for tailoring a CV to a specific job description using OpenAI.
    """

    def __init__(self):
        self.client = OpenAI()

    def optimize(self, cv: CV, job: Job) -> OptimizedCV:
        max_retries = 3
        delay = 2  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Optimizing CV | attempt=%d | job=%s | company=%s",
                    attempt,
                    job.title,
                    job.company,
                )

                full_text = self._call_openai(cv, job)

                return OptimizedCV(
                    original_cv=cv,
                    job=job,
                    full_text=full_text,
                )

            except OpenAIError as e:
                logger.warning(
                    "OpenAI failure | attempt=%d | job=%s | error=%s",
                    attempt,
                    job.title,
                    str(e),
                )

                if attempt == max_retries:
                    logger.error(
                        "CV optimization failed after retries | job=%s | company=%s",
                        job.title,
                        job.company,
                    )
                    raise

                time.sleep(delay)

    def _call_openai(self, cv: CV, job: Job) -> str:
        """
        Low-level OpenAI call. This is the ONLY place that talks to OpenAI.
        """

        prompt = f"""
You are a professional resume writer.

JOB TITLE:
{job.title}

COMPANY:
{job.company}

JOB DESCRIPTION:
{job.description}

CANDIDATE SUMMARY:
{cv.summary}

SKILLS:
{", ".join(cv.skills)}

Rewrite the CV to best match this role.
Focus on relevance, keywords, and clarity.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You optimize resumes for job applications."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()
