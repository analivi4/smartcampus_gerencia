from datetime import datetime, timezone
from app.infrastructure.pddl.plan_parser import PDDLPlanParser

def test_pddl_parser_conversion():
  parser = PDDLPlanParser(time_unit_to_hours=10.0)
  reference_time = datetime(2023, 1, 1, 8, 0, 0)

  plan_text = "0.100: (turn_on_light room1 l1) [0.200]"

  actions = parser.parse_file(plan_text, reference_time)

  assert len(actions) == 1
  assert actions[0].execution_time == datetime(2023, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
  assert actions[0].target_device_id == "l1"
  assert actions[0].command == "ON"

def test_pddl_parser_invalid_line():
  parser = PDDLPlanParser()
  actions = parser.parse_file("This is not a valid line", datetime.now())
  assert len(actions) == 0