import importlib

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugin(self, plugin_name):
        module = importlib.import_module(f"plugins.{plugin_name}")
        self.plugins[plugin_name] = module

    def run_plugin(self, plugin_name, *args, **kwargs):
        if plugin_name in self.plugins:
            self.plugins[plugin_name].run(*args, **kwargs)

import asyncio
import websockets

async def task_update_handler(websocket, path):
    async for message in websocket:
        console.print(f"[blue]Task update: {message}[/blue]")

start_server = websockets.serve(task_update_handler, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)