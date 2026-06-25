from typing import List
from .device import Device

class Room:
  def __init__(self, name: str, type: str, occupancy: int, devices: List[Device]):
    self._name = name
    self._type = type
    self._occupancy = occupancy
    self._devices = devices

  @property
  def name(self) -> str:
    return self._name
  
  @property
  def occupancy(self) -> int:
    return self._occupancy

  @property
  def type(self) -> str:
    return self._type

  @property
  def devices(self) -> List[Device]:
    return self._devices