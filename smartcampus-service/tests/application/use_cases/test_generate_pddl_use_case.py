from app.application.use_cases.generate_pddl_use_case_impl import GeneratePDDLUseCaseImpl
from app.application.dto.environment_input_dto import (
  ProblemDefinitionDTO, ObjectsDTO, InitDTO, GoalDTO, GoalPredicateDTO
)
from tests.application.fakes.fake_pddl_generator import FakePDDLGenerator

def test_generate_pddl_use_case_happy_path():
  fake_generator = FakePDDLGenerator()
  use_case = GeneratePDDLUseCaseImpl(fake_generator)

  input_dto = ProblemDefinitionDTO(
    name="bl1",
    domain="smart_campus",
    objects=ObjectsDTO(
      rooms=["sl1"],
      air_conditioners=["ac1"],
      lights=["l1"]
    ),
    init=InitDTO(
      fluents={"people_in_room": {"sl1": 5}, "metric_total_cost": 0},
      timed_events=[]
    ),
    goal=GoalDTO(predicates=[GoalPredicateDTO(predicate="out_work_time")])
  )

  result = use_case.execute(input_dto)

  assert result == "FAKE_PDDL_OUTPUT"
  assert fake_generator.called_with.name == "bl1"
  assert fake_generator.called_with.domain == "smart_campus"
  assert fake_generator.called_with.objects.rooms == ["sl1"]
  assert fake_generator.called_with.objects.air_conditioners == ["ac1"]
