#!/usr/bin/env python3
"""
Validates a content.json against content.schema.json AND checks the
cross-cutting SSS rules that JSON Schema alone cannot express:

  1. Simulation distribution: >=2 in Part 3, >=1 in Part 4, >=1 elsewhere,
     >=5 total (Section 3.3 of the master prompt).
  2. No two consecutive slides (within a Part, across the whole deck order)
     share the same 'type'.
  3. Reports total navigable slide count against the "40+" target in
     Section 4, since per-part min/max ranges do not structurally guarantee it.

Usage: python validate.py content.schema.json content.example.json
"""
import json
import sys

try:
    import jsonschema
except ImportError:
    print("Installing jsonschema...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "jsonschema"], check=True)
    import jsonschema


def main(schema_path, content_path):
    with open(schema_path) as f:
        schema = json.load(f)
    with open(content_path) as f:
        content = json.load(f)

    errors = []

    # 1. Structural validation
    validator = jsonschema.Draft202012Validator(schema)
    struct_errors = sorted(validator.iter_errors(content), key=lambda e: e.path)
    for e in struct_errors:
        loc = "/".join(str(p) for p in e.path)
        errors.append(f"[SCHEMA] {loc}: {e.message}")

    # 2. Simulation distribution check
    sim_counts = {}
    total_sims = 0
    for part in content.get("parts", []):
        pn = part.get("partNumber")
        count = sum(1 for s in part.get("slides", []) if s.get("type") == "simulation")
        sim_counts[pn] = count
        total_sims += count

    if sim_counts.get(3, 0) < 2:
        errors.append(f"[SIMULATION] Part 3 has {sim_counts.get(3, 0)} simulations, needs >=2.")
    if sim_counts.get(4, 0) < 1:
        errors.append(f"[SIMULATION] Part 4 has {sim_counts.get(4, 0)} simulations, needs >=1.")
    elsewhere = sum(sim_counts.get(p, 0) for p in [1, 2, 5, 6])
    if elsewhere < 1:
        errors.append(f"[SIMULATION] Parts 1/2/5/6 combined have {elsewhere} simulations, needs >=1.")
    if total_sims < 5:
        errors.append(f"[SIMULATION] Deck has {total_sims} total simulations, spec minimum is 5.")

    # 3. No two consecutive slides of the same type within a Part
    for part in content.get("parts", []):
        pn = part.get("partNumber")
        slides = part.get("slides", [])
        for i in range(1, len(slides)):
            if slides[i].get("type") == slides[i - 1].get("type"):
                errors.append(
                    f"[CONSECUTIVE-TYPE] Part {pn}: slides {i} and {i+1} "
                    f"('{slides[i]['slideId']}', '{slides[i-1]['slideId']}') are both type '{slides[i]['type']}'."
                )

    # 4. Slide count report (informational, not a hard failure)
    total_content_slides = sum(len(p.get("slides", [])) for p in content.get("parts", []))
    quiz_screens = 3 if content.get("quiz") else 0  # start, container, results
    total_screens = total_content_slides + quiz_screens

    print(f"Content slides (Parts 0-6): {total_content_slides}")
    print(f"Quiz screens (start/container/results): {quiz_screens}")
    print(f"Total navigable screens: {total_screens}")
    if total_screens < 40:
        print(
            f"NOTE: Section 4 targets '40+ slides', but per-part min/max ranges "
            f"only sum to a 27-33 content-slide range (this deck: {total_content_slides}) "
            f"plus ~3 quiz screens = {total_screens}. This is a gap in the source "
            f"master prompt's own arithmetic, not a bug in this deck. Either raise "
            f"per-part maximums or treat '40+' as aspirational."
        )

    print()
    if errors:
        print(f"FAILED - {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASSED - structurally valid, simulation distribution OK, no consecutive duplicate slide types.")
        sys.exit(0)


if __name__ == "__main__":
    schema_path = sys.argv[1] if len(sys.argv) > 1 else "content.schema.json"
    content_path = sys.argv[2] if len(sys.argv) > 2 else "content.example.json"
    main(schema_path, content_path)
