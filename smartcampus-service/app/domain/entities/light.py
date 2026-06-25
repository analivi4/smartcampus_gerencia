from .device import Device

class Light(Device):
  @property
  def device_type(self) -> str:
    return "light"