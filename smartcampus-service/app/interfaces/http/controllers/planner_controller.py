from fastapi import APIRouter, HTTPException, Depends
from app.infrastructure.planner.planner_output_service import PlannerOutputService
from app.application.use_cases.run_planner_use_case import RunPlannerUseCase
from app.interfaces.http.schemas.environment_request import EnvironmentRequest
from app.interfaces.http.mappers.environment_mapper import map_environment_request_to_dto
from app.interfaces.http.dependencies import get_run_planner_use_case
from app.application.dto.environment_input_dto import EnvironmentInputDTO

router = APIRouter(prefix="/planner", tags=["Planner"])

@router.post("/run")
def run_planner(
  request: EnvironmentRequest,
  use_case: RunPlannerUseCase = Depends(get_run_planner_use_case)
):
  try:
    input_dto = map_environment_request_to_dto(request)

    result = use_case.execute(input_dto)
    return result

  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.get("/result/{job_id}")
def get_plan(job_id: str):
  """Recupera o resultado de um planejamento executado."""
  output_service = PlannerOutputService(job_id)

  if not output_service.is_ready():
    return {
      "job_id": job_id,
      "status": "not_found",
      "message": "Job not found in history. Check if it has completed.",
      "plan": None
    }
  
  try:
    metadata = output_service.get_metadata()
    plan = output_service.read_plan()
    error_log = output_service.get_error_log()
  except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))

  return {
    "job_id": job_id,
    "status": metadata.get("status"),
    "execution_time": metadata.get("execution_time"),
    "timestamp": metadata.get("timestamp"),
    "plan": plan,
    "error": error_log
  }


@router.get("/history")
def list_jobs():
  """Lista todos os planejamentos executados."""
  from app.infrastructure.pddl.pddl_filesystem_service import PDDLFilesystemService

  filesystem_service = PDDLFilesystemService()
  jobs = filesystem_service.list_jobs()

  return {
    "total": len(jobs),
    "jobs": jobs
  }