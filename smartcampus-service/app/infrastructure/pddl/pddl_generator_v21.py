from app.application.dto.environment_input_dto import ProblemDefinitionDTO
from app.domain.interfaces.pddl_generator import PDDLGenerator as IPDDLGenerator

class PDDLGenerator(IPDDLGenerator):
  def generate(self, prob: ProblemDefinitionDTO) -> str:
    lines = [
      f"(define (problem {prob.name})",
      f"  (:domain {prob.domain})",
      "",
      self._generate_objects(prob.objects),
      "",
      self._generate_init(prob.init),
      "",
      self._generate_goal(prob.goal),
      ""
    ]

    if prob.metric:
      lines.append(f"  (:metric {prob.metric})")
    
    lines.append(")")
    return "\n".join(lines)

  def _generate_objects(self, obj_dto) -> str:
    lines = ["  (:objects"]

    mapping = {
      "room": obj_dto.rooms,
      "air_conditioner": obj_dto.air_conditioners,
      "light": obj_dto.lights,
      "slot": obj_dto.slots or []
    }

    for pddl_type, items in mapping.items():
      if items:
        lines.append(f"    {' '.join(items)} - {pddl_type}")
            
    lines.append("  )")
    return "\n".join(lines)

  def _generate_init(self, init_dto) -> str:
    lines = ["  (:init"]
    
    # 1. Initial Fluents
    for name, data in init_dto.fluents.items():
      if isinstance(data, dict):
        for arg, val in data.items():
          lines.append(f"    (= ({name} {arg}) {val})")
          
      else:
        lines.append(f"    (= ({name}) {data})")
    
    lines.append("")

    # 2. Timed Events (Timed Initial Literals)
    for event in init_dto.timed_events:
      time_val = f"{event.time:.3f}"

      if event.type == "predicate":
        args = f" {' '.join(event.args)}" if event.args else ""
        lines.append(f"    (at {time_val} ({event.predicate}{args}))")

      elif event.type == "negated_predicate":
        args = f" {' '.join(event.args)}" if event.args else ""
        lines.append(f"    (at {time_val} (not ({event.predicate}{args})))")

      elif event.type == "fluent":
        args = f" {' '.join(event.args)}" if event.args else ""
        lines.append(f"    (at {time_val} (= ({event.fluent}{args}) {event.value}))")
    
    lines.append("  )")
    return "\n".join(lines)

  def _generate_goal(self, goal_dto) -> str:
    lines = ["  (:goal", "    (and"]

    for pred in goal_dto.predicates:
      args = f" {' '.join(pred.args)}" if pred.args else ""
      lines.append(f"      ({pred.predicate}{args})")
      
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)