import time
from datetime import timezone, timedelta

from pathlib import Path
from datetime import datetime
from app.application.use_cases.run_planner_use_case import RunPlannerUseCase
from app.application.use_cases.generate_pddl_use_case import GeneratePDDLUseCase
from app.infrastructure.pddl.pddl_filesystem_service import PDDLFilesystemService
from app.infrastructure.planner.docker_planner_execution_service import DockerPlannerExecutionService

class RunPlannerUseCaseImpl(RunPlannerUseCase):
  def __init__(
    self,
    generate_pddl_use_case: GeneratePDDLUseCase,
    filesystem_service: PDDLFilesystemService,
    planner_service: DockerPlannerExecutionService,
    parser: "PDDLPlanParser",
    scheduler: "IScheduler"
  ):
    self._generate_pddl = generate_pddl_use_case
    self._filesystem = filesystem_service
    self._planner = planner_service
    self._parser = parser
    self._scheduler = scheduler

  def execute(self, input_data) -> dict:
    job_id = self._planner.create_job()
    start_time = time.time()
      
    try:
      problem_pddl = self._generate_pddl.execute(input_data)
        
      self._filesystem.setup_job(job_id)
      self._filesystem.write_domain(job_id)
      self._filesystem.write_problem(job_id, problem_pddl)

      execution_result = self._planner.run(job_id)

      if not execution_result.get("success"):
        error_detail = execution_result.get("message")
        raise Exception(f"Planner execution error: {error_detail}")

      plan_path = Path(self._filesystem.get_plan_path(job_id))
      plan_found = self._wait_for_plan(plan_path, max_attempts=3, wait_seconds=20)

      if not plan_found:
        raise FileNotFoundError(f"Plan file not found after waiting: {plan_path}")

      with open(plan_path, "r") as f:
        plan_content = f.read()
      
      ref_date = datetime.now(timezone.utc)

      actions = self._parser.parse_file(plan_content, ref_date)
      actions = self._snap_turn_on_to_class_start(actions, input_data, ref_date)

      device_map = input_data.device_map or {}
      if device_map:
        actions = [
          action.model_copy(update={"target_device_id": device_map.get(action.target_device_id, action.target_device_id)})
          for action in actions
        ]
        
      self._scheduler.clear_all_jobs()
      self._scheduler.schedule_many(actions)

      execution_time = execution_result.get("execution_time", time.time() - start_time)
      
      self._filesystem.archive_job(job_id, "success", execution_time)

      return {
        "job_id": job_id,
        "status": "completed",
        "scheduled_actions_count": len(actions),
        **execution_result
      }
    
    except Exception as e:
      elapsed = time.time() - start_time
      self._filesystem.archive_job(job_id, "error", elapsed)
      raise Exception(f"Job {job_id} failed: {str(e)}")

  def _snap_turn_on_to_class_start(self, actions, input_data, ref_date):
    """Move turn_on execution times to the start of the corresponding class window."""
    TURN_ON = {'turn_on_air_conditioner', 'turn_on_air_conditioner_peak_hours', 'turn_on_light'}
    multiplier = self._parser.time_multiplier
    timed_events = input_data.init.timed_events or []

    class_starts = sorted(
      ref_date + timedelta(hours=ev.time * multiplier)
      for ev in timed_events
      if ev.type == "fluent" and ev.fluent == "people_in_room" and (ev.value or 0) > 0
    )

    # Caso 2: room already occupied at t=0
    for value in input_data.init.fluents.get("people_in_room", {}).values():
      if (value or 0) > 0:
        class_starts = [ref_date] + class_starts

    if not class_starts:
      return actions

    result = []
    for action in actions:
      if action.action_name in TURN_ON:
        snap = next(
          (cs for cs in reversed(class_starts) if cs <= action.execution_time),
          None
        )
        if snap:
          action = action.model_copy(update={"execution_time": snap})
      result.append(action)

    return result

  def _wait_for_plan(self, plan_path: Path, max_attempts: int, wait_seconds: int) -> bool:
    for attempt in range(1, max_attempts + 1):
      print(f"[INFO] Attempt {attempt}: Checking for plan file...")

      if plan_path.exists() and plan_path.stat().st_size > 0:
        print(f"[INFO] Plan file found!")
        return True
      
      if attempt < max_attempts:
        time.sleep(wait_seconds)
        
    return False