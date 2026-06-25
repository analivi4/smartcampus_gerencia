import json
from pathlib import Path
from datetime import datetime

class PDDLFilesystemService:
  JOBS_PATH = Path("app/runtime/jobs")
  HISTORY_PATH = Path("app/runtime/history")

  def setup_job(self, job_id: str) -> Path:
    job_dir = self.JOBS_PATH / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
  
  def write_problem(self, job_id: str, content: str):
    job_dir = self.JOBS_PATH / job_id
    problem_path = job_dir / "problem.pddl"
    problem_path.write_text(content, encoding="utf-8")
    return problem_path
  
  def write_domain(self, job_id: str) -> Path:
    import os
    domain_src = Path(os.getenv("CAMPUS_DOMAIN", "data/domain.pddl"))
    job_dir = self.JOBS_PATH / job_id
    domain_dst = job_dir / "domain.pddl"

    if not domain_src.exists():
      raise FileNotFoundError(f"Domain source not foundL {domain_src}")

    domain_dst.write_text(domain_src.read_text(encoding="utf-8"), encoding="utf-8")
    return domain_dst
  
  def get_plan_path(self, job_id: str) -> Path:
    return self.JOBS_PATH / job_id / "output" / "plan.txt"

  def read_plan(self, job_id: str) -> str:
    plan_path = self.get_plan_path(job_id)

    if not plan_path.exists():
      raise FileNotFoundError(f"Plan not found: {plan_path}")

    return plan_path.read_text(encoding="utf-8")
  
  def read_error_log(self, job_id: str) -> str:
    error_path = self.JOBS_PATH / job_id / "output" / "error.log"

    if not error_path.exists():
      return None
    
    return error_path.read_text(encoding="utf-8")

  def archive_job(self, job_id: str, status: str, execution_time: float):
    self.HISTORY_PATH.mkdir(parents=True, exist_ok=True)

    job_dir = self.JOBS_PATH / job_id
    history_dir = self.HISTORY_PATH / job_id

    import shutil

    if history_dir.exists():
      shutil.rmtree(history_dir)

    shutil.copytree(job_dir, history_dir)
    shutil.rmtree(job_dir)

    metadata = {
      "job_id": job_id,
      "status": status,
      "execution_time": execution_time,
      "timestamp": datetime.now().isoformat()
    }

    metadata_path = history_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

  def list_jobs(self) -> list:
    if not self.HISTORY_PATH.exists():
      return []

    jobs = []

    for job_dir in self.HISTORY_PATH.iterdir():
      if job_dir.is_dir():
        metadata_path = job_dir / "metadata.json"

        if metadata_path.exists():
          metadata = json.loads(metadata_path.read_text())
          jobs.append(metadata)

    return sorted(jobs, key=lambda x: x["timestamp"])
  
