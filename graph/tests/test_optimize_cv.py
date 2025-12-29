from graph.state import GraphState
from models.job import Job
from models.cv import CV
from agents.cv_optimization_agent import OptimizedCV  # או איך שקראת לו

def main():
    state = GraphState(
        cv=CV(
            full_name="Elad Rabinovitch",
            email="elad@test.com",
            skills=["Python", "React"]
        ),
        optimizer=OptimizedCV(),
        current_job=Job(
            id="job-1",
            title="Backend Engineer",
            company="Test Co",
            application_url="https://job-boards.greenhouse.io/test/jobs/1"
        )
    )

    from graph.nodes import optimize_cv_node

    state = optimize_cv_node(state)

    assert state.current_optimized_cv is not None
    print("Optimized CV OK")
    print(state.current_optimized_cv)

if __name__ == "__main__":
    main()
