from graph.state import GraphState, Job, JobQueue
from graph.workflow import build_graph


def main():
    job = Job(
        id="test-job",
        title="Test Job",
        company="Rhino",
        apply_url="https://job-boards.greenhouse.io/rhinofederatedcomputing/jobs/4079601009",
    )

    state = GraphState(
        job_queue=JobQueue(jobs=[job])
    )

    graph = build_graph()
    graph.invoke(state)


if __name__ == "__main__":
    main()
