"""
Minimal dry-run test for LangGraph submission workflow.

This script tests that:
1. GraphState is the single source of truth
2. All nodes handle Optional fields safely
3. The graph runs end-to-end without crashes
4. Dry-run mode (no actual submission)

Expected log output indicating successful execution (even if validation fails):
- "Popped job | title=..."
- "Stub optimizer: Creating OptimizedCV (no LLM call)"
- "Submission started | ats_type=greenhouse | ..."
- "Extracting form schema | ..."
- "Mapping CV to fields | ..."
- "Filling form (stub)"
- Either "Form validation successful" OR "Form validation failed" (both are valid)
- "Confirming submission (stub)"
- Either "Submission success" OR "Submission failed" (both are valid paths)

Note: Validation may fail due to missing resume file - this is expected and shows
the validation logic works correctly. The important thing is the graph doesn't crash.
"""

import logging
from graph.state import GraphState
from graph.workflow import build_graph
from models.job import Job
from models.job_queue import JobQueue
from models.cv import CV
from models.optimized_cv import OptimizedCV
from storage.result_store import ResultStore
from agents.cv_optimization_agent import CVOptimizationAgent

# Configure logging to see node execution
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | %(name)s | %(message)s'
)

logger = logging.getLogger(__name__)


class StubOptimizer(CVOptimizationAgent):
    """
    Deterministic stub optimizer - no LLM calls.
    Returns a simple OptimizedCV based on the original CV.
    """
    
    def optimize(self, cv: CV, job: Job) -> OptimizedCV:
        """
        Create a deterministic OptimizedCV without LLM.
        For testing purposes only.
        """
        logger.info("Stub optimizer: Creating OptimizedCV (no LLM call)")
        
        return OptimizedCV(
            original_cv=cv,
            job=job,
            tailored_summary=f"Optimized summary for {job.title} at {job.company}",
            tailored_skills=cv.skills + [f"{job.company} specific skill"],
            full_text=f"Optimized CV text for {job.title}",
        )


def main():
    """
    Run the full graph workflow in dry-run mode.
    """
    logger.info("=" * 60)
    logger.info("Starting LangGraph Dry-Run Test")
    logger.info("=" * 60)
    
    # ===== Create test data =====
    test_job = Job(
        id="test-job-1",
        title="Backend Developer",
        company="Test Company",
        application_url="https://job-boards.greenhouse.io/rhinofederatedcomputing/jobs/4079601009",
        description="Test job description for backend developer role",
    )
    
    test_cv = CV(
        full_name="Test User",
        email="test@example.com",
        location="Remote",
        summary="Experienced backend developer",
        skills=["Python", "FastAPI", "SQL", "Docker"],
    )
    
    # Note: For a real test, you'd need a resume file path
    # For dry-run, the mapping will show missing fields but won't crash
    
    # ===== Initialize GraphState with all required fields =====
    state = GraphState(
        # Job flow
        job_queue=JobQueue(jobs=[test_job]),
        current_job=None,  # Will be set by POP_JOB node
        
        # User data
        cv=test_cv,
        user_profile=None,  # Optional - not needed for this test
        current_optimized_cv=None,  # Will be set by OPTIMIZE node
        
        # Optimization
        optimizer=StubOptimizer(),  # Stub - no LLM
        retry_count=0,
        max_retries=3,
        
        # Submission (will be set by nodes)
        ats_type=None,
        executor=None,  # Will be created by submit_start_node
        form_schema=None,
        field_mapping=None,
        submission_attempts=0,
        max_submission_attempts=2,
        
        # Observability
        result_store=ResultStore(candidate_name=test_cv.full_name),
    )
    
    # ===== Build and run graph =====
    logger.info("Building graph...")
    graph = build_graph()
    
    logger.info("Invoking graph...")
    logger.info("-" * 60)
    
    final_state = None
    try:
        final_state = graph.invoke(state)
        
        logger.info("-" * 60)
        logger.info("=" * 60)
        logger.info("✅ Graph execution completed successfully!")
        logger.info("=" * 60)
        
        # ===== Verify final state =====
        logger.info(f"  - Current job: {final_state.get('current_job')}")
        logger.info(f"  - Optimized CV created: {final_state.get('current_optimized_cv') is not None}")
        logger.info(f"  - ATS type detected: {final_state.get('ats_type')}")
        logger.info(f"  - Form schema extracted: {final_state.get('form_schema') is not None}")
        logger.info(f"  - Field mapping created: {final_state.get('field_mapping') is not None}")
        logger.info(f"  - Submission attempts: {final_state.get('submission_attempts')}")

        
        # Save results
        result_store = final_state.get("result_store")
        if result_store is not None:
            result_store.save()
            logger.info(f"Results saved to: {result_store.filepath}")

        
        logger.info("\n✅ DRY-RUN TEST PASSED")
        logger.info("The graph executed end-to-end without runtime errors.")
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ Graph execution failed with error:")
        logger.error(f"  {type(e).__name__}: {str(e)}")
        logger.error("=" * 60)
        raise
    
    finally:
        # Ensure executor cleanup (check both final_state and state)
        executor_to_cleanup = None

        if final_state is not None:
            executor_to_cleanup = final_state.get("executor")

        if executor_to_cleanup is None:
            executor_to_cleanup = state.executor

        elif state.executor is not None:
            executor_to_cleanup = state.executor
        
        if executor_to_cleanup is not None:
            try:
                logger.info("Cleaning up executor...")
                executor_to_cleanup.close()
            except Exception as cleanup_error:
                logger.warning(f"Error during executor cleanup: {cleanup_error}")


if __name__ == "__main__":
    main()
