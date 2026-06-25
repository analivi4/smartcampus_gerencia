from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class EnvType(str, Enum):
  AIR_CONDITIONER = "air_conditioner"
  LIGHT = "light"
  ROOM = "room"
  PROJECTOR = "projector"

class DeviceSchema(BaseModel):
  id: str = Field(..., example="ac1")
  type: EnvType = Field(..., example="air_conditioner")

class RoomSchema(BaseModel):
  id: str = Field(..., example="sala1")
  type: EnvType = Field(..., example="room")
  devices: List[DeviceSchema] = Field(..., example=[
    {"id": "ac1", "type": "air_conditioner"},
    {"id": "light1", "type": "light"}
  ])

class EnvSchema(BaseModel):
  environment: str = Field(..., example="bloco1")
  rooms: List[RoomSchema] = Field(..., example=[
    {
      "id": "sala1",
      "type": "room",
      "devices": [
        {"id": "ac1", "type": "air_conditioner"},
        {"id": "light1", "type": "light"}
      ]
    },
    {
      "id": "sala2",
      "type": "room",
      "devices": [
        {"id": "proj1", "type": "projector"},
        {"id": "light2", "type": "light"}
      ]
    }
  ])