"""The hooks run in every session, so their behaviour is pinned here. Run with: python -m pytest -q tests"""
import datetime
import io
import json
import os
import subprocess
import sys

import pytest

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
sys.path.insert(0, TOOLS)
import note  # noqa: E402
from redact import MASK, redact  # noqa: E402

SECRETS = [
    "ghp_" + "a1B2" * 9,
    "github_pat_" + "x9" * 30,
    "sk-ant-api03-" + "Zz09" * 10,
    "sk-proj-" + "Ab12" * 8,
    "xoxb-1234567890-abcdefghij",
    "AKIAABCDEFGHIJKLMNOP",
    "AIza" + "B" * 35,
    "abc8Q~" + "d" * 34,
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
]


@pytest.mark.parametrize("secret", SECRETS)
def test_known_tokens_are_masked(secret):
    out = redact("token is " + secret + " ok")
    assert secret not in out and MASK in out and out.endswith(" ok")


def test_assignments_keep_the_name_and_mask_the_value():
    assert redact("password=hunter2hunter2") == "password=" + MASK
    assert redact('"api_key": "abcd1234efgh"') == '"api_key": "' + MASK + '"'
    assert redact("AccountName=x;AccountKey=abc/def+ghi==;EndpointSuffix=core") == \
        "AccountName=x;AccountKey=" + MASK + ";EndpointSuffix=core"
    assert redact("Authorization: Bearer abcdefghijklmnopqrstuvwxyz") == "Authorization: " + MASK


def test_private_keys_are_masked():
    key = "-----BEGIN RSA PRIVATE KEY-----\nMIIE\nabc\n-----END RSA PRIVATE KEY-----"
    assert redact("x " + key + " y") == "x " + MASK + " y"


def test_normal_text_is_left_alone():
    text = ("The password policy is strict. Commit 7c7f164 on main, see https://github.com/org/repo. "
            "Ticket secret: app-registration expired. KV app-password: login refused.")
    assert redact(text) == text


def test_masked_transcript_lines_stay_valid_json():
    line = json.dumps({"message": {"content": 'export TOKEN="ghp_' + "q" * 36 + '" and password: "s3cretvalue1"'}})
    assert "ghp_" not in redact(line) and "s3cretvalue1" not in redact(line)
    json.loads(redact(line))


def test_journal_lines_are_masked(tmp_path, monkeypatch):
    monkeypatch.setattr(note, "BASE", str(tmp_path))
    (tmp_path / "projects" / "demo").mkdir(parents=True)
    with __import__("contextlib").redirect_stdout(io.StringIO()):
        note.append("demo", "deployed with key sk-ant-api03-" + "k" * 40)
        note.append("demo", "second line")
    month = datetime.datetime.now().strftime("%Y-%m")
    text = (tmp_path / "projects" / "demo" / "journal" / (month + ".md")).read_text()
    assert "kkkk" not in text and MASK in text
    assert text.startswith("# Journal demo " + month) and text.count("\n## ") == 1 and "second line" in text


def run_hook(command):
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run([sys.executable, os.path.join(TOOLS, "block_ai_attribution.py")], input=payload,
                          capture_output=True, text=True)


def test_attribution_lines_are_blocked():
    assert run_hook('git commit -m "Fix\n\nCo-Authored-By: Claude <noreply@anthropic.com>"').returncode == 2
    assert run_hook('gh pr create --body "Generated with [Claude Code](https://claude.com)"').returncode == 2
    assert run_hook('git commit -m "Fix the login"').returncode == 0


def _delegation(tmp_path, payloads, model="claude-opus-4"):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({"type": "assistant", "message": {"model": model}}) + "\n")
    env = dict(os.environ, LOCALAPPDATA=str(tmp_path), CLAUDE_CODE_SUBAGENT_MODEL="")
    codes = []
    for p in payloads:
        p = dict({"session_id": "s1", "transcript_path": str(transcript)}, **p)
        codes.append(subprocess.run([sys.executable, os.path.join(TOOLS, "force_delegation.py")], input=json.dumps(p),
                                    capture_output=True, text=True, env=env).returncode)
    return codes


def test_delegation_blocks_after_twelve_direct_calls_and_resets_on_cheap_agent(tmp_path):
    read = {"tool_name": "Read", "tool_input": {"file_path": "x"}}
    assert _delegation(tmp_path, [read] * 13) == [0] * 12 + [2]
    agent = {"tool_name": "Agent", "tool_input": {"model": "haiku"}}
    assert _delegation(tmp_path, [agent, read]) == [0, 0]


def test_delegation_ignores_small_models_subagents_and_grep(tmp_path):
    read = {"tool_name": "Read", "tool_input": {}}
    assert set(_delegation(tmp_path, [read] * 15, model="claude-sonnet-4")) == {0}
    assert set(_delegation(tmp_path, [dict(read, agent_id="a")] * 15)) == {0}
    assert set(_delegation(tmp_path, [{"tool_name": "Grep", "tool_input": {}}] * 15)) == {0}


def test_runway_style_hex_keys_are_masked():
    assert "key_" + "ab12" * 16 not in redact("k key_" + "ab12" * 16)
