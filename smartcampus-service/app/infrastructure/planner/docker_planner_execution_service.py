import subprocess
import time
from uuid import uuid4
from pathlib import Path
from threading import Lock

class DockerPlannerExecutionService:
  JOBS_PATH = Path("app/runtime/jobs")
  LOCK_FILE = Path("app/runtime/.planner.lock")
  TIMEOUT = 300 # 5 minutes

  _execution_lock = Lock()

  def create_job(self) -> str:
    job_id = str(uuid4())
    job_dir = self.JOBS_PATH / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    output_dir = job_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    return job_id

  def is_running(self) -> bool:
    return self.LOCK_FILE.exists()
  
  def run(self, job_id: str) -> dict:
    with self._execution_lock:
      job_path = self.JOBS_PATH / job_id
      absolute_job_path = job_path.resolve()

      print(f"\n[DEBUG] Job ID: {job_id}")
      print(f"[DEBUG] Path solved: {str(job_path.absolute())}")

      if not job_path.exists():
        raise FileNotFoundError(f"Job directory not found: {job_path}")
      
      self.LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
      self.LOCK_FILE.write_text(job_id)

      start_time = time.time()

      try:
        cmd = [
          "docker", "run", "--rm",
          "-v", f"{absolute_job_path}:/planner/runtime",
          "smart-planner",
          "/planner/runtime/domain.pddl",
          "/planner/runtime/problem.pddl",
        ]

        print(f"[INFO] Running Docker command: {' '.join(cmd)}")
        print(f"[INFO] Volume path: {job_path.resolve()}")

        result = subprocess.run(
          cmd,
          capture_output=True,
          text=True,
          timeout=self.TIMEOUT,
          check=False
        )

        print(f"[DEBUG] Docker stdout:\n{result.stdout}")
        print(f"[DEBUG] Docker stderr:\n{result.stderr}")
        print(f"[DEBUG] Return code: {result.returncode}")

        execution_time = time.time() - start_time

        (job_path / "output" / "stdout.log").write_text(result.stdout)

        if result.stderr:
          (job_path / "output" / "error.log").write_text(result.stderr)

        success = result.returncode == 0

        return {
          "job_id": job_id,
          "success": success,
          "execution_time": execution_time,
          "return_code": result.returncode,
          "message": "Planner executed successfully"
        }
      
      except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        (job_path / "output" / "error.log").write_text(f"Timeout after {self.TIMEOUT} seconds")

        return {
          "job_id": job_id,
          "success": False,
          "execution_time": execution_time,
          "message": f"Planner timeout after {self.TIMEOUT}s"
        }
      
      except Exception as e:
        execution_time = time.time() - start_time
        (job_path / "output" / "error.log").write_text(str(e))

        return {
          "job_id": job_id,
          "success": False,
          "execution_time": execution_time,
          "message": f"Error: {str(e)}"
        }
      
      finally:
        if self.LOCK_FILE.exists():
          self.LOCK_FILE.unlink()
