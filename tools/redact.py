"""Masks secrets before anything is written to a journal or a saved transcript.

Journals and transcripts are pushed automatically, so a token that shows up in a question, an
answer or a tool output would otherwise land in Git. Every match is replaced by [redacted].
The patterns stop at quotes and backslashes, so a masked line in a .jsonl transcript stays valid JSON.
"""
import re

MASK = "[redacted]"
_V = r"[^\s\"'\\,;<>]"  # a value character: anything up to a quote, backslash, separator or space

PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}"),  # GitHub tokens
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}"),
    re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}"),  # Anthropic and OpenAI keys
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),  # Slack
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}"),  # Google API key
    re.compile(r"\b[A-Za-z0-9_~.-]{3}\dQ~[A-Za-z0-9_~.-]{31,34}"),  # Entra ID client secret
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT
    re.compile(r"(?i)\bBearer\s+" + _V + r"{20,}"),
    re.compile(r"(?i)\b((?:AccountKey|SharedAccessKey|Password|Pwd)=)" + _V + r"+"),  # connection strings
    re.compile(r"(?i)\b(password|passwd|secret|client_secret|api[_-]?key|access[_-]?token)"
               r"(\\?[\"']?\s*[:=]\s*\\?[\"']?)"
               r"(?=" + _V + r"*\d)(?=" + _V + r"*[A-Za-z])" + _V + r"{8,}"),  # a word alone is no secret
]


def _mask(match):
    groups = [g for g in match.groups() if g is not None]
    return "".join(groups) + MASK if groups else MASK


def redact(text):
    for pattern in PATTERNS:
        text = pattern.sub(_mask, text)
    return text
