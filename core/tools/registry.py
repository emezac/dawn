class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, func: callable):
        """Register a tool with a given name and function."""
        self.tools[name] = func

    def execute_tool(self, tool_name: str, input_data: dict) -> dict:
        """Execute a registered tool with the provided input data."""
        if tool_name in self.tools:
            try:
                result = self.tools[tool_name](**input_data)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Tool '{tool_name}' not found."} 