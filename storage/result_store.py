import json
import os
from datetime import datetime
from typing import Dict, Any, List


class ResultStore:
    """
    Persists the results of a single run to a JSON file.
    """

    def __init__(self, candidate_name: str):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_id = f"run_{timestamp}"
        self.filepath = os.path.join("results", f"{self.run_id}.json")

        self.data: Dict[str, Any] = {
            "run_id": self.run_id,
            "candidate": candidate_name,
            "started_at": datetime.utcnow().isoformat(),
            "jobs": [],
        }

    def record_success(self, company: str, title: str) -> None:
        self.data["jobs"].append(
            {
                "company": company,
                "title": title,
                "status": "submitted",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def record_failure(self, company: str, title: str, error: str) -> None:
        self.data["jobs"].append(
            {
                "company": company,
                "title": title,
                "status": "failed",
                "error": error,
                "error_type": error.__class__.__name__ if hasattr(error, "__class__") else "Exception",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


    def finalize(self) -> None:
        total = len(self.data["jobs"])
        submitted = sum(1 for j in self.data["jobs"] if j["status"] == "submitted")
        failed = sum(1 for j in self.data["jobs"] if j["status"] == "failed")

        self.data["summary"] = {
            "total_jobs": total,
            "submitted": submitted,
            "failed": failed,
            "completed_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


    def save(self) -> None:
        self.finalize()
        os.makedirs("results", exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

