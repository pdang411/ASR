class ExecutorRegistry:
    MAP={
        "analyst":"deepagents",
        "coder":"agent-mcp",
        "controller":"runtime",
        "cad":"freecad",
        "blender":"blender",
        "git":"github"
    }

    def resolve(self, role):
        return self.MAP.get(role,"runtime")
    
    def best_executor(self, capabilities):
        """Determine the best executor based on task capabilities"""
        if not capabilities:
            return "runtime"
            
        # Check for specific capability matches
        for cap in capabilities:
            if cap == "cad":
                return "freecad"
            elif cap == "coding":
                return "agent-mcp"
            elif cap == "planning":
                return "deepagents"
        
        # Default to runtime
        return "runtime"