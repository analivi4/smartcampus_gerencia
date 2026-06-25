import os
import re
from datetime import datetime, timedelta, timezone
from app.domain.entities.plan import ScheduleAction

class PDDLPlanParser:
  def __init__(self, time_unit_to_hours: float = None):
    env_val = os.getenv("APP_TIME_UNIT_TO_HOURS")

    if time_unit_to_hours is None:
      if env_val:
        time_unit_to_hours = float(env_val)
      else:
        time_unit_to_hours = 1
    
    self.time_multiplier = time_unit_to_hours
    self.pattern = r"(\d+\.\d+):\s*\(\s*(\w+)(?:\s+(.*?))?\)\s*\[(\d+\.\d+)\]"
    self.action_map = {
      "turn_on_light": "ON",
      "turn_off_light": "OFF",
      "turn_on_air_conditioner": "ON",
      "turn_on_air_conditioner_peak_hours": "ON",
      "turn_off_air_conditioner": "OFF",
      "set_ac_temperature_25": "SET_TEMP_25",
      "start_campus_operating": "START"
    }

  def parse_file(self, file_content: str, reference_date: datetime, override_multiplier: float = None) -> list[ScheduleAction]:
    actions = []

    multiplier = override_multiplier if override_multiplier is not None else self.time_multiplier

    if reference_date.tzinfo is None:
      ref_aware = reference_date.replace(tzinfo=timezone.utc)
    else:
      ref_aware = reference_date

    for line in file_content.splitlines():
      match = re.search(self.pattern, line)

      if not match:
        continue

      raw_time = float(match.group(1))
      action_name = match.group(2)
      params_raw = match.group(3) or ""
      params = params_raw.strip().split() if params_raw.strip() else []
      duration = float(match.group(4))

      room_id = params[0] if len(params) > 0 else None
      device_id = params[-1] if params else None
      
      command = self.action_map.get(action_name, "UNKNOWN")

      if reference_date.tzinfo is None:
        reference_date = reference_date.replace(tzinfo=timezone.utc)

      execution_time = ref_aware + timedelta(hours=raw_time * multiplier)

      actions.append(ScheduleAction(
        execution_time=execution_time,
        action_name=action_name,
        target_device_id=device_id,
        command=command,
        duration=duration
      ))

    return actions