import asyncio
import json


class CodexConfigurationClient:
    def __init__(self, process: asyncio.subprocess.Process):
        self.process = process
        self.request_number = 0

    async def send(self, message: dict) -> None:
        self.process.stdin.write(json.dumps(message).encode() + b"\n")
        await self.process.stdin.drain()

    async def request(self, method: str, parameters: dict) -> dict:
        self.request_number += 1
        await self.send(
            {"id": self.request_number, "method": method, "params": parameters}
        )
        while line := await self.process.stdout.readline():
            response = json.loads(line)
            if response.get("id") != self.request_number:
                continue
            if "error" in response:
                raise RuntimeError(f"{method}: {response['error']['message']}")
            return response["result"]
        raise RuntimeError(f"Codex app-server closed while handling {method}")

    async def initialize(self) -> None:
        await self.request(
            "initialize",
            {
                "clientInfo": {"name": "codex_launcher_hook_trust", "version": "1"},
                "capabilities": {"experimentalApi": True},
            },
        )
        await self.send({"method": "initialized", "params": {}})
