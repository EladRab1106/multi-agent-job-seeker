from graph.state import GraphState
from graph.nodes import pop_job_node
from models.job_queue import JobQueue
from models.job import Job

def main():
    job = Job(
        id="job-1",
        title="Test Job",
        company="Test Co",
        apply_url="https://job-boards.greenhouse.io/test/jobs/1"
    )

    queue = JobQueue()
    queue.add(job)

    state = GraphState(job_queue=queue)

    state = pop_job_node(state)

    print("Current job:", state.current_job)
    print("Queue empty:", state.job_queue.is_empty())

if __name__ == "__main__":
    main()
