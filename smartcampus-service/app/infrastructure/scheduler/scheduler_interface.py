from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.plan import ScheduleAction

class IScheduler(ABC):
  @abstractmethod
  def schedule_action(self, action: ScheduleAction):
    pass

  @abstractmethod
  def schedule_many(self, actions: List[ScheduleAction]):
    pass

  @abstractmethod
  def clear_all_jobs(self):
    pass

  @abstractmethod
  def get_scheduled_jobs(self) -> list:
    pass

  @abstractmethod
  async def shutdown(self):
    pass
