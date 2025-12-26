from typing import Optional
import logging

from models.cv import CV

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    The Supervisor Agent is responsible for determining
    the target job role (job query) for the application flow.

    Design principle:
    - Prefer explicit user input.
    - Only infer from CV as a fallback.
    """

    def resolve_job_query(
        self,
        user_job_query: Optional[str],
        cv: CV,
    ) -> str:
        """
        Resolve the final job query to use.

        Priority:
        1. Explicit user-provided job query
        2. Inference from CV experience
        3. Inference from CV skills
        4. Safe default
        """

        # 1️⃣ Explicit user intent always wins
        if user_job_query:
            cleaned = user_job_query.strip()
            if cleaned:
                return cleaned

        # 2️⃣ Infer from most recent experience (if exists)
        if cv.experience:
            # Assume first entry is most recent (by convention)
            role = cv.experience[0].role
            if role:
                return role

        # 3️⃣ Infer from skills (very rough fallback)
        if cv.skills:
            return f"{cv.skills[0]} Developer"

        # 4️⃣ Absolute safe fallback
        return "Software Engineer"
