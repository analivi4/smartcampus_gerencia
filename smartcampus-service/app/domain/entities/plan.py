from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScheduleAction(BaseModel):
  execution_time: datetime
  action_name: str
  target_device_id: Optional[str]
  command: str
  duration: float