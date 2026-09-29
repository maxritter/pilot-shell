"""Compare real MCP initialize/tools-list contracts using temporary profiles."""

import argparse
import json
import os
import select
import subprocess
import tempfile
import time
from pathlib import Path


def tool_surface(artifact: Path, bun: str) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="pilot-mcp-contract-") as home:
        settings = Path(home) / ".pilot/memory/settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text(json.dumps({"CLAUDE_PILOT_WORKER_PORT": "65530"}))
        env = {"PATH": os.environ.get("PATH", ""), "HOME": home, "TMPDIR": home}
        process = subprocess.Popen(
            [bun, str(artifact.resolve())],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
        )
        try:

            def request(identifier, method, params):
                process.stdin.write(
                    json.dumps({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params}) + "\n"
                )
                process.stdin.flush()
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if not select.select([process.stdout], [], [], max(0, deadline - time.monotonic()))[0]:
                        break
                    line = process.stdout.readline()
                    if not line:
                        break
                    response = json.loads(line)
                    if response.get("id") == identifier:
                        if "error" in response:
                            raise RuntimeError(response["error"])
                        return response["result"]
                raise RuntimeError(f"MCP {method} did not complete")

            initialized = request(
                1,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "pilot-artifact-contract", "version": "1"},
                },
            )
            assert initialized.get("capabilities", {}).get("tools") is not None
            process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
            process.stdin.flush()
            return sorted(request(2, "tools/list", {})["tools"], key=lambda item: item["name"])
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--bun", default="bun")
    args = parser.parse_args()
    before = tool_surface(args.before, args.bun)
    after = tool_surface(args.after, args.bun)
    if before != after:
        raise SystemExit("MCP tool definitions changed: inspect schemas before shipping")
    print(f"MCP initialize and all {len(after)} tools/list contracts match the baseline")


if __name__ == "__main__":
    main()
