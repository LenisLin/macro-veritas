# State Machine

## Intent

MacroVeritas uses object-level lifecycle states rather than a "4院 workflow" representation. The goal is to track the readiness and review position of concrete project objects without implying a larger institutional or automated workflow engine.

- This document is design intent for the MVP documentation layer.
- No lifecycle engine, state validator, or transition code is implemented yet.

## Transition Principles

- States belong to objects, not to teams or organizational lanes.
- A transition should happen only when the minimum provenance and linkage for the next step are present.
- Transitions should be conservative and easy to audit.
- When an object needs correction, it should be returned to an earlier workable state rather than silently edited past the problem.
- Supersession or closure should preserve traceability rather than delete history.

## `StudyCard` Lifecycle

| Status | Meaning |
| --- | --- |
| `draft` | A study candidate has been identified, but the canonical registry record is not yet stable. |
| `registered` | The study has enough identity and provenance to serve as a stable anchor for downstream objects. |
| `active` | The study is being used by one or more `DatasetCard` or `ClaimCard` records. |
| `closed` | The study record is intentionally frozen, retired from active use, or superseded by a better canonical record. |

Typical transition direction:

`draft -> registered -> active -> closed`

## `DatasetCard` Lifecycle

| Status | Meaning |
| --- | --- |
| `identified` | The dataset is known, but its project record or binding is still incomplete. |
| `registered` | The dataset has enough identity and provenance to be tracked in the registry. |
| `bound` | The dataset is linked to a concrete filesystem location or prepared project artifact path. |
| `retired` | The dataset record remains for traceability, but it is no longer the preferred active binding. |

Typical transition direction:

`identified -> registered -> bound -> retired`

## `ClaimCard` Lifecycle

| Status | Meaning |
| --- | --- |
| `captured` | The claim has been recorded, but its scope is still rough or incomplete. |
| `scoped` | The claim boundary is clear enough to link to a study and intended evidence target. |
| `ready` | The claim has enough linkage and context to enter later reanalysis or evidence collection work. |
| `closed` | The claim record has been reviewed, deferred, or superseded with a retained reason. |

Typical transition direction:

`captured -> scoped -> ready -> closed`

## Notes On Returns And Audit

- An audit return does not create a separate workflow model. It simply means the object should move back to the last status whose requirements it actually satisfies.
- Not every object family needs a full public state list in the MVP. The three families above are the minimum needed to make the registry model operational at a documentation level.
- Additional object-family states can be added later only when their contracts and transition reasons are concrete enough to document without guesswork.
