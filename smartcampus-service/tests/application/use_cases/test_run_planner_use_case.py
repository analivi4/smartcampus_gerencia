from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from app.application.use_cases.run_planner_use_case_impl import RunPlannerUseCaseImpl

def test_execute_planner_success_calls_scheduler():
  gen_pddl_mock = MagicMock()
  fs_mock = MagicMock()
  planner_mock = MagicMock()
  parser_mock = MagicMock()
  scheduler_mock = MagicMock()

  planner_mock.create_job.return_value = "job123"
  planner_mock.run.return_value = {"success": True, "execution_time": 1.5}
  fs_mock.get_plan_path.return_value = "fake_path.txt"

  mock_action = MagicMock()
  parser_mock.parse_file.return_value = [mock_action]

  mock_path = MagicMock(spec=Path)
  mock_path.exists.return_value = True
  mock_path.stat.return_value = MagicMock(st_size=100)

  with patch("app.application.use_cases.run_planner_use_case_impl.Path", return_value=mock_path):
    with patch("builtins.open", mock_open(read_data="0.001: (start_campus_operating)  [15.000]")):
      use_case = RunPlannerUseCaseImpl(
        generate_pddl_use_case=gen_pddl_mock,
        filesystem_service=fs_mock,
        planner_service=planner_mock,
        parser=parser_mock,
        scheduler=scheduler_mock
      )

      result = use_case.execute(input_data={"test": "data"})

      assert result["job_id"] == "job123"
      assert result["scheduled_actions_count"] == 1

      scheduler_mock.schedule_many.assert_called_once()
      fs_mock.archive_job.assert_called_with("job123", "success", 1.5)
