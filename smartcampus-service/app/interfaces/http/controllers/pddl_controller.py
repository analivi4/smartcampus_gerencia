from fastapi import APIRouter, Depends
from app.interfaces.http.schemas.environment_request import EnvironmentRequest
from app.interfaces.http.mappers.environment_mapper import map_environment_request_to_dto
from app.application.use_cases.generate_pddl_use_case import GeneratePDDLUseCase
from app.interfaces.http.dependencies import get_generate_pddl_use_case

router = APIRouter(prefix="/pddl", tags=["PDDL"])

@router.post("", response_model=str)
def generate_pddl(
  request: EnvironmentRequest,
  use_case: GeneratePDDLUseCase = Depends(get_generate_pddl_use_case)
):
  input_dto = map_environment_request_to_dto(request)
  return use_case.execute(input_dto)