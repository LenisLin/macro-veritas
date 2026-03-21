# CLI Command Contracts

## Purpose

This document freezes the current internal command-family contracts for
MacroVeritas.

- It defines the reserved internal command families for the current phase.
- It defines the expected owner, purpose, inputs, outputs, and dependency
  boundary of each family.
- It defines the shared internal command style used by the modules in
  `macro_veritas.commands`.
- Concrete gateway-facing payload families are frozen separately in
  [`docs/payload_contracts.md`](payload_contracts.md).

This document now describes a mixed implementation state.

- Two narrow public exceptions now exist: `ingest study` and `ingest dataset`.
- Those public paths are thin adapters over the same narrow internal ingest
  bridge module.
- ClaimCard ingest remains internal and non-public.
- The rest of the command families remain reserved and non-public.

## Command Families

### `ingest`

- Owning module: `macro_veritas.commands.ingest`
- Owning domain: Registry Department / 户部, intake boundary
- Purpose: execute the current StudyCard and DatasetCard ingest bridges while
  keeping ClaimCard ingest non-runtime and non-public
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `StudyCardPayload`, `DatasetCardPayload`,
  `ClaimCardPayload`
- Expected primary inputs: internal StudyCard or DatasetCard ingest input,
  target card-family label, full-card StudyCard/DatasetCard payload prepared
  from normalized intake input, and provenance/reference notes already carried
  by those inputs
- Expected primary outputs: StudyCard or DatasetCard gateway create-plan
  request, StudyCard or DatasetCard gateway create execution, and an internal
  command result mapping
- Expected dependency boundary: registry governance intake descriptors,
  card-contract docs, payload-contract docs, runtime docs, and registry gateway
  create-planning/create contracts
- Public paths now:
  - `macro_veritas ingest study` is a thin adapter over the StudyCard bridge
  - `macro_veritas ingest dataset` is a thin adapter over the DatasetCard bridge
- Runtime status now:
  - public StudyCard create-only ingest is implemented through normalized
    command input, `plan_create_study_card(...)`, and `create_study_card(...)`
  - public DatasetCard create-only ingest is implemented through normalized
    command input, `plan_create_dataset_card(...)`, and `create_dataset_card(...)`
  - missing parent `StudyCard` failures for DatasetCard ingest are translated to
    a clean command-level `missing_reference` result
- Still deferred inside `ingest`: ClaimCard ingest runtime/public exposure,
  StudyCard update/patch ingest, DatasetCard update/patch ingest, and broader
  identifier allocation behavior
- Non-goals in this milestone: no ClaimCard public ingest, no StudyCard or
  DatasetCard update/patch ingest, no scientific logic, no evidence grading

### `bind`

- Owning module: `macro_veritas.commands.bind`
- Owning domain: Registry Department / 户部, locator-binding boundary
- Purpose: stage the association of governed objects with raw, processed, or
  artifact-facing locators
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `StudyCardPayload`, `DatasetCardPayload`,
  `ClaimCardPayload`
- Expected primary inputs: target object identity, locator reference, binding
  provenance note, full replacement payload when an update plan is needed
- Expected primary outputs: future gateway read/update-plan request and a
  binding summary
- Non-goals in this milestone: no filesystem checks, no path mutation, no
  gateway execution, no public CLI exposure

### `extract`

- Owning module: `macro_veritas.commands.extract`
- Owning domain: Registry Department / 户部, extraction-planning boundary
- Purpose: stage claim or metadata capture tasks against curated sources
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `ClaimCardPayload` for create/update and
  `StudyCardPayload` / `DatasetCardPayload` for update follow-up
- Expected primary inputs: curated source reference, extraction scope note,
  linked study or dataset context, full-card payload for a future create/update
  plan
- Expected primary outputs: future gateway read/create/update-plan request and
  an extraction-task summary
- Non-goals in this milestone: no text parsing, no metadata extraction engine,
  no gateway execution, no public CLI exposure

### `audit`

- Owning module: `macro_veritas.commands.audit`
- Owning domain: Review Department / 刑部, routine audit lane
- Purpose: stage routine audit checks and routine audit outcome recording around
  reviewable objects
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read and list DTOs; no first-slice mutation payload preparation
- Expected primary outputs: audit action summary and future audit-record-facing
  planning request
- Non-goals in this milestone: no audit engine, no adjudication runtime, no
  evidence grading, no public CLI exposure

### `review`

- Owning module: `macro_veritas.commands.review`
- Owning domain: Prosecution / 检察院, escalated review lane
- Purpose: stage escalated review / prosecution intake after routine audit
  escalation
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read DTOs; no first-slice mutation payload preparation
- Expected primary outputs: case-intake summary and prosecution handoff note
- Non-goals in this milestone: no case management, no sanctions, no workflow
  engine, no public CLI exposure

### `run`

- Owning module: `macro_veritas.commands.run`
- Owning domain: Operations Department / 兵部, run/bundle boundary
- Purpose: stage future run or bundle commands around declared inputs, methods,
  and outputs
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read DTOs; no first-slice mutation payload preparation
- Expected primary outputs: run-scope summary and future bundle-planning request
- Non-goals in this milestone: no scientific execution, no bundle generation,
  no orchestration runtime, no CellVoyager integration, no public CLI exposure

### `grade`

- Owning module: `macro_veritas.commands.grade`
- Owning domain: Review-adjacent grading boundary, provisionally aligned with
  Review Department / 刑部
- Purpose: stage a future evidence-judgment or claim-grading command family
  without locking grading runtime behavior
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `ClaimCard` plus linked `DatasetCard` /
  `StudyCard` read DTOs; no first-slice mutation payload preparation
- Expected primary outputs: grading summary and future evidence-judgment request
- Non-goals in this milestone: no evidence grading logic, no scoring engine,
  no report assembly runtime, no public CLI exposure

## Command Style

The frozen internal command style is conservative:

- one module per reserved command family under `macro_veritas.commands`
- one `build_parser(subparsers_or_parser: object) -> None` hook per family
- one `handle_<family>_command(args: object) -> object` hook per family
- static descriptor helpers for family metadata and dependency declarations
- static payload-touchpoint descriptors that point to
  [`docs/payload_contracts.md`](payload_contracts.md)
- runtime execution exists only for the StudyCard and DatasetCard ingest
  bridges; other command families remain descriptor/skeleton-only
- file IO is allowed only through the registry gateway for explicitly
  documented runtime paths
- raw `argparse.Namespace` objects remain outside the command-to-gateway boundary
- no silent side effects

Interpretation:

- the public CLI adapts parsed `ingest study` and `ingest dataset` flags into
  typed mappings and then into normalized internal ingest inputs before payload
  preparation
- the command layer does not write files directly
- the command layer does not bypass the gateway
- `handle_ingest_command(...)` accepts mapping-based internal input and supports
  StudyCard plus DatasetCard only
- ClaimCard ingest remains unsupported at the runtime layer in this milestone
- broader option and flag design remains deferred

## Public Exposure Rule

These command families are reserved, with only narrow documented public
exceptions.

- `python -m macro_veritas status` remains public.
- `python -m macro_veritas show-config` remains public.
- `python -m macro_veritas init-layout` remains public.
- `python -m macro_veritas ingest study` is public for create-only `StudyCard`
  ingest.
- `python -m macro_veritas ingest dataset` is public for create-only
  `DatasetCard` ingest.
- `ClaimCard` ingest remains non-public and skeleton-only.
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` remain non-public.
