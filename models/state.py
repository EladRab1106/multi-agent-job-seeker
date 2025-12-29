from pydantic import BaseModel, ConfigDict
from typing import Optional

from models.job import Job
from models.job_queue import JobQueue
from mapping.mapping_models import FieldMappingResult
from models.submission.form_schema import SubmissionFormSchema
from models.cv import CV
from models.optimized_cv import OptimizedCV


class GraphState(BaseModel):
    # ===== Job flow =====
    job_queue: JobQueue = JobQueue()
    current_job: Optional[Job] = None

    # ===== CV optimization =====
    cv: Optional[CV] = None
    current_optimized_cv: Optional[OptimizedCV] = None
    retry_count: int = 0
    max_retries: int = 3

    # ===== Submission =====
    ats_type: Optional[str] = None

    # executor – אובייקט ריצה (Playwright)
    executor: Optional[object] = None  

    form_schema: Optional[SubmissionFormSchema] = None
    field_mapping: Optional[FieldMappingResult] = None

    submission_attempts: int = 0
    max_submission_attempts: int = 2

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
