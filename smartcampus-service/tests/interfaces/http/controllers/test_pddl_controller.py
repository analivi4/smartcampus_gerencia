from fastapi.testclient import TestClient
from app.main import app
from app.interfaces.http.dependencies import get_generate_pddl_use_case
from tests.interfaces.http.fakes.fake_use_case import FakeGeneratePDDLUseCase

client = TestClient(app)

def override_use_case():
  return FakeGeneratePDDLUseCase()

app.dependency_overrides[get_generate_pddl_use_case] = override_use_case

VALID_PAYLOAD = {
  "name": "test-problem",
  "domain": "smart_campus",
  "objects": {
    "rooms": ["sl1"],
    "air_conditioners": ["ac1"],
    "lights": ["l1"]
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
      {"predicate": "out_work_time"}
    ]
  }
}

def test_generate_pddl_endpoint():
  response = client.post("/pddl", json=VALID_PAYLOAD)

  assert response.status_code == 200
  assert response.json() == "FAKE_PDDL_FROM_API"
