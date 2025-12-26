from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

from config.logging import setup_logging
setup_logging()

from models.cv import CV
from agents.job_matching_agent import JobMatchingAgent
from storage.result_store import ResultStore

from agents.cv_optimization_agent import CVOptimizationAgent
from agents.submission_agent import SubmissionAgent

from graph.state import GraphState
from graph.workflow import build_graph


def main():
    cv = CV(
        full_name="Test User",
        skills=["Python", "FastAPI", "SQL"],
        location="Remote",
        summary="Backend developer",
    )

    matcher = JobMatchingAgent()
    job_queue = matcher.find_matching_jobs("Backend Developer", cv)

    result_store = ResultStore(cv.full_name)

    # 🔑 Instantiate shared runtime agents
    optimizer = CVOptimizationAgent()
    submission_agent = SubmissionAgent(optimizer)

    graph = build_graph()

    print(graph.get_graph().draw_mermaid())

    # 🔑 Inject agents into state
    state = GraphState(
        cv=cv,
        job_queue=job_queue,
        result_store=result_store,
        optimizer=optimizer,
        submission_agent=submission_agent,
    )

    graph.invoke(state)

    result_store.save()


if __name__ == "__main__":
    main()
