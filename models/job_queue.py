from typing import List
from pydantic import BaseModel, Field

from models.job import Job


class JobQueue(BaseModel):
    """
    FIFO queue of job positions to be processed by the Submission Agent.
    This object owns iteration order and guarantees deterministic execution.
    """

    jobs: List[Job] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.jobs) == 0

    def pop_next(self) -> Job:
        if self.is_empty():
            raise IndexError("Cannot pop from an empty JobQueue")
        return self.jobs.pop(0)

    def add(self, job: Job) -> None:
        self.jobs.append(job)
