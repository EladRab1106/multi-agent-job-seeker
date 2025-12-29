import logging

from graph.state import GraphState
from agents.cv_optimization_agent import CVOptimizationAgent
from agents.submission_agent import SubmissionAgent

logger = logging.getLogger(__name__)


def pop_job_node(state: GraphState) -> GraphState:
    """
    Pops the next job from the queue and stores it in state.current_job.
    Deterministic: if queue is missing or empty, sets current_job to None.
    """
    if state.job_queue is None or state.job_queue.is_empty():
        state.current_job = None
        logger.info("No more jobs in queue")
    else:
        state.current_job = state.job_queue.pop_next()
        logger.info(
            "Popped job | title=%s | company=%s",
            state.current_job.title,
            state.current_job.company,
        )

    return state


def optimize_cv_node(state: GraphState) -> GraphState:
    """
    Optimizes CV for the current job.
    Requires: current_job, cv, optimizer in state.
    If any are missing, sets current_optimized_cv to None and increments retry_count.
    """
    job = state.current_job
    if job is None:
        logger.warning("optimize_cv_node called without current_job")
        state.current_optimized_cv = None
        return state

    if state.cv is None:
        logger.warning("optimize_cv_node called without CV in state")
        state.current_optimized_cv = None
        state.retry_count += 1
        return state

    if state.optimizer is None:
        logger.warning("optimize_cv_node called without optimizer in state")
        state.current_optimized_cv = None
        state.retry_count += 1
        return state

    try:
        logger.info(
            "Optimizing CV | title=%s | company=%s | attempt=%d",
            job.title,
            job.company,
            state.retry_count + 1,
        )

        optimized_cv = state.optimizer.optimize(
            cv=state.cv,
            job=job,
        )

        state.current_optimized_cv = optimized_cv
        state.retry_count = 0  # reset on success

    except Exception as e:
        state.retry_count += 1
        state.current_optimized_cv = None

        logger.warning(
            "Optimization failed | title=%s | company=%s | retry=%d | error=%s",
            job.title,
            job.company,
            state.retry_count,
            str(e),
        )

    return state



def submit_job_node(state: GraphState) -> GraphState:
    optimized_cv = state.current_optimized_cv
    if optimized_cv is None:
        return state

    logger.info(
        "Submitting application | title=%s | company=%s",
        optimized_cv.job.title,
        optimized_cv.job.company,
    )

    state.submission_agent._submit_application(optimized_cv)
    state.result_store.record_success(
        optimized_cv.job.company,
        optimized_cv.job.title,
    )

    # Clear state for next iteration
    state.current_job = None
    state.current_optimized_cv = None

    return state



def optimization_failed_node(state: GraphState) -> GraphState:
    """
    Handles permanent optimization failure.
    Records failure if result_store is available, then clears current_job.
    """
    job = state.current_job

    if job:
        logger.error(
            "Optimization permanently failed | title=%s | company=%s",
            job.title,
            job.company,
        )

        if state.result_store is not None:
            state.result_store.record_failure(
                job.company,
                job.title,
                "CV optimization failed after retries",
            )

    state.current_job = None
    state.retry_count = 0

    return state

