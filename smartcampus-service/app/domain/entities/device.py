from abc import ABC, abstractmethod

class Device(ABC):
  def __init__(self, device_id: str):
    self._id = device_id

  @property
  def id(self) -> str:
    return self._id

  @property
  @abstractmethod
  def device_type(self) -> str:
    pass