from graph.state import GraphState
from execution.greenhouse.greenhouse_executor import GreenhouseExecutor


def submit_start_node(state: GraphState) -> GraphState:
    print("\n===== SUBMIT_START_NODE =====")

    # ===== 1️⃣ Job sanity check =====
    assert state.current_job is not None, "❌ current_job is None"

    job = state.current_job
    print("JOB:", job)
    assert hasattr(job, "apply_url"), "❌ job has no apply_url"

    print("APPLY URL:", job.apply_url)

    # ===== 2️⃣ Detect ATS =====
    url = job.apply_url.lower()

    if "greenhouse.io" in url:
        state.ats_type = "greenhouse"
    else:
        state.ats_type = "unsupported"

    print("ATS TYPE:", state.ats_type)
    assert state.ats_type == "greenhouse", "❌ Unsupported ATS"

    # ===== 3️⃣ Executor creation (ONLY ONCE) =====
    if state.executor is None:
        print("🆕 Creating GreenhouseExecutor")

        state.executor = GreenhouseExecutor(
            job_url=job.apply_url,
            headless=False,  # חובה לפיתוח
        )

    else:
        print("♻️ Reusing existing executor")

    # ===== 4️⃣ Executor sanity checks =====
    assert state.executor is not None, "❌ executor is None"
    print("EXECUTOR:", state.executor)
    print("EXECUTOR ID:", id(state.executor))

    # ===== 5️⃣ Browser / page checks =====
    assert hasattr(state.executor, "page"), "❌ executor has no page"
    assert state.executor.page is not None, "❌ executor.page is None"

    print("PAGE:", state.executor.page)
    print("✅ submit_start_node OK")

    return state
