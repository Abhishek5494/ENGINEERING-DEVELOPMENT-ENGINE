# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0402 — CIE URL ingestion + exact-identification flow
- **State:** READY
- **Phase:** 4 — Component Intelligence Engine (CIE)

### Objective
Implement the CIE entry point (MASTER §8, §9): given an exact product URL
and the page's HTML, extract the product's identity — title, manufacturer,
model, SKU, part number, seller, product URL and listed specifications —
and map it onto a `Component` record. The system MUST identify the exact
product first and MUST NOT fall back to a generic search ("775 motor")
when identity cannot be established; in that case it refuses and reports
why. Acquisition itself is delegated through an injected acquirer so this
task performs NO network access (Scrapling wiring is T-0502).

### Dependencies
- T-0401 (COMPLETE — `Component`/`UNKNOWN`/`MotorSpec`, `src/cie`), T-0302
  (COMPLETE — evidence labels), T-0202 (COMPLETE — shared paths).

### Affected components
- `src/cie/target.py` (new): `Target`, `TargetError`, `parse_target`
  (URL validation + host extraction; no network).
- `src/cie/identify.py` (new): `Identification`, `Acquirer` protocol,
  `identify_page(url, html)`, `ingest(url, acquire)`.
- `src/cie/__init__.py` (re-export the new public names).
- `config/identification.schema.json` (new; draft-07 for `Identification`).
- `tests/test_cie_target.py`, `tests/test_cie_identify.py` (new) with
  fixture HTML strings (no network).
- `requirements.md` (R5.x), roadmap/audit/project-state/next-task/chatmem
  closure updates.

### Identity sources (in priority order within one page)
1. JSON-LD (`<script type="application/ld+json">`, schema.org `Product`):
   `name`, `brand`, `manufacturer`, `sku`, `mpn`, `offers.seller`,
   `additionalProperty` (name/value specs).
2. OpenGraph / product `<meta>` tags: `og:title`, `og:site_name`,
   `og:url`, `product:brand`, `product:price:amount`,
   `product:price:currency`, `product:retailer`.
3. `<title>` element and the canonical link (`<link rel="canonical">`).
Anything not found stays `UNKNOWN` (never fabricated). Later (T-0403) each
extracted fact gains provenance; for now provenance is the page URL.

### Constraints
- Standard library only (`html.parser`, `json`, `urllib.parse`, `re`).
  No `requests`, no network, no Scrapling — the acquirer is injected.
- Untrusted input (§14 spirit): the parser only *extracts*; it never
  evaluates scripts, never follows URLs, never imports/executes page
  content. Non-`ld+json` `<script>` contents are ignored. A malformed
  JSON-LD block is skipped, not fatal.
- Exact-identification rule (§8/§9): if a page yields no usable identity
  signal (no title AND no model/sku/part number/manufacturer), raise
  `IdentificationError` — do NOT degrade to a generic search.
- Identity fields map into §12 `Component`; only real values are set,
  everything else is omitted/UNKNOWN.
- No fabricated data: extraction never invents a manufacturer/model.

### Acceptance criteria
1. `parse_target(url)` validates scheme+host (`http`/`https`), rejects
   empty/invalid/relative URLs with `TargetError`, and exposes `url`,
   `host` (lowercased, no `www.` prefix) and `scheme`.
2. `identify_page(url, html)` returns an `Identification` whose
   `title`/`manufacturer`/`model`/`sku`/`part_number`/`seller`/
   `product_url` are `UNKNOWN` when absent, populated when present.
3. JSON-LD `Product` is parsed: `name`, `brand`/`manufacturer`, `sku`,
   `mpn`, `offers` seller all extracted; `additionalProperty` becomes the
   specifications mapping; malformed JSON-LD is ignored (other signals
   still used).
4. OpenGraph/`<title>`/canonical fallbacks fill fields JSON-LD lacks;
   JSON-LD wins when both are present.
5. `to_component()` yields a `Component` (id derived from
   host+model/sku, or supplied) with `name`, `manufacturer`, `model`,
   `part_number`, `sku`, `source_urls=(url,)` and `specifications`, with
   no UNKNOWN padding.
6. `identify_page` raises `IdentificationError` on an empty/opaque page
   (e.g. `<html></html>`) — proving the no-generic-search rule.
7. `ingest(url, acquire)` calls the injected `acquire(url)`, then
   `identify_page`; a raising acquirer propagates (no silent fallback).
8. `config/identification.schema.json` is a valid draft-07 schema for the
   serialized `Identification`; a stdlib checker validates a good record
   and rejects a wrong-typed field.
9. `from src.cie import ...` exposes the new names; full suite passes
   (`python -m pytest tests/ -v`).
10. Roadmap (T-0402 COMPLETE; T-0403 and T-0502 unblock as applicable),
    requirements, project-state, audit (AUDIT-0018), chatmem, memory
    updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: run `identify_page` over a fixture HTML string with a
  JSON-LD product block and over an opaque page; print the extracted
  `Identification` dict and the `Component` dict, and show the opaque page
  raising `IdentificationError` — OBSERVED, not claimed.
- Review `git status` / `git diff` before commit.
- After completion, pick the next READY task by §48 order (T-0403 is
  READY; T-0502 depends on T-0501) and record the reason.

### Out of scope (do not pull in)
- Real network fetching / Scrapling (T-0502), provenance objects + source
  priority + conflict detection (T-0403), authoritative re-search (§10),
  engineering conclusions. No CLI/UI.