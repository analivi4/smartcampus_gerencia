from typing import List
from .room import Room

class Environment:
  def __init__(self, name: str, rooms: List[Room]):
    self._name = name
    self._rooms = rooms

  @property
  def name(self) -> str:
    return self._name

  @property
  def rooms(self) -> List[Room]:
    return self._rooms