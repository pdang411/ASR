class ChartDispatcher:

    def dispatch(self, task):
        return {
            'executor':'chart_mcp',
            'dataset':task.input_ref,
            'chart':'auto'
        }