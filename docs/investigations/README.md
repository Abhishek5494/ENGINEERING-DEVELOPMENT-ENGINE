# REA investigations

Authorized reverse-engineering investigations live here, one directory per
investigation (MASTER §21):

```
docs/investigations/<investigation-name>/
├── scope.md
├── evidence.md
├── findings.md
├── behavior.md
├── unknowns.md
├── limitations.md
└── implementation-notes.md
```

Investigations are created from an authorized record via
`src.rea.write_investigation(root, investigation)`; each file is generated
from the record so the two cannot silently disagree. An investigation
cannot be constructed without a documented authorization basis (§20), and
findings enforce the §19 evidence rules (recovered pseudocode is never
claimed as the original source; a reconstruction is never labelled
`OBSERVED`).

Only investigate targets for which you have appropriate authorization or
where the investigation is otherwise legally permitted.