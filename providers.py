"""Model providers for llm-doc-extractor.

Each LLM provider takes a prompt and returns raw text (expected to be JSON).
The `demo` provider needs no API key — it runs a small rule-based extractor so
the pipeline works out of the box.
"""
from __future__ import annotations

import json
import re
import urllib.request


def call(provider: str, prompt: str, model: str | None) -> str:
    if provider == "anthropic":
        return _anthropic(prompt, model)
    if provider == "openai":
        return _openai(prompt, model)
    if provider == "ollama":
        return _ollama(prompt, model)
    raise ValueError(f"unknown provider: {provider}")


def _anthropic(prompt: str, model: str | None) -> str:
    import anthropic  # pip install anthropic ; needs ANTHROPIC_API_KEY

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model or "claude-sonnet-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _openai(prompt: str, model: str | None) -> str:
    from openai import OpenAI  # pip install openai ; needs OPENAI_API_KEY

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content or ""


def _ollama(prompt: str, model: str | None) -> str:
    body = json.dumps({"model": model or "llama3.1", "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"]


# --------------------------------------------------------------------------- #
# demo provider — rule-based, no API key                                       #
# --------------------------------------------------------------------------- #
_ITEM_RE = re.compile(r"^\s*[-*]\s*(.+?):?\s*\$?\s*([\d.,]+)\s*$")


def _to_number(text: str) -> float | None:
    m = re.search(r"[-+]?\d[\d.,]*", text or "")
    return float(m.group(0).replace(",", "")) if m else None


def demo_extract(doc: str, fields: list[dict]) -> dict:
    """A naive labelled-line extractor. Demonstrates the JSON shape without an LLM."""
    lines = doc.splitlines()
    out: dict = {}
    for f in fields:
        name = f["name"]
        ftype = f.get("type", "string")
        target = name.replace("_", "").lower()

        if ftype == "array":
            items = []
            for line in lines:
                m = _ITEM_RE.match(line)
                if m:
                    items.append({"description": m.group(1).strip(), "amount": _to_number(m.group(2))})
            out[name] = items or None
            continue

        val = None
        # 1) exact label before the colon
        for line in lines:
            if ":" in line:
                label, _, value = line.partition(":")
                if label.replace(" ", "").replace("_", "").lower() == target:
                    val = value.strip()
                    break
        # 2) fallback: any line mentioning the field name
        if val is None:
            needle = name.replace("_", " ").lower()
            for line in lines:
                if needle in line.lower() and ":" in line:
                    val = line.split(":", 1)[1].strip()
                    break

        out[name] = _to_number(val) if ftype == "number" else val
    return out
