import pytest

from app.domain.factories.device_factory import DeviceFactory
from app.domain.entities.air_conditioner import AirConditioner
from app.domain.entities.light import Light

def test_create_air_conditioner():
  device = DeviceFactory.create(device_type='air_conditioner', device_id='ac1')
  assert isinstance(device, AirConditioner)
  assert device.id == "ac1"

def test_create_light():
  device = DeviceFactory.create(device_type='light', device_id='l1')
  assert isinstance(device, Light)
  assert device.id == "l1"

def test_unsupported_device_type():
  with pytest.raises(ValueError):
    DeviceFactory.create(device_type='sensor', device_id='s1')