from fastapi import APIRouter, Request, Header
import logging

router = APIRouter(prefix="/device", tags=["Mock IoT API"])
logger = logging.getLogger("mock_iot_api")

@router.post("/{device_id}/control")
async def mock_control_endpoint(
  device_id: str,
  request: Request,
  authorization: str = Header(None)
):
  body = await request.json()

  print(f"\n[MOCK API] CALL RECEIVED:")
  print(f"  Device ID: {device_id}")
  print(f"  Command: {body.get('command')}")
  print(f"  Duration: {body.get('duration')}")
  print(f"  Authorization: {authorization}\n")

  return {"status": "success", "device": device_id, "received": body}
  