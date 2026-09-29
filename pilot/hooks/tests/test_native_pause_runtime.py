"""Exercise the installed Claude runtime and real hooks against a local API stub.

No credentials, paid requests, real-home writes, or Pilot installation are used.
The deterministic provider makes native continuation and tool-denial behavior
observable; normal unit tests cover the choices of a real model separately.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CLAUDE_BIN = os.environ.get("PILOT_NATIVE_CLAUDE_BIN") or shutil.which("claude")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not CLAUDE_BIN or os.environ.get("PILOT_NATIVE_RUNTIME_TESTS") != "1",
        reason="Native runtime acceptance is opt-in: PILOT_NATIVE_RUNTIME_TESTS=1",
    ),
]

RECORDER = """import json, subprocess, sys
from pathlib import Path
raw = sys.stdin.read()
root = Path(sys.argv[1])
target = root / "home/.pilot/hooks" / sys.argv[2]
result = subprocess.run([sys.executable, str(target.parent / "run_if_licensed.py"), str(target), *sys.argv[3:]], input=raw, text=True, capture_output=True)
with (root / "events.jsonl").open("a") as stream:
    stream.write(json.dumps({"hook": target.name, "input": json.loads(raw), "output": result.stdout, "stderr": result.stderr, "code": result.returncode}) + "\\n")
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
raise SystemExit(result.returncode)
"""


class _Provider(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, scenario: str, plan: Path, final_plan: str, session: str):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.scenario = scenario
        self.plan = plan
        self.final_plan = final_plan
        self.session = session
        self.requests: list[dict] = []
        self.background_read_at: int | None = None

    def reply(self, body: dict) -> tuple[list[dict], str]:
        self.requests.append(body)
        number = len(self.requests)
        if self.scenario.startswith("background"):
            marker = self.plan.parent / "job-finished"
            if number == 1:
                program = f"import time; from pathlib import Path; time.sleep(2); Path({str(marker)!r}).write_text('job-complete'); print('job-complete')"
                pytest_runner = self.plan.parent / "pytest"
                pytest_runner.write_text(f"#!{sys.executable}\n{program}\n")
                pytest_runner.chmod(0o755)
                command = shlex.join([str(pytest_runner), "tests/"])
                if self.scenario == "background_ci":
                    gh = self.plan.parent / "gh"
                    gh.write_text(f"#!{sys.executable}\n{program}\n")
                    gh.chmod(0o755)
                    command = shlex.join([str(gh), "run", "watch", "12345", "--exit-status"])
                return [
                    {
                        "type": "tool_use",
                        "id": "toolu_job",
                        "name": "Bash",
                        "input": {
                            "command": command,
                            "run_in_background": True,
                            "description": "Run the bounded fixture build",
                        },
                    }
                ], "tool_use"
            if number == 2:
                return [{"type": "text", "text": "Waiting for the background build's result."}], "end_turn"
            if not marker.exists():
                program = f"import time; from pathlib import Path; target=Path({str(marker)!r}); deadline=time.monotonic()+5\nwhile not target.exists() and time.monotonic()<deadline: time.sleep(0.01)\nassert target.exists(); print(target.read_text())"
                return [
                    {
                        "type": "tool_use",
                        "id": f"toolu_wait_{number}",
                        "name": "Bash",
                        "input": {
                            "command": shlex.join([sys.executable, "-c", program]),
                            "description": "Wait on the existing job's result without relaunching it",
                        },
                    }
                ], "tool_use"
            if self.background_read_at is None:
                self.background_read_at = number
        if self.scenario == "continuations" and number <= 11:
            return [{"type": "text", "text": f"Progress report {number}; work remains."}], "end_turn"
        if self.scenario in ("waiting", "material", "mixed", "answered") and number == 1:
            question = (
                "The API budget is $100. Keep waiting?"
                if self.scenario in ("material", "answered")
                else "Still building. Keep waiting?"
            )
            questions = [
                {
                    "header": "Still building",
                    "question": question,
                    "options": [
                        {"label": "Yes, keep waiting", "description": "Report when it finishes."},
                        {"label": "Stop checking for now", "description": "Pick it up later."},
                    ],
                    "multiSelect": False,
                }
            ]
            if self.scenario == "mixed":
                questions.append(
                    {**questions[0], "header": "Budget", "question": "The API budget is $100. Keep waiting?"}
                )
            return [
                {
                    "type": "tool_use",
                    "id": "toolu_wait",
                    "name": "AskUserQuestion",
                    "input": {
                        "questions": questions,
                    },
                }
            ], "tool_use"
        if self.scenario in ("material", "mixed"):
            return [{"type": "text", "text": "The required budget decision remains pending."}], "end_turn"
        if self.scenario == "answered" and number == 2:
            return [{"type": "text", "text": "The budget question was answered; work remains."}], "end_turn"
        read_at = (
            12
            if self.scenario == "continuations"
            else (
                self.background_read_at
                if self.scenario.startswith("background")
                else (3 if self.scenario == "answered" else 2)
            )
        )
        if number == read_at:
            return [
                {"type": "tool_use", "id": "toolu_read", "name": "Read", "input": {"file_path": str(self.plan)}}
            ], "tool_use"
        if number == read_at + 1:
            return [
                {
                    "type": "tool_use",
                    "id": "toolu_finish",
                    "name": "Write",
                    "input": {
                        "file_path": str(self.plan),
                        "content": self.final_plan,
                    },
                }
            ], "tool_use"
        if number == read_at + 2:
            program = (
                f"import sys; sys.path.insert(0, {str(ROOT)!r}); "
                f"from launcher.session import register_plan; register_plan({str(self.plan)!r}, 'VERIFIED')"
            )
            command = shlex.join([sys.executable, "-c", program])
            return [
                {
                    "type": "tool_use",
                    "id": "toolu_register",
                    "name": "Bash",
                    "input": {
                        "command": command,
                        "description": "Register the completed disposable fixture",
                    },
                }
            ], "tool_use"
        return [{"type": "text", "text": "Fixture completed."}], "end_turn"


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        if "/count_tokens" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"input_tokens":32}')
            return
        assert isinstance(self.server, _Provider)
        content, stop = self.server.reply(body)
        message = {
            "id": f"msg_local_{len(self.server.requests)}",
            "type": "message",
            "role": "assistant",
            "model": body["model"],
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 32, "output_tokens": 0},
        }
        events = [("message_start", {"type": "message_start", "message": message})]
        for index, block in enumerate(content):
            start = {**block, "text": ""} if block["type"] == "text" else {**block, "input": {}}
            delta = (
                {"type": "text_delta", "text": block["text"]}
                if block["type"] == "text"
                else {"type": "input_json_delta", "partial_json": json.dumps(block["input"])}
            )
            events.extend(
                [
                    ("content_block_start", {"type": "content_block_start", "index": index, "content_block": start}),
                    ("content_block_delta", {"type": "content_block_delta", "index": index, "delta": delta}),
                    ("content_block_stop", {"type": "content_block_stop", "index": index}),
                ]
            )
        events.extend(
            [
                (
                    "message_delta",
                    {
                        "type": "message_delta",
                        "delta": {"stop_reason": stop, "stop_sequence": None},
                        "usage": {"output_tokens": 16},
                    },
                ),
                ("message_stop", {"type": "message_stop"}),
            ]
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for event, data in events:
            self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
        self.wfile.flush()


def _run_native(tmp_path: Path, scenario: str) -> tuple[list[dict], list[dict], Path, Path]:
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    session = str(uuid.uuid4())
    pilot = home / ".pilot"
    pilot.mkdir(parents=True)
    (pilot / "hooks").symlink_to(ROOT / "pilot/hooks", target_is_directory=True)
    (pilot / ".license").write_text("isolated license-gate fixture")
    (pilot / "config.json").write_text(json.dumps({"specWorkflow": {"autoPause": True, "runawayGuard": False}}))
    plan = project / "plan.md"
    plan.write_text(
        "# Native fixture\nStatus: PENDING\nApproved: Yes\nType: Feature\n## Progress Tracking\n- [ ] Task 1: Complete fixture\n"
    )
    final = plan.read_text().replace("PENDING", "VERIFIED").replace("[ ]", "[x]")
    registration = pilot / "sessions" / session / "active_plan.json"
    registration.parent.mkdir(parents=True)
    data = {"plan_path": str(plan), "status": "PENDING"}
    if scenario in ("waiting", "material", "mixed", "answered"):
        message = (
            "The API budget is $100. Keep waiting?"
            if scenario in ("material", "mixed", "answered")
            else "Still building. Keep waiting?"
        )
        data["interaction"] = {"state": "paused", "kind": "decision", "message": message}
    registration.write_text(json.dumps(data))
    recorder = tmp_path / "record.py"
    recorder.write_text(RECORDER)
    matrix = json.loads((ROOT / "pilot/hooks/hook-lifecycle.json").read_text())
    relevant = {"spec_interaction.py", "spec_stop_guard.py", "spec_question_guard.py"}
    hooks = {}
    for entry in matrix["entries"]:
        if entry["platform"] != "claude" or entry["event"] == "SessionStart":
            continue
        targets = [target for target in relevant if any(target in command for command in entry["handlers"])]
        if targets:
            hooks.setdefault(entry["event"], []).append(
                {
                    "matcher": entry["matcher"] or "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": shlex.join(
                                [sys.executable, str(recorder), str(tmp_path), target]
                                + (["--answer"] if any("--answer" in command for command in entry["handlers"]) else [])
                            ),
                            "timeout": 10,
                        }
                        for target in targets
                    ],
                }
            )
    shipped_env = json.loads((ROOT / "pilot/settings.json").read_text())["env"]
    settings = tmp_path / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "hooks": hooks,
                "env": {key: value for key, value in shipped_env.items() if key == "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP"},
            }
        )
    )
    env = dict(os.environ)
    for key in (
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "CLAUDECODE",
        "CLAUDE_CODE_CHILD_SESSION",
        "CLAUDE_CODE_SESSION_ID",
        "PILOT_SESSION_ID",
        "CODEX_THREAD_ID",
        "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP",
        "CLAUDE_CODE_SIMPLE",
        "CLAUDE_CODE_SAFE_MODE",
    ):
        env.pop(key, None)
    env.update(
        HOME=str(home),
        CLAUDE_CONFIG_DIR=str(home / ".claude"),
        CLAUDE_PROJECT_ROOT=str(project),
        CLAUDE_PROJECT_PLATFORM="claude",
        PILOT_SESSION_ID=session,
        CLAUDE_CODE_TMPDIR=str(tmp_path / "runtime"),
        ANTHROPIC_API_KEY="sk-ant-local-test-only",
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
        DISABLE_AUTOUPDATER="1",
        DISABLE_TELEMETRY="1",
    )
    provider = _Provider(scenario, plan, final, session)
    env["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{provider.server_port}"
    threading.Thread(target=provider.serve_forever, daemon=True).start()
    try:
        args = [
            str(CLAUDE_BIN),
            "-p",
            "--model",
            "sonnet",
            "--effort",
            "low",
            "--setting-sources",
            "",
            "--strict-mcp-config",
            "--mcp-config",
            '{"mcpServers":{}}',
            "--settings",
            str(settings),
            "--session-id",
            session,
            "--output-format",
            "json",
            "--no-session-persistence",
            "--tools",
            "Read,Write,Bash,AskUserQuestion",
            "--allowedTools",
            "Read,Write,Bash",
            "--system-prompt",
            "Complete the deterministic local fixture using the tools. All files are disposable test artifacts.",
        ]
        if scenario == "continuations":
            result = subprocess.run([*args, "resume"], cwd=project, env=env, capture_output=True, text=True, timeout=45)
            assert result.returncode == 0, result.stderr
        else:
            args[args.index("json", args.index("--output-format"))] = "stream-json"
            _run_sdk(
                [*args, "--input-format", "stream-json", "--verbose", "--permission-prompt-tool", "stdio"],
                project,
                env,
                tmp_path,
                scenario,
            )
    finally:
        provider.shutdown()
        provider.server_close()
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert all(event["code"] == 0 and not event["stderr"] for event in events), events
    return provider.requests, events, plan, registration


def _run_sdk(args: list[str], project: Path, env: dict, root: Path, scenario: str) -> None:
    """Use the public SDK's stdio protocol so AskUserQuestion is actually enabled."""
    initialized = threading.Event()
    completed = threading.Event()
    received = []
    permissions = []
    with (root / "sdk-stderr.log").open("w") as stderr:
        process = subprocess.Popen(
            args, cwd=project, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, text=True
        )
        assert process.stdin and process.stdout

        def send(data: dict) -> None:
            process.stdin.write(json.dumps(data) + "\n")
            process.stdin.flush()

        def read() -> None:
            for line in process.stdout:
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                received.append(data)
                if (
                    data.get("type") == "control_response"
                    and data.get("response", {}).get("request_id") == "fixture-init"
                ):
                    initialized.set()
                elif data.get("type") == "control_request":
                    request = data["request"]
                    if request.get("subtype") == "can_use_tool":
                        permissions.append(request)
                        if request.get("tool_name") == "AskUserQuestion":
                            if scenario == "answered":
                                response = {
                                    "behavior": "allow",
                                    "updatedInput": {
                                        **request["input"],
                                        "answers": {"The API budget is $100. Keep waiting?": "Yes, approved"},
                                    },
                                }
                            else:
                                response = {"behavior": "deny", "message": "The required human decision is pending."}
                        else:
                            response = {"behavior": "allow", "updatedInput": request["input"]}
                        send(
                            {
                                "type": "control_response",
                                "response": {
                                    "subtype": "success",
                                    "request_id": data["request_id"],
                                    "response": response,
                                },
                            }
                        )
                elif data.get("type") == "result":
                    if not scenario.startswith("background") or "Status: VERIFIED" in (project / "plan.md").read_text():
                        completed.set()

        thread = threading.Thread(target=read, daemon=True)
        thread.start()
        try:
            send(
                {
                    "type": "control_request",
                    "request_id": "fixture-init",
                    "request": {"subtype": "initialize", "hooks": None},
                }
            )
            assert initialized.wait(10), (root / "sdk-stderr.log").read_text()
            send(
                {
                    "type": "user",
                    "session_id": "",
                    "message": {"role": "user", "content": "resume" if scenario.startswith("background") else "1"},
                }
            )
            assert completed.wait(30), (root / "sdk-stderr.log").read_text()
            process.stdin.close()
            assert process.wait(timeout=10) == 0, (root / "sdk-stderr.log").read_text()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            thread.join(timeout=5)
            (root / "sdk-messages.json").write_text(json.dumps(received))
        asked = [item for item in permissions if item.get("tool_name") == "AskUserQuestion"]
        assert bool(asked) == (scenario in ("material", "mixed", "answered")), permissions
        if scenario == "mixed":
            assert len(asked[0]["input"]["questions"]) == 1
            assert "budget" in asked[0]["input"]["questions"][0]["question"]


