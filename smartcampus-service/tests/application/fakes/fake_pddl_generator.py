from app.domain.interfaces.pddl_generator import PDDLGenerator

class FakePDDLGenerator(PDDLGenerator):
  def __init__(self):
    self.called_with = None

  def generate(self, environment):
    self.called_with = environment
    return "FAKE_PDDL_OUTPUT"