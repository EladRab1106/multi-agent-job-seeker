from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

from models.job_queue import JobQueue
from execution.greenhouse.greenhouse_executor import GreenhouseExecutor
from models.job import Job
from models.cv import CV
from models.optimized_cv import OptimizedCV
from user.profile import UserProfile
from agents.cv_optimization_agent import CVOptimizationAgent
from storage.result_store import ResultStore
from models.submission.form_schema import SubmissionFormSchema


class GraphState(BaseModel):
    """
    Single source of truth for the LangGraph state machine.
    All nodes read from and write to this state - no hidden globals.
    """

    # ===== Job flow =====
    job_queue: Optional[JobQueue] = None
    current_job: Optional[Job] = None

    # ===== User data =====
    user_profile: Optional[UserProfile] = None
    cv: Optional[CV] = None
    current_optimized_cv: Optional[OptimizedCV] = None

    # ===== Optimization =====
    optimizer: Optional[CVOptimizationAgent] = None
    retry_count: int = 0
    max_retries: int = 3

    # ===== Submission =====
    ats_type: Optional[str] = None
    executor: Optional[GreenhouseExecutor] = None
    form_schema: Optional[SubmissionFormSchema] = None
    # field_mapping is a dict mapping field_id -> value (not FieldMappingResult model)
    field_mapping: Optional[Dict[str, Any]] = None

    submission_attempts: int = 0
    max_submission_attempts: int = 2

    # ===== Observability =====
    result_store: Optional[ResultStore] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
