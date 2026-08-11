import json
import sys
import click
from failure_injection.runner import SCENARIOS, get_active_scenario, set_active_scenario
from diagnosis.engine import DiagnosisEngine, get_incident_by_id, list_incidents
from mcp.server import start_server
from agent.cli import agent_cli

@click.group()
def cli():
    """DataOps Agent CLI - Pipeline Observability & Incident Diagnosis Platform"""
    pass

@cli.command("inject")
@click.option("--scenario", "-s", type=click.Choice(list(SCENARIOS.keys())), help="Failure scenario to activate")
@click.option("--reset", "-r", is_flag=True, help="Reset active failure scenario to HEALTHY")
def inject_cmd(scenario, reset):
    """Inject a failure scenario or reset the system to healthy."""
    if reset:
        set_active_scenario(None)
        click.echo("Success: Reset failure injection framework. Pipeline restored to HEALTHY.")
        return

    if scenario:
        set_active_scenario(scenario)
        click.echo(f"Success: Activated failure scenario '{scenario}'.")
        click.echo(f"Description: {SCENARIOS[scenario]['description']}")
        click.echo(f"Expected Failure: {SCENARIOS[scenario]['expected_failure']}")
    else:
        click.echo("Please specify --scenario <name> or --reset. Use --help for details.")

@cli.command("reset")
def reset_cmd():
    """Reset all active failure scenarios to HEALTHY."""
    set_active_scenario(None)
    click.echo("Success: Reset failure injection framework. Pipeline restored to HEALTHY.")

@cli.group("incident")
def incident_group():
    """Manage and inspect pipeline incidents."""
    pass

@incident_group.command("list")
def incident_list_cmd():
    """List all detected incidents."""
    incidents = list_incidents()
    click.echo(f"\nTotal Incidents Recorded: {len(incidents)}\n")
    for inc in incidents:
        click.echo(f"Incident ID: {inc.incident_id}")
        click.echo(f"Status:      {inc.status.value}")
        click.echo(f"Severity:    {inc.severity.value.upper()}")
        click.echo(f"Root Cause:  {inc.probable_root_cause}")
        click.echo(f"Confidence:  {inc.confidence * 100:.1f}%\n" + "-" * 50)

@incident_group.command("inspect")
@click.argument("incident_id")
def incident_inspect_cmd(incident_id):
    """Inspect detailed evidence and status for a specific incident ID."""
    inc = get_incident_by_id(incident_id)
    if not inc:
        click.echo(f"Error: Incident ID '{incident_id}' not found.", err=True)
        sys.exit(1)

    click.echo(json.dumps(inc.model_dump(), indent=2))

@cli.command("diagnose")
@click.option("--incident-id", default=None, help="Optional incident ID to diagnose")
def diagnose_cmd(incident_id):
    """Run the deterministic diagnosis engine to analyze current pipeline health."""
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    click.echo("\n" + "=" * 60)
    click.echo("           DATAOPS AGENT INCIDENT DIAGNOSIS REPORT           ")
    click.echo("=" * 60)
    click.echo(f"Incident ID:          {incident.incident_id}")
    click.echo(f"Status:               {incident.status.value}")
    click.echo(f"Severity:             {incident.severity.value.upper()}")
    click.echo(f"Confidence Score:     {incident.confidence * 100:.1f}%")
    click.echo(f"Affected Assets:      {', '.join(incident.affected_assets) or 'None'}")
    click.echo(f"\nRoot Cause:\n  {incident.probable_root_cause}")
    click.echo(f"\nImpact:\n  {incident.impact}")
    click.echo("\nEvidence Collected:")
    for ev in incident.evidence:
        click.echo(f"  - {ev}")
    click.echo("\nRecommended Actions:")
    for act in incident.recommended_actions:
        click.echo(f"  - {act}")
    click.echo("=" * 60 + "\n")

@cli.group("mcp")
def mcp_group():
    """Model Context Protocol (MCP) server commands."""
    pass

@mcp_group.command("start")
def mcp_start_cmd():
    """Start the DataOps MCP Server on stdio transport."""
    start_server()

# Add agent sub-commands under dataops agent
cli.add_command(agent_cli, name="agent")

if __name__ == "__main__":
    cli()
