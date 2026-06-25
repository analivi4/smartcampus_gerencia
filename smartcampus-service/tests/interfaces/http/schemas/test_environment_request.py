from app.interfaces.http.schemas.environment_request import EnvironmentRequest

def test_environment_request_schema():
  data = {
    "name": "bl1",
    "domain": "smart_campus",
    "objects": {
      "rooms": ["sl1"],
      "air_conditioners": ["ac1"],
      "lights": ["l1", "l2"]
    },
    "init": {
      "fluents": {
        "people_in_room": {"sl1": 5},
        "metric_total_cost": 0
      },
      "timed_events": [
        {"time": 0.0, "type": "predicate", "predicate": "operating_hour"}
      ]
    },
    "goal": {
      "predicates": [
        {"predicate": "ac_off", "args": ["sl1", "ac1"]},
        {"predicate": "light_off", "args": ["sl1", "l1"]}
      ]
    },
    "metric": "minimize (metric_total_cost)"
  }

  env = EnvironmentRequest(**data)

  assert env.name == "bl1"
  assert env.domain == "smart_campus"
  assert env.objects.rooms == ["sl1"]
  assert env.objects.air_conditioners == ["ac1"]
  assert env.init.timed_events[0].predicate == "operating_hour"
  assert env.goal.predicates[0].predicate == "ac_off"
  assert env.metric == "minimize (metric_total_cost)"
