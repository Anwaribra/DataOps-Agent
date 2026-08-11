import logging
from typing import Any, Dict, List, Optional
from mcp.server import app

logger = logging.getLogger("dataops.agent.client")

class DataOpsMCPClient:
    """
    MCP Client layer connecting the LLM DataOps Agent to the Phase 3 MCP Server.
    Provides tool discovery, argument validation, and invocation over MCP protocol.
    """
    def __init__(self):
        self.connected = False
        self._registered_tools: List[Dict[str, Any]] = []

    def connect(self) -> bool:
        """Connects to the MCP server and discovers registered tools."""
        try:
            tools = app._tool_manager.list_tools()
            self._registered_tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
                for t in tools
            ]
            self.connected = True
            logger.info(f"Connected to MCP Server. Discovered {len(self._registered_tools)} tools.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP Server: {e}")
            self.connected = False
            return False

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns the list of available MCP tools formatted for LLM tool calling."""
        if not self.connected:
            self.connect()
        return self._registered_tools

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calls a specific MCP tool by name and arguments."""
        if not self.connected:
            self.connect()

        arguments = arguments or {}
        tool_fn = None
        for t in app._tool_manager.list_tools():
            if t.name == name:
                tool_fn = t.fn
                break

        if not tool_fn:
            logger.error(f"MCP Tool '{name}' not found.")
            return {
                "error": f"Tool '{name}' not found on MCP Server.",
                "requested_name": name,
                "requested_arguments": arguments
            }

        try:
            logger.info(f"MCP Client calling tool '{name}' with args={arguments}")
            # Invoke the tool function registered on the MCP Server
            result = tool_fn(**arguments) if arguments else tool_fn()
            return result
        except Exception as e:
            logger.error(f"Error calling MCP tool '{name}': {e}")
            return {
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }

    def disconnect(self):
        """Disconnects the MCP Client."""
        self.connected = False
        logger.info("Disconnected from MCP Server.")
