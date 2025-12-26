from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

from models.cv import CV
from models.job import Job
from models.job_queue import JobQueue
from models.optimized_cv import OptimizedCV
from storage.result_store import ResultStore


class GraphState(BaseModel):
    # ========= Core flow =========
    cv: CV
    job_queue: JobQueue
    result_store: ResultStore

    current_job: Optional[Job] = None
    current_optimized_cv: Optional[OptimizedCV] = None

    # ========= Optimization retry =========
    retry_count: int = 0
    max_retries: int = 3

    # ========= Submission sub-graph =========
    ats_type: Optional[str] = None
    form_schema: Optional[List[Dict[str, Any]]] = None
    field_mapping: Optional[Dict[str, Any]] = None

    submission_attempts: int = 0
    max_submission_attempts: int = 2

    # ========= Pydantic config =========
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
