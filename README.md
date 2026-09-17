# llm-doc-extractor

[![CI](https://github.com/dkautomation23/llm-doc-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/dkautomation23/llm-doc-extractor/actions/workflows/ci.yml)

Turn messy documents — invoices, contracts, emails, forms — into **clean,
schema-shaped JSON** you can drop straight into a database, spreadsheet, or CRM.

You describe the fields you want once, in YAML. The tool asks an LLM to fill
them in and returns exactly those keys, every time. Swap between **Anthropic,
OpenAI, or a local Ollama model** with one flag, and use the built-in **`demo`
provider to run the whole pipeline with no API key at all**.

## Why

Most "AI document" work is the same loop: read a PDF/email, find a handful of
fields, write them somewhere structured. This is that loop, made repeatable and
provider-agnostic — so you're not locked to one vendor and you can test offline.

## Quick start (no key needed)

```bash
pip install -r requirements.txt
python extract.py --doc samples/invoice.txt --schema schema.example.yaml --provider demo
```

Output:

```json
{
  "invoice_number": "INV-2026-00842",
  "date": "2026-08-14",
  "vendor": "ACME Robotics Ltd.",
  "total": 3012.0,
  "line_items": [
    { "description": "CNC calibration service", "amount": 1200.0 },
    { "description": "Replacement servo motors (x4)", "amount": 860.0 },
    { "description": "On-site installation", "amount": 450.0 }
  ]
}
```

## Real providers

```bash
export ANTHROPIC_API_KEY=...            # or OPENAI_API_KEY
python extract.py --doc contract.pdf --schema schema.yaml --provider anthropic
python extract.py --doc contract.pdf --schema schema.yaml --provider openai --model gpt-4o-mini
python extract.py --doc contract.pdf --schema schema.yaml --provider ollama --model llama3.1   # fully local
```

PDFs are read automatically when `pypdf` is installed (`pip install pypdf`).

## Define your fields

```yaml
fields:
  - name: invoice_number
    type: string
    description: The invoice identifier / number
  - name: total
    type: number
    description: Grand total amount
  - name: line_items
    type: array
    description: List of purchased items with description and amount
```

- `type` is `string`, `number`, or `array`.
- The output JSON always has **exactly your keys, in order**; missing fields
  come back as `null`, and `number` fields are coerced to real numbers.

## How it works

1. Load the document (`.txt` or `.pdf`).
2. Build a strict extraction prompt from your schema.
3. Call the chosen provider and pull the JSON object out of the response
   (tolerant of code fences and surrounding prose).
4. Keep only your schema keys, coerce types, print or `--out` to a file.

The `demo` provider swaps step 2–3 for a small rule-based extractor, so the
repo runs end-to-end before you connect a model.

## License

MIT — see [LICENSE](LICENSE).
