from abc import ABC, abstractmethod
from typing import Any

class PDDLGenerator(ABC):
  @abstractmethod
  def generate(self, input_data: Any) -> str:
    pass