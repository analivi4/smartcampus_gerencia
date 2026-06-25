from app.interfaces.http.schemas.environment_request import (
  EnvironmentRequest
)
from app.application.dto.environment_input_dto import (
  ProblemDefinitionDTO, TimedEventDTO, InitDTO, GoalDTO, GoalPredicateDTO, ObjectsDTO
)

def map_environment_request_to_dto(request: EnvironmentRequest) -> ProblemDefinitionDTO:
  return ProblemDefinitionDTO(
    name=request.name,
    domain=request.domain,
    objects=ObjectsDTO(
      rooms=request.objects.rooms,
      air_conditioners=request.objects.air_conditioners,
      lights=request.objects.lights,
      slots=request.objects.slots
    ),
    init=InitDTO(
      fluents=request.init.fluents,
      timed_events=[
        TimedEventDTO(**event.model_dump()) for event in request.init.timed_events
      ]
    ),
    goal=GoalDTO(
      predicates=[
        GoalPredicateDTO(predicate=p.predicate, args=p.args)
        for p in request.goal.predicates
      ]
    ),
    metric=request.metric,
    device_map=request.device_map
  )
