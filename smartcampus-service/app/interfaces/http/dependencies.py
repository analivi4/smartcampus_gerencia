from app.application.use_cases.generate_pddl_use_case_impl import GeneratePDDLUseCaseImpl
from app.infrastructure.pddl.pddl_generator_v21 import PDDLGenerator
from app.application.use_cases.run_planner_use_case_impl import RunPlannerUseCaseImpl
from app.infrastructure.pddl.pddl_filesystem_service import PDDLFilesystemService
from app.infrastructure.planner.docker_planner_execution_service import DockerPlannerExecutionService
from app.infrastructure.scheduler.apscheduler_impl import APSchedulerImpl
from app.infrastructure.pddl.plan_parser import PDDLPlanParser

_scheduler_instance = None
_parser_instance = None

def get_plan_parser():
  global _parser_instance
  
  if _parser_instance is None:
    _parser_instance = PDDLPlanParser()

  return _parser_instance

def get_generate_pddl_use_case():
  return GeneratePDDLUseCaseImpl(pddl_generator=PDDLGenerator())

def get_run_planner_use_case():
  generate_pddl = get_generate_pddl_use_case()
  filesystem = PDDLFilesystemService()
  planner = DockerPlannerExecutionService()
  parser = get_plan_parser()
  scheduler = get_scheduler()

  return RunPlannerUseCaseImpl(
    generate_pddl_use_case=generate_pddl,
    filesystem_service=filesystem,
    planner_service=planner,
    parser=parser,
    scheduler=scheduler
  )

def get_scheduler():
  global _scheduler_instance
  
  if _scheduler_instance is None:
    _scheduler_instance = APSchedulerImpl()
    
  return _scheduler_instance