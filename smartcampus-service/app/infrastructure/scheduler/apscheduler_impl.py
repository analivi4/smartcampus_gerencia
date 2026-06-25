import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .scheduler_interface import IScheduler
from app.domain.entities.plan import ScheduleAction
from itertools import groupby
import httpx
import logging
import asyncio

class APSchedulerImpl(IScheduler):
  def __init__(self, base_url: str = None, api_key: str = None, client: httpx.AsyncClient = None, timezone="UTC"):
    self.logger = logging.getLogger(__name__)
    self.base_url = base_url or os.getenv("ORION_URL", "")
    self.api_key = api_key or os.getenv("IOT_API_KEY")
    self.fiware_service = os.getenv("FIWARE_SERVICE", "smartufc")
    self.fiware_service_path = os.getenv("FIWARE_SERVICE_PATH", "/campusquixada")

    try:
      loop = asyncio.get_running_loop()

    except RuntimeError:
      loop = None

    if loop is not None:
      self.scheduler = AsyncIOScheduler(event_loop=loop, timezone=timezone)
    else:
      self.scheduler = AsyncIOScheduler(timezone=timezone)

    self._client_provided = client is not None
    self.client = client or httpx.AsyncClient(timeout=10.0)
    self.scheduler.start()

  async def _execute_iot_call(self, action: ScheduleAction):
    self.logger.info("Executing action %s for device %s at %s", action.action_name, action.target_device_id, action.execution_time)

    if action.command == "UNKNOWN":
      self.logger.warning("Unknown command for action %s, skipping", action.action_name)
      return

    if action.command == "ON":
      orion_command, orion_value = "ligar", "1"
    elif action.command == "OFF":
      orion_command, orion_value = "desligar", "0"
    else:
      self.logger.warning("Unhandled command %s for action %s, skipping", action.command, action.action_name)
      return

    try:
      url = f"{self.base_url}/v2/entities/{action.target_device_id}/attrs"
      params = {"type": "Atuador"}
      payload = {orion_command: {"type": "command", "value": orion_value}}
      headers = {
        "Content-Type": "application/json",
        "fiware-service": self.fiware_service,
        "fiware-servicepath": self.fiware_service_path
      }

      self.logger.warning("Orion PATCH → %s | service=%s | servicepath=%s | body=%s", url, self.fiware_service, self.fiware_service_path, payload)

      for attempt in range(3):
        response = await self.client.patch(url, json=payload, headers=headers, params=params)

        if response.status_code < 400:
          self.logger.info("Action %s executed successfully: %s", action.action_name, response.status_code)
          break
        else:
          self.logger.warning("Attempt %d failed: %s — %s", attempt + 1, response.status_code, response.text[:200])
          await asyncio.sleep(2 ** attempt)
      else:
        self.logger.error("Failed to call Orion for action %s", action.action_name)

    except Exception:
      self.logger.exception("Error calling Orion")

  def schedule_action(self, action: ScheduleAction):
    job_id = f"{action.action_name}:{action.target_device_id}:{action.execution_time.isoformat()}"
    
    self.scheduler.add_job(
      self._execute_iot_call,
      'date',
      run_date=action.execution_time,
      args=[action],
      id=job_id,
      replace_existing=True
    )

  def schedule_many(self, actions: list[ScheduleAction]):
    self.logger.info(f"Scheduling {len(actions)} actions from plan...")

    INTERNAL_ACTIONS = {'start_campus_operating', 'acknowledge_class'}
    actions_to_schedule = [a for a in actions if a.action_name not in INTERNAL_ACTIONS]

    for action in actions_to_schedule:
      try:
        self.schedule_action(action)

      except Exception as e:
        self.logger.error(f"Failed to schedule action {action.action_name} for device {action.target_device_id}: {e}")

    self.logger.info("All relevant actions have been scheduled in the timeline.")

  async def execute_plan_in_batches(self, actions: list[ScheduleAction], seconds_per_unit: float):
    filtered_actions = [a for a in actions if a.action_name != 'start_campus_operating']
    groups = groupby(filtered_actions, key=lambda x: x.execution_time)

    for execution_time, group in groups:
      batch = list(group)

      if not batch:
        continue

      self.logger.info(f"--- Starting batch: {len(batch)} action for time {execution_time} ---")

      tasks = [self._execute_iot_call(action) for action in batch]
      await asyncio.gather(*tasks)

      avg_duration = sum(a.duration for a in batch) / len(batch)
      wait_time = avg_duration * seconds_per_unit

      self.logger.info(f"Batch completed. Expected average duration: {wait_time:.2f}s")

      await asyncio.sleep(wait_time)

    self.logger.info(f"Sequential plan execution completed successfully.")

  def clear_all_jobs(self):
    """Remove all pending appointments from the scheduler."""
    try:
      self.scheduler.remove_all_jobs()
      self.logger.info("All scheduled jobs have been cleared.")
    except Exception as e:
      self.logger.error(f"Error clearing scheduled jobs: {e}")

  def get_scheduled_jobs(self):
    """Return a list of all currently scheduled jobs."""
    jobs = self.scheduler.get_jobs()
    job_list = []
    for job in jobs:
      job_list.append({
        "id": job.id,
        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        "function": job.func.__name__,
        "args": str(job.args),
      })
    return job_list
  
  async def shutdown(self):
    self.logger.info("Shutting down scheduler")
    self.scheduler.shutdown(wait=False)

    if not self._client_provided:
      await self.client.aclose()