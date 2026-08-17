#!/usr/bin/env python3
"""llm-doc-extractor — turn messy documents into clean structured JSON.

Give it a document (text or PDF) and a field schema; it asks an LLM to return
JSON matching your schema exactly. Works with Anthropic, OpenAI, or a local
Ollama model — and ships a no-API-key `demo` provider so you can watch the
whole pipeline run before wiring up any keys.

Usage:
    python extract.py --doc samples/invoice.txt --schema schema.example.yaml --provider demo
    python extract.py --doc samples/invoice.txt --schema schema.example.yaml --provider anthropic
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

import providers


def load_document(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            sys.exit("PDF support needs pypdf: pip install pypdf")
        return "\n".join((page.extract_text() or "") for page in PdfReader(str(p)).pages)
    return p.read_text(encoding="utf-8", errors="replace")


def load_schema(path: str) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    fields = data.get("fields", [])
    if not fields:
        sys.exit("Schema has no `fields`.")
    return fields


def build_prompt(doc: str, fields: list[dict]) -> str:
    lines = [
        "You are a precise data-extraction engine.",
        "Extract the fields below from the document and return ONLY a valid JSON",
        "object with exactly these keys. Use null for anything not present.",
        "",
        "Fields:",
    ]
    for f in fields:
        lines.append(f"- {f['name']} ({f.get('type', 'string')}): {f.get('description', '')}")
    lines += ["", "Document:", '"""', doc.strip(), '"""', "", "Return only the JSON object."]
    return "\n".join(lines)


def parse_json(raw: str) -> dict:
    """Pull a JSON object out of a model response, tolerating code fences."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object in model response: {raw[:200]}")
    return json.loads(raw[start : end + 1])


def coerce(result: dict, fields: list[dict]) -> dict:
    """Keep exactly the schema keys, in order, with light type coercion."""
    out: dict = {}
    for f in fields:
        name = f["name"]
        val = result.get(name)
        if f.get("type") == "number" and isinstance(val, str):
            m = re.search(r"[-+]?\d[\d.,]*", val)
            val = float(m.group(0).replace(",", "")) if m else None
        out[name] = val
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract structured JSON from a document using an LLM.")
    ap.add_argument("--doc", required=True, help="document file (.txt or .pdf)")
    ap.add_argument("--schema", required=True, help="YAML schema with a `fields` list")
    ap.add_argument("--provider", default="demo", choices=["demo", "anthropic", "openai", "ollama"])
    ap.add_argument("--model", default=None, help="model id (provider default if omitted)")
    ap.add_argument("--out", default=None, help="write JSON here instead of stdout")
    args = ap.parse_args()

    doc = load_document(args.doc)
    fields = load_schema(args.schema)

    if args.provider == "demo":
        result = providers.demo_extract(doc, fields)
    else:
        raw = providers.call(args.provider, build_prompt(doc, fields), args.model)
        result = coerce(parse_json(raw), fields)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
