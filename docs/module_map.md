# Module Map

## Purpose

This document bridges the governance freeze to the current package skeleton.

- [`docs/governance_spec.md`](governance_spec.md) is the function-level source of truth.
- [`docs/card_contracts.md`](card_contracts.md) is the field-level source of truth for the first frozen card slice.
- [`docs/registry_layout.md`](registry_layout.md) is the filesystem source of truth for first-slice registry placement and naming.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md) is the source of truth for future registry access and mutation boundaries.
- [`docs/gateway_contracts.md`](gateway_contracts.md) is the source of truth for gateway result, error, and mutation-plan communication contracts.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md) is the source of truth for reserved internal command-family contracts.
- This file maps those frozen responsibilities onto the existing package and module layout.
- It does not claim that the mapped functions, CLI groups, or workflows are implemented.

## Stable Base To Preserve

The current freeze still preserves the existing lightweight runtime base:

| Current Path | Current Role | Preserve Rule |
| --- | --- | --- |
| `src/macro_veritas/config.py` | Resolved project configuration and layout-path helper | Keep as the current runtime configuration base. |
| `src/macro_veritas/cli.py` | Current lightweight `argparse` CLI scaffold | Keep current implemented commands and entry flow intact. |
| `src/macro_veritas/__main__.py` | Module execution entrypoint | Preserve `python -m macro_veritas` support. |
| repo-root `macro_veritas/` bootstrap package | Checkout-time bootstrap namespace | Preserve unless the invocation model intentionally changes later. |
| current `status` / `show-config` / `init-layout` CLI scaffold | Honest implemented interface | Treat as stable implemented fact while governance descriptors grow around it. |

## Governance-To-Code Mapping

This mapping is the conservative module-level freeze for the current round.

| Governance Label | Code Path | Current Representation | Function-Level Source | Current Module Responsibility | Explicitly Deferred |
| --- | --- | --- | --- | --- | --- |
| 核心决策层 / A-header | `macro_veritas.governance.a_header` | single module with static lane and function descriptors | `docs/governance_spec.md` A-header section | Freeze mandate, contract, and oversight descriptor functions for future non-trivial work units. | Orchestration engine, dispatch, workflow execution, enforcement. |
| 吏部 / Personnel Department | `macro_veritas.governance.departments.personnel` | single department module with office-level descriptors | `docs/governance_spec.md` personnel section | Freeze role vocabulary, assignment headers, and escalation coverage descriptors. | Authentication, permissions, staffing workflow, identity management. |
| 户部 / Registry Department | `macro_veritas.governance.departments.registry` | single department module with office-level descriptors | `docs/governance_spec.md` registry section | Freeze intake, locator-binding, and extraction-planning descriptors for registry-facing objects. | Registry IO, identifier allocation, validation, persistence workflow. |
| 礼部 / Standards Department | `macro_veritas.governance.departments.standards` | single department module with office-level descriptors | `docs/governance_spec.md` standards section | Freeze naming, contract-boundary, and exception-handling descriptors. | Automatic linting, rule enforcement, policy service. |
| 兵部 / Operations Department | `macro_veritas.governance.departments.operations` | single department module with office-level descriptors | `docs/governance_spec.md` operations section | Freeze method, reanalysis-planning, and artifact-manifest descriptors. | Scientific execution, orchestration runtime, notebook loop, CellVoyager integration. |
| 工部 / Infrastructure Department | `macro_veritas.governance.departments.infrastructure` | single department module with office-level descriptors | `docs/governance_spec.md` infrastructure section | Freeze layout, config-boundary, and runtime-surface descriptors. | Deployment system, environment manager, storage backend, runtime automation. |
| 刑部 / Review Department | `macro_veritas.governance.departments.review` | single department module with office-level descriptors | `docs/governance_spec.md` review section | Freeze routine audit intake, audit-record, and escalation-gate descriptors. | Audit engine, evidence grading engine, automated adjudication. |
| 检察院 / Prosecution | `macro_veritas.prosecution.specs` | single specs module with lane-level descriptors | `docs/governance_spec.md` prosecution section | Freeze escalated case intake, case-brief, and disposition descriptors. | Automated escalation, sanctions, case-management engine, enforcement. |

## Functional Office Policy

For this freeze, "功能司" stays inside existing modules rather than becoming many empty package trees.

- Department modules hold the office-level descriptors and planned function names.
- `macro_veritas.prosecution.specs` holds the prosecution lanes and planned function names.
- No office or lane gets its own subpackage yet.
- Promotion to a separate module or package should happen only after the office contract grows beyond static descriptors.

## First Card Contract Modules

The first precise card-contract slice lives in `macro_veritas.registry`, not in governance office packages.

| Code Path | Current Role | Explicit Boundary |
| --- | --- | --- |
| `src/macro_veritas/registry/study.py` | Static `StudyCard` contract metadata for fields, statuses, and relationship anchors | No IO, no file mutation, no screening engine, no validation runtime |
| `src/macro_veritas/registry/dataset.py` | Static `DatasetCard` contract metadata for fields, statuses, and direct study linkage | No binding engine, no locator resolution, no filesystem mutation |
| `src/macro_veritas/registry/claim.py` | Static `ClaimCard` contract metadata for fields, statuses, and direct study/dataset pointers | No extraction engine, no evidence grading, no review runtime |

## Registry Layout And Access Boundary Modules

The filesystem layout freeze is documentation-led first and mirrored only by
static helper modules.

