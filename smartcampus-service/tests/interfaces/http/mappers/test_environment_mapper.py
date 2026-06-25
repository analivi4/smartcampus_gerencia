from app.interfaces.http.schemas.environment_request import EnvironmentRequest
from app.interfaces.http.mappers.environment_mapper import map_environment_request_to_dto

def test_environment_request_to_dto_mapper():
  request = EnvironmentRequest(
    name="bl1",
    domain="smart_campus",
    objects={
      "rooms": ["sl1"],
      "air_conditioners": ["ac1"],
      "lights": ["l1"]
    },
    init={
      "fluents": {"people_in_room": {"sl1": 5}, "metric_total_cost": 0},
      "timed_events": []
    },
    goal={
      "predicates": [{"predicate": "out_work_time"}]
    }
  )

  dto = map_environment_request_to_dto(request)

  assert dto.name == "bl1"
  assert dto.domain == "smart_campus"
  assert dto.objects.rooms == ["sl1"]
  assert dto.objects.air_conditioners == ["ac1"]
  assert dto.goal.predicates[0].predicate == "out_work_time"