def test_native_claude_does_not_silently_stop_after_eight_continuations(tmp_path: Path) -> None:
    requests, events, plan, _registration = _run_native(tmp_path, "continuations")
    assert len(requests) >= 13
    assert "Status: VERIFIED" in plan.read_text()
    stops = [event for event in events if event["hook"] == "spec_stop_guard.py"]
    assert len(stops) >= 12
    assert not any("RUNAWAY" in event["output"] for event in stops)


def test_native_runtime_rejects_waiting_question_and_continues_without_user_input(tmp_path: Path) -> None:
    requests, events, plan, registration = _run_native(tmp_path, "waiting")
    guard = [event for event in events if event["hook"] == "spec_question_guard.py"]
    assert guard and '"permissionDecision": "deny"' in guard[0]["output"]
    assert "job handle" in json.dumps(requests[1]["messages"])
    assert "interaction" not in json.loads(registration.read_text())
    assert "Status: VERIFIED" in plan.read_text()


def test_native_runtime_preserves_a_real_budget_decision(tmp_path: Path) -> None:
    _requests, events, plan, registration = _run_native(tmp_path, "material")
    guard = [event for event in events if event["hook"] == "spec_question_guard.py"]
    assert guard and not guard[0]["output"]
    assert "Status: PENDING" in plan.read_text()
    assert json.loads(registration.read_text())["interaction"]["kind"] == "decision"


