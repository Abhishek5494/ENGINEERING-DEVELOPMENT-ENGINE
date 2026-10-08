# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0401 — Component data model + schema + storage
- **State:** READY
- **Phase:** 4 — Component Intelligence Engine (CIE)

### Objective
Establish the CIE foundation: a machine-readable component record
(§12) with the optional motor extension (§13), a JSON Schema for that
record, and a local store (SQLite; JSON import/export) that round-trips
records losslessly. This is the data contract every later CIE/REA/
engineering task depends on.

### Dependencies
- T-0302 (COMPLETE — evidence `Claim`), T-0202 (COMPLETE — shared paths).

### Affected components
- `src/cie/__init__.py`, `src/cie/model.py`, `src/cie/store.py` (new)
- `config/component.schema.json` (new; draft-07, mirrors the model)
- `tests/test_cie_model.py`, `tests/test_cie_store.py` (new)
- `requirements.md` (CIE data-model row R5.x), roadmap/audit/project-state/
  next-task/chatmem closure updates

### Data model (MASTER §12, §13)
§12 component fields: id, category, name, manufacturer, model,
part_number, sku, source_urls, retrieval_date, specifications,
dimensions, materials, interfaces, electrical, mechanical, thermal,
environmental, datasheets.
§13 motor fields (when category is a motor): rated voltage, rated
current, rated speed, rated torque, stall torque, stall current, winding
resistance, torque constant/Kv, rotor inertia, efficiency, thermal
limits, dimensions, and method notes for derived values.
Every field is OPTIONAL. A field with no real value is **UNKNOWN** —
never empty-string/zero/“N/A” padding.

### Constraints
- Standard library only (`sqlite3`, `json`, `dataclasses`). No ORM.
- **No padding fields (§12):** serialization OMITS fields whose value is
  UNKNOWN; the schema must NOT require any content field, so an
  incomplete record is valid and honest. Only `id` is required (the
  storage key).
- **UNKNOWN is explicit:** `UNKNOWN` is a distinct sentinel, not `None`
  masquerading as a value and not the string "UNKNOWN". Round-trips must
  preserve the difference between "field absent" and "field UNKNOWN"
  where that distinction matters; the simplest honest rule is: absent
  field == UNKNOWN, and both serialize to omission (documented).
- Derived/calculated values (§13) must carry a method note — a
  `DerivedValue(value, method, evidence_label)` type is required; a
  derived value without a method is rejected. Evidence labels come from
  `src/core.evidence` (T-0302).
- Storage: SQLite file under a caller-supplied path (default under the
  `components/` directory resolved via `src.core.config`). `save` is
  idempotent by `id` (upsert); `get`/`all`/`delete` round-trip exactly.
  No network, no scraping.
- No fabricated data: constructing a motor record does not invent
  ratings; unset ratings stay UNKNOWN.

### Acceptance criteria
1. `src/cie/model.py` exposes `UNKNOWN`, `UNKNOWN_TOKENS`?, `DerivedValue`,
   `Component`, `MotorSpec`, `to_dict`/`from_dict` (or equivalent),
   `ComponentError`.
2. `Component` accepts all §12 fields; unset fields are UNKNOWN; `to_dict`
   omits UNKNOWN fields (no padding); `from_dict(to_dict(x)) == x`
   (round-trip) including source_urls order and nested `specifications`.
3. `DerivedValue` requires a non-empty `method` and a valid evidence
   label; a missing method raises `ComponentError`.
4. A `MotorSpec` covers the §13 fields; unset fields are UNKNOWN; a
   motor record embeds it only when present.
5. `config/component.schema.json` is a valid draft-07 schema requiring
   only `id` (plus `$schema`/title), asserts types, and a stdlib checker
   in tests validates good records and rejects a record with a wrong
   field type. (A fabricated status/label field is rejected by
   `additionalProperties: false`.)
6. `src/cie/store.py` exposes `ComponentStore` with `save`, `get`,
   `all`, `delete` over SQLite (upsert by id) plus `export_json` /
   `load_json`; stored-then-fetched records equal the originals; saving
   the same id twice yields one row with the latest value.
7. `from src.cie.model import ...` and `from src.cie.store import ...`
   work; `src/cie/__init__.py` re-exports the public names.
8. Full suite passes (`python -m pytest tests/ -v`).
9. Roadmap (T-0401 COMPLETE; T-0402/T-0403 unblock; next per §48 order),
   requirements, project-state, audit (AUDIT-0017), chatmem, memory
   updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: build a component with some known and some UNKNOWN
  fields, save to a temp SQLite DB, fetch it back, and print the
  round-tripped dict — OBSERVED, not claimed. Validate the JSON through
  the schema check.
- Review `git status` / `git diff` before commit.
- After completion, select the next READY task (T-0402 URL ingestion and
  T-0403 provenance both depend on T-0401) by §48 order and record the
  reason.

### Out of scope (do not pull in)
- Scraping/ingestion/network (T-0402+), provenance & conflict handling
  (T-0403), source priority (§10), and any UI/CLI. No engine integration.