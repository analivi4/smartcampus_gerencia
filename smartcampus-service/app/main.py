from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORS
from contextlib import asynccontextmanager
from app.interfaces.http.controllers.pddl_controller import router as pddl_router
from app.interfaces.http.controllers.planner_controller import router as planner_router
from app.interfaces.http.controllers.scheduler_controller import router as scheduler_router
from app.interfaces.http.controllers.mock_api_controller import router as mock_api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
  from app.interfaces.http.dependencies import get_scheduler

  scheduler = get_scheduler()
  app.state.scheduler = scheduler

  yield

  await scheduler.shutdown()

  # try:
  #   with open("data/plan.pddl", "r", encoding="utf-8") as f:
  #     pddl_content = f.read()

  #   reference_date = datetime.now(timezone.utc).replace(hour=7, minute=0, second=0, microsecond=0)

  #   actions = parser.parse_file(pddl_content, reference_date)

  #   scheduler.schedule_many(actions)
  #   app.state.scheduler = scheduler   
    
  # except FileNotFoundError:
  #   print("plan.pddl file not found. Scheduler will not be initialized.")
  
  # yield
  
  # if hasattr(app.state, "scheduler"):
  #   await app.state.scheduler.shutdown()

origins = [
  "http://localhost:5173",
  "http://127.0.0.1:5173"
]

app = FastAPI(title="Smart Campus Service", lifespan=lifespan)

app.add_middleware(CORS, allow_origins=origins, allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

app.include_router(pddl_router)
app.include_router(planner_router)
app.include_router(scheduler_router)
app.include_router(mock_api_router)