@pytest.mark.parametrize("scenario", ["background", "background_ci"])
def test_native_background_job_wakes_and_finishes_without_a_user_resume(tmp_path: Path, scenario: str) -> None:
    requests, events, plan, registration = _run_native(tmp_path, scenario)
    assert "Status: VERIFIED" in plan.read_text()
    assert "interaction" not in json.loads(registration.read_text())
    assert (plan.parent / "job-finished").read_text() == "job-complete"
    jobs = [
        item
        for item in requests
        if any(
            block.get("id") == "toolu_job"
            for message in item["messages"]
            if message.get("role") == "assistant"
            for block in message.get("content", [])
            if isinstance(block, dict)
        )
    ]
    assert jobs
    waits = [
        event for event in events if event["hook"] == "spec_stop_guard.py" and event["input"].get("background_tasks")
    ]
    assert waits, "The native runtime did not supply its documented live background-task contract"
    assert any(not event["output"] for event in waits)


def test_native_answer_inside_question_tool_continues_without_another_user_turn(tmp_path: Path) -> None:
    requests, events, plan, registration = _run_native(tmp_path, "answered")
    assert "Status: VERIFIED" in plan.read_text()
    assert "interaction" not in json.loads(registration.read_text())
    assert any("received a user answer" in event["output"] for event in events)
    assert len(requests) >= 4


def test_native_mixed_question_batch_keeps_only_the_required_user_decision(tmp_path: Path) -> None:
    _requests, events, plan, registration = _run_native(tmp_path, "mixed")
    guard = [event for event in events if event["hook"] == "spec_question_guard.py"]
    assert guard and '"updatedInput"' in guard[0]["output"]
    assert '"permissionDecision"' not in guard[0]["output"]
    assert "Status: PENDING" in plan.read_text()
    assert json.loads(registration.read_text())["interaction"]["kind"] == "decision"
