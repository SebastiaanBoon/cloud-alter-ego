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
