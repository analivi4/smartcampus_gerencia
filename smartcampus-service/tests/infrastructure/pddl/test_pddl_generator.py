from app.infrastructure.pddl.pddl_generator_v21 import PDDLGenerator
from app.application.dto.environment_input_dto import (
  ProblemDefinitionDTO, ObjectsDTO, InitDTO, GoalDTO, GoalPredicateDTO, TimedEventDTO
)

def test_generate_pddl_for_simple_enviroment():
  problem = ProblemDefinitionDTO(
    name="test_problem",
    domain="smart_campus",
    objects=ObjectsDTO(
      rooms=["sl1"],
      air_conditioners=["ac1"],
      lights=["l1", "l2"]
    ),
    init=InitDTO(
      fluents={
        "people_in_room": {"sl1": 5},
        "metric_total_cost": 0
      },
      timed_events=[
        TimedEventDTO(time=0.0, type="predicate", predicate="operating_hour")
      ]
    ),
    goal=GoalDTO(predicates=[
      GoalPredicateDTO(predicate="ac_off", args=["sl1", "ac1"]),
      GoalPredicateDTO(predicate="light_off", args=["sl1", "l1"]),
      GoalPredicateDTO(predicate="out_work_time")
    ]),
    metric="minimize (metric_total_cost)"
  )

  generator = PDDLGenerator()
  pddl = generator.generate(problem)

  assert "(define (problem test_problem)" in pddl
  assert "(:domain smart_campus)" in pddl
  assert "sl1 - room" in pddl
  assert "ac1 - air_conditioner" in pddl
  assert "l1 l2 - light" in pddl
  assert "(= (people_in_room sl1) 5)" in pddl
  assert "(at 0.0 (operating_hour))" in pddl
  assert "(ac_off sl1 ac1)" in pddl
  assert "(light_off sl1 l1)" in pddl
  assert "(out_work_time)" in pddl
  assert "(:metric minimize (metric_total_cost))" in pddl


def test_generate_pddl_negated_predicate_til():
  problem = ProblemDefinitionDTO(
    name="test_reset",
    domain="smart_campus",
    objects=ObjectsDTO(rooms=["sl1"], air_conditioners=["ac1"], lights=["l1"]),
    init=InitDTO(
      fluents={"people_in_room": {"sl1": 0}, "metric_total_cost": 0},
      timed_events=[
        TimedEventDTO(time=0.0, type="predicate", predicate="operating_hour"),
        TimedEventDTO(time=5.0, type="negated_predicate", predicate="ac_on",  args=["sl1", "ac1"]),
        TimedEventDTO(time=5.0, type="negated_predicate", predicate="ac_off", args=["sl1", "ac1"]),
      ]
    ),
    goal=GoalDTO(predicates=[GoalPredicateDTO(predicate="ac_off", args=["sl1", "ac1"])]),
    metric="minimize (metric_total_cost)"
  )

  pddl = PDDLGenerator().generate(problem)

  assert "(at 5.0 (not (ac_on sl1 ac1)))" in pddl
  assert "(at 5.0 (not (ac_off sl1 ac1)))" in pddl
