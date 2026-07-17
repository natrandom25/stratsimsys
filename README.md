# SSS Studio

A no-backend, client-side generator for interactive classroom slide decks built on the SSS (Strategic Systems Simulation) instructional framework. Fill in a form, get a ready-to-paste prompt for any LLM, paste back its JSON response, and download a single self-contained HTML deck with navigation, animated simulations, an assessment quiz, and dark mode — no API key, no server, hostable on GitHub Pages.

Two domains are supported today: **MBA / EMBA / Executive Education** and **Software & Systems Engineering** (distributed systems, databases, networking, security, ML infrastructure — not embedded, electrical, or mechanical engineering). Each domain has its own voice rules, bridging framework, Part structure, and slide-type menu; they share the same rendering engine.

## How it works

```
Studio (index.html)
  → pick a domain, fill in deck metadata
  → "Generate Prompt" fetches the matching schema and builds a copy-paste prompt
  → paste that into Claude, ChatGPT, or any LLM
  → paste the LLM's JSON response back into Studio
  → "Validate" checks it against the deck's structural rules
  → "Build Deck" merges it with engine.template.html
  → download one self-contained .html file — the finished deck
```

`build.py` does the same merge from the command line if you'd rather script it: `python build.py content.json output.html`.

## Files

All files sit at repo root — Studio's fetch calls assume `index.html`, `engine.template.html`, `content.schema.json`, and `content-engineering.schema.json` are siblings, so this is deliberate, not a cleanup TODO.

- `index.html` — Studio, the generator form. Also the GitHub Pages landing page.
- `engine.template.html` — the shared rendering engine: navigation, transitions, icon system, dark mode, quiz engine, and every slide-type renderer for both domains.
- `content.schema.json` — content contract for the MBA/EMBA domain.
- `content-engineering.schema.json` — content contract for the Software & Systems Engineering domain.
- `build.py` — command-line build script (merges a content JSON file into the engine template).
- `validate.py` — structural validator using `jsonschema`, for exhaustive checks beyond what Studio's in-browser validator covers.
- `content.example.json` — a worked MBA example ("Blockchain in Supply Chain Management").
- `deck-blockchain-supply-chain.html` — that example, already built into a standalone deck.
- `SSS-Engineering-Spec-DRAFT.md` — the pedagogical spec for the Engineering domain (voice rules, bridging taxonomy, Part structure, slide types) that `content-engineering.schema.json` implements.

## Hosting

Deploy from the repo root via GitHub Pages (Settings → Pages → Deploy from branch → main → /root). Studio's fetch calls require serving over http/https — opening `index.html` directly as a local file will break the schema and engine fetch steps. For local testing, run `python -m http.server` in the repo folder first.

## What's built vs. not

**Working:** both domains end to end (prompt generation, validation, build, download); quiz engine with scoring, Part-breakdown results, retake, and localStorage persistence; 3 of 5 simulation templates (`network-growth`, `before-after-toggle`, `flow-reveal`); dark mode; print stylesheet; 5 named theme palettes.

**Not yet built:** 2 of 5 simulation templates (`decision-tree`, `data-story-reveal` render a labeled placeholder rather than an animation); bookmarking; certificate rendering (the schema supports certificate configuration, but the engine doesn't yet render a certificate screen); full keyboard roving-focus on quiz options (Tab/Enter work, arrow-key navigation between options doesn't).

**Testing status:** built and hand-traced logic-by-logic, but not yet run end-to-end in a live browser. Test both domains in Studio before relying on either for a real class.

## Credits

Created by Dr. Natraj N. A. — SIDTM, Symbiosis International University.

## License

MIT.
