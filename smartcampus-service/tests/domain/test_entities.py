from app.domain.entities.air_conditioner import AirConditioner
from app.domain.entities.light import Light
from app.domain.entities.room import Room
from app.domain.entities.environment import Environment

def test_environment_with_room_and_devices():
  ac1 = AirConditioner("ac1")
  l1 = Light("l1")
  sl1 = Room(name="sl1", type="room", occupancy=5, devices=[ac1, l1])
  environment = Environment(name="bl1", rooms=[sl1])

  assert environment.name == "bl1"
  assert len(environment.rooms) == 1  
  assert environment.rooms[0].name == "sl1"
  assert len(environment.rooms[0].devices) == 2
  assert environment.rooms[0].devices[0].id == "ac1"
  assert environment.rooms[0].devices[1].id == "l1"