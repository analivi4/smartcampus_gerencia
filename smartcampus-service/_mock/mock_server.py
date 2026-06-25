from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/device/{device_id}/control")
async def control(device_id: str, request: Request):
    body = await request.json()
    print("MOCK RECEIVED:", device_id, body)
    return {"status": "ok", "device": device_id, "body": body}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)