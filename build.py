#!/usr/bin/env python3
"""
Injects a content.json file into engine.template.html to produce a single,
self-contained deck .html file — the "one engine, many decks" build step.

Optionally validates the content against content.schema.json first (if
jsonschema is installed and --skip-validate is not passed), so a malformed
content.json fails loudly here instead of silently breaking in the browser.

Usage:
  python build.py <content.json> <output.html> [--template engine.template.html] [--skip-validate]

Example:
  python build.py content.example.json deck-blockchain-supply-chain.html
"""
import json
import sys
import argparse
from pathlib import Path

PLACEHOLDER = "/*__SSS_CONTENT_JSON__*/ null"


def validate(content_path, schema_path):
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed — skipping structural validation. "
              "Run: pip install jsonschema --break-system-packages")
        return
    with open(schema_path) as f:
        schema = json.load(f)
    with open(content_path) as f:
        content = json.load(f)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(content), key=lambda e: e.path)
    if errors:
        print(f"BUILD ABORTED — {len(errors)} schema violation(s) in {content_path}:")
        for e in errors:
            loc = "/".join(str(p) for p in e.path)
            print(f"  - {loc}: {e.message}")
        sys.exit(1)


def build(content_path, output_path, template_path, skip_validate, schema_path):
    if not skip_validate and Path(schema_path).exists():
        validate(content_path, schema_path)

    with open(content_path) as f:
        content_json_text = f.read()
        json.loads(content_json_text)  # fail fast on malformed JSON

    with open(template_path) as f:
        template = f.read()

    if PLACEHOLDER not in template:
        print(f"ERROR: placeholder '{PLACEHOLDER}' not found in {template_path}. "
              "engine.template.html may have been edited incompatibly.")
        sys.exit(1)

    output = template.replace(PLACEHOLDER, content_json_text)

    with open(output_path, "w") as f:
        f.write(output)

    print(f"Built {output_path} from {template_path} + {content_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("content")
    parser.add_argument("output")
    parser.add_argument("--template", default="engine.template.html")
    parser.add_argument("--schema", default="content.schema.json")
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()
    build(args.content, args.output, args.template, args.skip_validate, args.schema)
