from pathlib import Path

class PlannerOutputService:
	JOBS_PATH = Path("app/runtime/jobs")
	HISTORY_PATH = Path("app/runtime/history")

	def __init__(self, job_id: str):
		self.job_id = job_id
		self.job_path = self.JOBS_PATH / job_id
		self.history_path = self.HISTORY_PATH / job_id

	def is_ready(self) -> bool:
		return self.history_path.exists()

	def read_plan(self) -> str:
		plan_path = self.history_path / "output" / "plan.txt"
			
		if not plan_path.exists():
			raise FileNotFoundError(f"Plan not found: {plan_path}")

		return plan_path.read_text(encoding="utf-8")
	
	def get_metadata(self) -> dict:
		import json

		metadata_path = self.history_path / "metadata.json"

		if not metadata_path.exists():
			raise FileNotFoundError("Metadata not found")

		return json.loads(metadata_path.read_text())

	def get_error_log(self) -> str:
		error_path = self.history_path / "output" / "error.log"

		if not error_path.exists():
			return None
		
		return error_path.read_text(encoding="utf-8")