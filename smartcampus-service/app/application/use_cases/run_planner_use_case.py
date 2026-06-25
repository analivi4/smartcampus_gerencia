from abc import ABC, abstractmethod
from app.application.dto.environment_input_dto import EnvironmentInputDTO

class RunPlannerUseCase(ABC):
  @abstractmethod
  def execute(self, input_data: EnvironmentInputDTO) -> str:
    """Triggers the planning process and returns the job_id."""