from app.application.dto.environment_input_dto import (
  EnvironmentInputDTO,
  RoomInputDTO,
  DeviceInputDTO
)

def test_environment_input_dto_creation():
  dto = EnvironmentInputDTO(
    name="bl1",
    rooms=[
      RoomInputDTO(
        name="sl1",
        type="room",
        occupancy=5,
        devices=[
          DeviceInputDTO(id="ac1", type="air_conditioner"),
          DeviceInputDTO(id="l1", type="light")
        ]
      )
    ]
  )

  assert dto.name == "bl1"
  assert dto.rooms[0].devices[0].id == "ac1"
  assert dto.rooms[0].devices[1].type == "light"