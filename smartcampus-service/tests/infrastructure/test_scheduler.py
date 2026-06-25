from datetime import datetime, timezone, timedelta
from app.infrastructure.scheduler.apscheduler_impl import APSchedulerImpl
from app.domain.entities.plan import ScheduleAction
from httpx import Response, Request, codes
import asyncio
import pytest
import httpx
import json

@pytest.mark.asyncio
async def test_scheduler_sends_http_request():
    events = []

    async def handler(request: Request):
        body = json.loads(request.content.decode("utf-8"))
        events.append({"url": str(request.url), "json": body})
        return Response(status_code=200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    scheduler = APSchedulerImpl(base_url="http://testserver", api_key="key", client=client, timezone="UTC")

    exec_time = datetime.now(timezone.utc) + timedelta(seconds=2)
    action = ScheduleAction(
        execution_time=exec_time,
        action_name="turn_on_light_during_class",
        target_device_id="bl1_sl1_light1",
        command="ON",
        duration=0.2
    )
    scheduler.schedule_action(action)

    for _ in range(30):
        if len(events) > 0:
            break
        await asyncio.sleep(0.1)

    await scheduler.shutdown()
    await client.aclose()

    assert len(events) == 1
    assert "/v2/entities/bl1_sl1_light1/attrs" in events[0]["url"]
    assert events[0]["json"] == {"ligar": {"type": "command", "value": "1"}}