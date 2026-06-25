from abc import ABC, abstractmethod

class GeneratePDDLUseCase(ABC):
  @abstractmethod
  def execute(self, input_data: dict) -> str:
    pass