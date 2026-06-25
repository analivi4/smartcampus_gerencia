from typing import Type, Dict
from app.domain.entities.device import Device
from app.domain.entities.air_conditioner import AirConditioner
from app.domain.entities.light import Light

class DeviceFactory:
  _register: Dict[str, Type[Device]] = {
    "air_conditioner": AirConditioner,
    "light": Light
  }

  @classmethod
  def create(cls, device_type: str, device_id: str) -> Device:
    device_class = cls._register.get(device_type)

    if not device_class:
      raise ValueError(f"Unknown device type: {device_type}")

    return device_class(device_id)