from app.application.use_cases.generate_pddl_use_case import GeneratePDDLUseCase
from app.application.dto.environment_input_dto import EnvironmentInputDTO, ProblemDefinitionDTO
from app.domain.entities.environment import Environment
from app.domain.entities.room import Room
from app.domain.factories.device_factory import DeviceFactory
from app.domain.interfaces.pddl_generator import PDDLGenerator

class GeneratePDDLUseCaseImpl(GeneratePDDLUseCase):
  def __init__(self, pddl_generator: PDDLGenerator):
    self._pddl_generator = pddl_generator

  def execute(self, input_data: ProblemDefinitionDTO) -> str:
    return self._pddl_generator.generate(input_data)

  def _build_domain(self, input_data: EnvironmentInputDTO) -> Environment:
    rooms = []

    for room_dto in input_data.rooms:
      devices = [
        DeviceFactory.create(
          device_id=device_dto.id,
          device_type=device_dto.type
        )
        for device_dto in room_dto.devices
      ]

      room = Room(
        name=room_dto.name,
        type=room_dto.type,
        occupancy=room_dto.occupancy,
        devices=devices
      )

      rooms.append(room)

    return Environment(
      name=input_data.name,
      rooms=rooms
    )