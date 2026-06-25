from fastapi import APIRouter, Depends, Query, BackgroundTasks
from datetime import datetime, timezone
from app.interfaces.http.dependencies import get_scheduler
from app.infrastructure.pddl.plan_parser import PDDLPlanParser
import os

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/run-plan")
async def run_plan_manually(
  background_tasks: BackgroundTasks,
  seconds_per_unit: float = Query(10.0, description="How many real SECONDS is 1.0 unit of PDDL worth?")
):
  """
  Manually trigger scheduling for quick tests.
  The default multiplier (0.0027) makes 1.0 in PDDL translate to 10 secondes in real life.
  """

  scheduler = get_scheduler()
  parser = PDDLPlanParser()

  scheduler.clear_all_jobs()

  multiplier_in_hours = seconds_per_unit / 3600.0

  ref_date = datetime.now(timezone.utc)

  try:
    with open("data/plan.pddl", "r", encoding="utf-8") as f:
      plan_content = f.read()

    actions = parser.parse_file(plan_content, ref_date, override_multiplier=multiplier_in_hours)

    background_tasks.add_task(scheduler.execute_plan_in_batches, actions, seconds_per_unit)

    return {
      "status": "Plan scheduled for testing",
      "reference_date": ref_date,
      "seconds_per_pddl_unit": seconds_per_unit,
      "actions_count": len(actions),
      "actions": [
        {
          "name": action.action_name,
          "scheduled_time": action.execution_time.isoformat()
        }
        for action in actions
      ]
    }
  except Exception as e:
    return {
      "status": "Error scheduling plan",
      "error": str(e)
    }
  
@router.get("/jobs")
async def list_scheduled_jobs(scheduler = Depends(get_scheduler)):
  jobs = scheduler.get_scheduled_jobs()
  jobs.sort(key=lambda x: x['next_run_time'] if x['next_run_time'] else "")

  return {
    "total_jobs": len(jobs),
    "jobs": jobs
  }

@router.delete("/jobs")
async def clear_all_scheduled_jobs(scheduler = Depends(get_scheduler)):
  scheduler.clear_all_jobs()
  return {"status": "all jobs cleared"}