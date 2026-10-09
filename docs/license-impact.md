# License Impact Report — T-0002 analysis

Status: **T-0002 remains BLOCKED — the license decision is a human gate
(MASTER §35).** This document is a supporting analysis only; it chooses no
license and grants nothing. It exists so the owner can make an informed
decision through the normal governance process.

Prepared: 2026-10-09. Basis of evidence: the repository as committed, a live
import scan of `src/` and `tests/`, and `pip show` metadata for installed
Python packages. Third-party project licences that were not directly
inspected are marked UNVERIFIED (never asserted as fact).

## 1. Project license state (OBSERVED)

- There is **no `LICENSE`, `COPYING`, or equivalent file** in the repository
  root, and no SPDX headers in source files.
- There is **no declared dependency file** (`requirements.txt`,
  `pyproject.toml`, `setup.py`, `environment.yml`).
- Consequence: absent an explicit licence grant, default copyright applies —
  the work is **"all rights reserved"**. It currently cannot be reused,
  modified, or distributed by others, and cannot be offered under an open
  licence, until the owner records a decision (T-0002).

## 2. Runtime dependencies actually imported (OBSERVED)

A scan of `src/**/*.py` found exactly one non-stdlib import:

| Dependency | Version here | Licence | Imported by | Bundled? |
|---|---|---|---|---|
| Python Standard Library | 3.13.5 | PSF-2.0 | all modules | no (part of interpreter) |
| `sqlite3` | stdlib | SQLite (public domain) | `src/cie/store.py` | no |
| PyYAML (`yaml`) | 6.0.3 | MIT | `src/core/config.py` (lazy/optional) | no |

- PyYAML is **optional**: `config.load_config` imports it only when loading a
  YAML file; absent it, the code raises a clear `ConfigError` and JSON still
  works. It is not pinned and not declared.
- All other imports (`json`, `subprocess`, `sqlite3`, `hashlib`, `urllib`,
  `argparse`, etc.) are Python Standard Library.

## 3. Test / development dependencies (OBSERVED)

| Dependency | Version here | Licence | Role | Bundled? |
|---|---|---|---|---|
| pytest | 9.1.1 | MIT | test runner only | no |

pytest is not imported by shipped code.

## 4. External engineering tools (invoked, NOT bundled) (OBSERVED)

The platform integrates external programs by invoking their CLIs as separate
processes (`src/integrations/*`, `src/pem/*`). **No third-party tool code is
copied, linked, or redistributed** by this repository. Consequently those
tools' licences generally impose **no obligations on this project's source**;
they govern the user's own installation and use of those tools.

If this project ever bundles or redistributes one of these tools, the
obligations below become relevant and must be re-verified.

| Tool | Candidate upstream | Licence (UNVERIFIED unless noted) |
|---|---|---|
| Git | git-scm.com / github.com/git/git | GPL-2.0 |
| Python | python.org / github.com/python/cpython | PSF-2.0 |
| Jupyter | jupyter.org | BSD-3-Clause |
| FreeCAD | freecad.org / github.com/FreeCAD/FreeCAD | LGPL-2.1 |
| KiCad | kicad.org / gitlab.com/kicad/code/kicad | GPL-3.0 |
| ngspice | ngspice.sourceforge.io | BSD-3-Clause and/or GPL (component-dependent) |
| Gazebo | gazebosim.org / github.com/gazebosim/gz-sim | Apache-2.0 |
| Blender | blender.org / github.com/blender/blender | GPL-3.0 (GPL-2.0+ for some parts) |
| Scrapling | github.com/D4Vinci/Scrapling | UNVERIFIED (choose at T-0501) |
| REA (external engine) | github.com/morluto/rea (candidate) | UNVERIFIED |
| Taiga-S1 | upstream UNKNOWN (blocker B-1) | UNKNOWN |

Licence strings other than PyYAML/pytest/stdlib are reported, not verified
in this session; verify them before any redistribution or bundling decision.

## 5. Obligations by candidate project licence

Because no third-party code is bundled today, **there is no current
compatibility conflict**. The obligations below describe what each candidate
choice would impose on this project's own distribution:

- **No licence (current state):** all rights reserved; no reuse rights granted.
- **MIT / BSD:** permissive. Obligation: retain copyright notice and licence
  text in distributions. No source-disclosure requirement.
- **Apache-2.0:** permissive plus an explicit patent grant and a `NOTICE`
  file requirement for redistributions.
- **GPL-2.0 / GPL-3.0:** copyleft. Distributing binaries or derivative works
  requires providing corresponding source under the same licence. GPL-3.0 adds
  anti-tivoisation and patent terms.
- **AGPL-3.0:** GPL-3.0 plus a network-use trigger — offering the software as
  a network service counts as distribution for source-disclosure purposes.

## 6. Compatibility concerns

- None today: no third-party code is embedded.
- If external tools are ever bundled, GPL/AGPL tools (Blender, KiCad, possibly
  ngspice) would constrain the whole combined distribution, whereas
  LGPL (FreeCAD), Apache-2.0 (Gazebo) and BSD (Jupyter) are more permissive.
- PyYAML (MIT) and pytest (MIT) are compatible with any plausible project
  licence, including copyleft.

## 7. Open questions for the owner (T-0002 decision inputs)

1. Will the project be private, published open-source, or commercialised?
2. If published: which licence (permissive vs copyleft vs AGPL)?
3. Is bundling/redistributing any external engineering tool ever intended?
   (Currently: no — tools are user-installed.)
4. Is a contributor policy needed (CLA/DCO) if contributions are accepted?
5. Should PyYAML be pinned/declared, or kept strictly optional?

## 8. Limitations

- Third-party project licences in §4 are reported but not independently
  fetched/verified in this session; treat as UNVERIFIED.
- This report is not legal advice. A human owner must make and record the
  decision through governance (T-0002 stays BLOCKED until then).

## 9. Decision B — MIT license applied (2026-10-09)
- LICENSE file added with standard MIT text (Copyright (c) 2026 Shiv Shanmugam).
- Third-party assets (model weights, datasets, external tools) are NOT covered by this project's MIT license; their own licenses remain in force.
- The upstream biome-s1/taiga-s1 is MIT-licensed (source code) per the upstream repo; model weights may have separate terms — documented separately if needed.
- T-0002: project license decision is now resolved (MIT). Remaining third-party license verification tracked separately.
