import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

async def send_action(
  client: httpx.AsyncClient,
  device_id: str,
  command: str,
  fiware_service: str = "openiot",
  fiware_service_path: str = "/",
):
  if command == "ON":
    orion_command, orion_value = "ligar", "1"
  elif command == "OFF":
    orion_command, orion_value = "desligar", "0"
  else:
    logger.warning("Unhandled command %s for device %s, skipping", command, device_id)
    return

  url = f"/v2/entities/{device_id}/attrs"
  params = {"type": "Atuador"}
  payload = {orion_command: {"type": "command", "value": orion_value}}
  headers = {
    "Content-Type": "application/json",
    "fiware-service": fiware_service,
    "fiware-servicepath": fiware_service_path,
  }

  for attempt in range(3):
    try:
      response = await client.patch(url, json=payload, headers=headers, params=params)
      response.raise_for_status()
      logger.info("Sent action %s to %s: %s", command, device_id, response.status_code)
      return response

    except Exception as e:
      logger.warning("Attempt %d failed sending to %s: %s", attempt + 1, device_id, e)
      await asyncio.sleep(2 ** attempt)

  raise RuntimeError("Failed to send action after retries")
