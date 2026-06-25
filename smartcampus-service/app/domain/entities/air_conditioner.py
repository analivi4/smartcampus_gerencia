from .device import Device

class AirConditioner(Device):
  @property
  def device_type(self) -> str:
    return "air_conditioner"