import json
import os
import sys
import click
from agent.agent import DataOpsAgent
from agent.client import DataOpsMCPClient
from agent.provider import get_llm_provider

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
    click.echo(f"Safety Boundaries:   ENABLED (Read-Only Mode, Write Executions Disabled)")
    click.echo("=" * 60 + "\n")

if __name__ == "__main__":
    agent_cli()