| Code Path | Current Role | Explicit Boundary |
| --- | --- | --- |
| `src/macro_veritas/config.py` | Resolve configured roots and expose conservative root-level helpers for the registry tree | No directory creation beyond existing CLI scaffold, no registry-card IO |
| `src/macro_veritas/shared/types.py` | Provide lightweight descriptor aliases and gateway contract TypedDicts shared across documentation-oriented modules | No validation engine, no runtime model classes, no serializer behavior |
| `src/macro_veritas/shared/naming.py` | Provide canonical first-slice subdirectory and filename helpers | No identifier validation, no filesystem access, no serialization |
| `src/macro_veritas/registry/specs.py` | Describe the frozen registry topology, gateway boundary, integrity policy, and planned error categories | No resolver engine, no manifest/index, no persistence runtime |
| `src/macro_veritas/registry/layout.py` | Return canonical first-slice relative paths and layout-vs-gateway boundary descriptors | Path/layout helper layer only; no path existence checks, no reads, no writes |
| `src/macro_veritas/registry/gateway.py` | Hold the gateway interface skeleton plus static result/error/mutation contract descriptors for first-slice cards | Interface skeleton only; no implemented retrieval, no persistence, no serializer calls |
| `src/macro_veritas/registry/errors.py` | Freeze the domain-level registry error taxonomy used by gateway contracts | No recovery engine, no exception routing framework, no runtime enforcement by itself |

No separate `macro_veritas.registry.contracts` module is introduced in this
round. The minimal contract TypedDicts stay in `src/macro_veritas/shared/types.py`.

## Internal Command Skeleton Modules

The next command layer is frozen as an internal adapter layer beneath the
public CLI scaffold and above future gateway/governance execution.

| Code Path | Current Role | Explicit Boundary |
| --- | --- | --- |
| `src/macro_veritas/commands/common.py` | Hold shared command-contract style descriptors and lightweight command metadata helpers | No runtime dispatch, no public CLI registration, no side effects |
| `src/macro_veritas/commands/ingest.py` | Internal skeleton for the reserved `ingest` family | Parser-builder + handler contract only; no registry writes, no public exposure |
| `src/macro_veritas/commands/bind.py` | Internal skeleton for the reserved `bind` family | Parser-builder + handler contract only; no filesystem checks, no public exposure |
| `src/macro_veritas/commands/extract.py` | Internal skeleton for the reserved `extract` family | Parser-builder + handler contract only; no parsing engine, no public exposure |
| `src/macro_veritas/commands/audit.py` | Internal skeleton for the reserved `audit` family | Parser-builder + handler contract only; no audit engine, no public exposure |
| `src/macro_veritas/commands/review.py` | Internal skeleton for the reserved `review` family | Parser-builder + handler contract only; no prosecution workflow, no public exposure |
| `src/macro_veritas/commands/run.py` | Internal skeleton for the reserved `run` family | Parser-builder + handler contract only; no scientific execution, no public exposure |
| `src/macro_veritas/commands/grade.py` | Internal skeleton for the reserved `grade` family | Parser-builder + handler contract only; no evidence grading logic, no public exposure |

Each command-family module contains only parser-builder and handler contracts
plus static descriptors. No family gets a deep subpackage tree in this round.

## Current Package Shape

The current governance-aligned skeleton should stay small:

```text
src/macro_veritas/
  __init__.py
  __main__.py
  cli.py
  commands/
    __init__.py
    common.py
    ingest.py
    bind.py
    extract.py
    audit.py
    review.py
    run.py
    grade.py
  config.py
  governance/
    __init__.py
    a_header.py
    departments/
      __init__.py
      personnel.py
      registry.py
      standards.py
      operations.py
      infrastructure.py
      review.py
  registry/
    __init__.py
    study.py
    dataset.py
    claim.py
    errors.py
    gateway.py
    layout.py
    specs.py
  runs/
    __init__.py
    specs.py
  audit/
    __init__.py
    specs.py
  prosecution/
    __init__.py
    specs.py
  shared/
    __init__.py
    naming.py
    types.py
```

## Boundary Rules For This Round

- Governance labels stay human-facing in docs.
- Code names stay ASCII and English.
- Department modules may expose office-level descriptor APIs, but they do not become runtime handlers.
- `macro_veritas.registry.study`, `macro_veritas.registry.dataset`, and `macro_veritas.registry.claim` are the current home of frozen card contract definitions.
- `docs/registry_layout.md` is the source of truth for first-slice registry filesystem conventions.
- `docs/registry_io_boundary.md` is the source of truth for future registry access and mutation responsibility.
- `docs/gateway_contracts.md` is the source of truth for gateway result, error, and mutation-plan communication semantics.
- `docs/cli_command_contracts.md` is the source of truth for reserved internal command-family contracts.
- `macro_veritas.registry.gateway` is the sole planned internal boundary for future registry card retrieval and persistence.
- `macro_veritas.commands` is the reserved internal command-family layer between the current public CLI scaffold and future gateway/governance operations.
- `macro_veritas.shared.naming` and `macro_veritas.registry.layout` remain static naming/path helper layers only.
- Higher layers must consume gateway contracts rather than raw filesystem semantics.
- Higher command layers must consume gateway/governance contracts rather than raw filesystem semantics.
- The registry modules in this round remain interface or metadata modules; they do not implement registry IO.
- CLI and governance code must not do raw path traversal or raw file access for registry cards.
- Prosecution remains distinct from routine review and should not be folded into `macro_veritas.governance.departments.review`.
- Reserved command families may be aligned to governance domains in docs and internal skeletons, but current public CLI behavior does not change.
- This round must not add FastAPI, SQL, registry IO, notebook-centric workflow, evidence grading logic, or CellVoyager integration.
