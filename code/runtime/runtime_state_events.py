def on_mcp_connected(connection, state):
    state.update_mcp_connection(connection)


def on_mcp_disconnected(service_id, state):
    state.remove_mcp_connection(service_id)


def on_tool_discovered(tool, state):
    state.update_tool(tool)


def on_feature_changed(feature, state):
    state.update_feature(feature)


def on_agent_state_changed(agent, state):
    state.update_agent(agent)


def on_task_state_changed(task, state):
    state.update_task(task)


def on_reasoning_service_changed(service, state):
    state.update_reasoning_service(service)
