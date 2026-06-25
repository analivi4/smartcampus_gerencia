from datetime import datetime, timezone, timedelta
from app.infrastructure.pddl.plan_parser import PDDLPlanParser
import asyncio

def test_parse_plan_file_basic():
  with open('data/plan.pddl', 'r', encoding='utf-8') as f:
    plan_content = f.read()

  reference_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
  parser = PDDLPlanParser()
  actions = parser.parse_file(plan_content, reference_date)
  assert len(actions) >= 1
  
  a_start = next((a for a in actions if a.action_name == 'start_campus_operating'), None)
  assert a_start is not None
  expected_hours = 0.001 * parser.time_multiplier
  assert a_start.execution_time == reference_date + timedelta(hours=expected_hours)

  a_light = next((a for a in actions if a.action_name == 'turn_on_light'), None)
  assert a_light is not None
  expected_light_time = reference_date + timedelta(hours=1.001 * parser.time_multiplier)
  assert a_light.execution_time == expected_light_time