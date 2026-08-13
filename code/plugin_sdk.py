from __future__ import annotations

import importlib.util
from pathlib import Path


class Plugin:
    name = ""

    async def initialize(self):
        return {"name": self.name or self.__class__.__name__, "initialized": True}


class PluginManager:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin):
        name = plugin.name or plugin.__class__.__name__
        self._plugins[name] = plugin
        return name

    async def discover(self, plugins_dir: str = "./plugins"):
        discovered = []
        path = Path(plugins_dir)
        if not path.exists() or not path.is_dir():
            return discovered

        for candidate in sorted(path.glob("*.py")):
            module = _load_module(candidate)
            if module is None:
                continue
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr is not Plugin:
                    instance = attr()
                    name = self.register(instance)
                    discovered.append(name)

        return discovered

    async def initialize_all(self):
        results = {}
        for name, plugin in self._plugins.items():
            results[name] = await plugin.initialize()
        return results

    def list_plugins(self):
        return sorted(self._plugins.keys())


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module