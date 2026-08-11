import json
import os
import sys
import click
from agent.agent import DataOpsAgent
from agent.client import DataOpsMCPClient
from agent.provider import get_llm_provider
from remediation.approval import approval_service
from remediation.executor import executor
from remediation.planner import planner
from remediation.verifier import verifier

@click.group()
def agent_cli():
    """AI DataOps Agent CLI - Incident Investigation & Operational Reasoning Platform"""
    pass

@agent_cli.command("investigate")
@click.argument("incident_id")
def investigate_cmd(incident_id: str):
    """Investigate a pipeline incident using MCP tools and generate an evidence-based diagnosis."""
    click.echo(f"Initializing AI DataOps Agent for incident '{incident_id}'...")
    agent = DataOpsAgent()
    diagnosis = agent.investigate(incident_id)
    click.echo(diagnosis.to_formatted_report())

    # Automatically propose remediation plan
    plan = planner.create_plan_from_diagnosis(diagnosis)
    approval_service.register_plan(plan)
    click.echo(f"Proposed Remediation Plan Registered: '{plan.plan_id}' (Status: {plan.status.value})")
    click.echo(f"Run 'dataops-agent remediation inspect {plan.plan_id}' or approve via 'dataops-agent remediation approve {plan.plan_id}'.\n")

@agent_cli.command("tools")
def tools_cmd():
    """List available MCP tools discovered by the DataOps Agent."""
    client = DataOpsMCPClient()
    connected = client.connect()
    if not connected:
        click.echo("Error: Could not connect to MCP Server.", err=True)
        sys.exit(1)

    tools = client.list_tools()
    click.echo(f"\nDiscovered {len(tools)} MCP Tools:\n")
    for t in tools:
        click.echo(f"Tool:        {t['name']}")
        click.echo(f"Description: {t['description']}")
        click.echo("-" * 50)

@agent_cli.command("health")
def health_cmd():
    """Verify LLM provider configuration, MCP server connectivity, and tool registration."""
    provider = get_llm_provider()
    client = DataOpsMCPClient()
    connected = client.connect()
    tools = client.list_tools() if connected else []

    click.echo("\n" + "=" * 60)
    click.echo("             DATAOPS AGENT HEALTH & STATUS CHECK            ")
    click.echo("=" * 60)
    click.echo(f"LLM Provider:        {provider.__class__.__name__}")
    click.echo(f"Configured Model:    {os.getenv('LLM_MODEL', 'gpt-4o (default)')}")
    click.echo(f"MCP Connectivity:    {'CONNECTED' if connected else 'FAILED'}")
    click.echo(f"Discovered Tools:    {len(tools)} tools registered")
    click.echo(f"Safety Boundaries:   ENABLED (Human Approval & Allowlisted Actions Enforced)")
    click.echo("=" * 60 + "\n")

@agent_cli.group("remediation")
def remediation_group():
    """Manage human approval, execution, and verification of remediation plans."""
    pass

@remediation_group.command("list")
def remediation_list_cmd():
    """List registered remediation plans."""
    plans = approval_service.list_plans()
    click.echo(f"\nTotal Registered Remediation Plans: {len(plans)}\n")
    for p in plans:
        click.echo(f"Plan ID:      {p.plan_id}")
        click.echo(f"Incident ID:  {p.incident_id}")
        click.echo(f"Status:       {p.status.value}")
        click.echo(f"Risk Level:   {p.risk_level.value}")
        click.echo(f"Actions:      {len(p.actions)} allowlisted actions\n" + "-" * 50)

@remediation_group.command("inspect")
@click.argument("plan_id")
def remediation_inspect_cmd(plan_id: str):
    """Inspect detailed remediation plan JSON."""
    plan = approval_service.get_plan(plan_id)
    if not plan:
        click.echo(f"Error: Remediation plan '{plan_id}' not found.", err=True)
        sys.exit(1)

    click.echo(json.dumps(plan.model_dump(), indent=2))

@remediation_group.command("approve")
@click.argument("plan_id")
@click.option("--approver", default="HUMAN_OPERATOR", help="Name or ID of human approver")
def remediation_approve_cmd(plan_id: str, approver: str):
    """Approve a proposed remediation plan (Human Approval Gate)."""
    try:
        plan = approval_service.approve_plan(plan_id, approver=approver)
        click.echo(f"Success: Remediation plan '{plan_id}' APPROVED by {approver}.")
        click.echo(f"Approval Expires At: {plan.expires_at}")
    except Exception as e:
        click.echo(f"Approval Failed: {e}", err=True)
        sys.exit(1)

@remediation_group.command("reject")
@click.argument("plan_id")
@click.option("--approver", default="HUMAN_OPERATOR", help="Name or ID of operator rejecting plan")
@click.option("--reason", default="Operator rejected plan", help="Reason for rejection")
def remediation_reject_cmd(plan_id: str, approver: str, reason: str):
    """Reject a proposed remediation plan."""
    try:
        plan = approval_service.reject_plan(plan_id, approver=approver, reason=reason)
        click.echo(f"Success: Remediation plan '{plan_id}' REJECTED.")
    except Exception as e:
        click.echo(f"Rejection Failed: {e}", err=True)
        sys.exit(1)

@remediation_group.command("execute")
@click.argument("plan_id")
def remediation_execute_cmd(plan_id: str):
    """Execute an approved remediation plan."""
    plan = approval_service.get_plan(plan_id)
    if not plan:
        click.echo(f"Error: Remediation plan '{plan_id}' not found.", err=True)
        sys.exit(1)

    try:
        res = executor.execute_plan(plan)
        click.echo(f"Success: Executed remediation plan '{plan_id}'.")
        click.echo(json.dumps(res, indent=2))
    except Exception as e:
        click.echo(f"Execution Failed: {e}", err=True)
        sys.exit(1)

@remediation_group.command("verify")
@click.argument("plan_id")
def remediation_verify_cmd(plan_id: str):
    """Verify recovery after remediation execution."""
    plan = approval_service.get_plan(plan_id)
    if not plan:
        click.echo(f"Error: Remediation plan '{plan_id}' not found.", err=True)
        sys.exit(1)

    try:
        res = verifier.verify_recovery(plan)
        click.echo(f"\nRecovery Verification Result for Plan '{plan_id}':")
        click.echo(f"Overall Status: {res.status}")
        click.echo(f"Summary:        {res.summary}\n")
        click.echo("Verification Checks:")
        for chk in res.checks:
            click.echo(f"  - [{chk.status}] {chk.check_name}: {chk.evidence}")
        click.echo()
    except Exception as e:
        click.echo(f"Verification Failed: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    agent_cli()
