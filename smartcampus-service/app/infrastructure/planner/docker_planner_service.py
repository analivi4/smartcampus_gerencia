import subprocess
from pathlib import Path

class DockerPlannerService:
  def run(self):
    cmd = [
      "docker", "run", "--rm",
      "-v", f"{Path('app/runtime/pddl').resolve()}:/planner/input",
      "planner-image",
      "/planner/input/domain.pddl",
      "/planner/input/problem.pddl"
    ]

    result = subprocess.run(
      cmd,
      capture_output=True,
      text=True,
      check=True
    )

    return result.stdout