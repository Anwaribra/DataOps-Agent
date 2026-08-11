import pytest
from click.testing import CliRunner
from cli.main import cli
from failure_injection.scenarios import set_active_scenario

def test_cli_inject_and_reset():
    runner = CliRunner()
    res_inject = runner.invoke(cli, ["inject", "--scenario", "null_customer_id"])
    assert res_inject.exit_code == 0
    assert "Activated failure scenario 'null_customer_id'" in res_inject.output

    res_reset = runner.invoke(cli, ["reset"])
    assert res_reset.exit_code == 0
    assert "Reset failure injection framework" in res_reset.output

def test_cli_diagnose():
    runner = CliRunner()
    set_active_scenario("duplicate_order_id")
    res_diag = runner.invoke(cli, ["diagnose"])
    assert res_diag.exit_code == 0
    assert "DATAOPS AGENT INCIDENT DIAGNOSIS REPORT" in res_diag.output
    assert "duplicate order_id" in res_diag.output
    set_active_scenario(None)

def test_cli_incident_list():
    runner = CliRunner()
    res_list = runner.invoke(cli, ["incident", "list"])
    assert res_list.exit_code == 0
    assert "Total Incidents Recorded" in res_list.output
