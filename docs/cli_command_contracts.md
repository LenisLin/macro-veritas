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

- Thirteen narrow public exceptions now exist: `ingest study`, `ingest dataset`,
  `ingest claim`, `ingest claim --from-file`, `show study`, `show dataset`,
  `show claim`, `list studies`, `list datasets`, `list claims`, `delete study`,
  `delete dataset`, and `delete claim`.
- Those public paths are thin adapters over the same narrow internal ingest,
  show, list, and delete bridge modules.
- The rest of the command families remain reserved and non-public.

## Command Families

### `ingest`

- Owning module: `macro_veritas.commands.ingest`
- Owning domain: Registry Department / 户部, intake boundary
- Purpose: execute the current StudyCard, DatasetCard, and ClaimCard ingest
  bridges, including the single-file YAML paths for StudyCard, DatasetCard,
  and ClaimCard, while keeping update/patch ingest semantics deferred
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `StudyCardPayload`, `DatasetCardPayload`,
  `ClaimCardPayload`
- Expected primary inputs: internal StudyCard, DatasetCard, or ClaimCard
  ingest input; StudyCard, DatasetCard, or ClaimCard single-file YAML
  mapping input; target
  card-family label; full-card StudyCard/DatasetCard/ClaimCard payload
  prepared from normalized intake input; and provenance/reference notes already
  carried by those inputs
- Expected primary outputs: StudyCard, DatasetCard, or ClaimCard gateway
  create-plan request; StudyCard, DatasetCard, or ClaimCard gateway create
  execution; and an internal command result mapping
- Expected dependency boundary: registry governance intake descriptors,
  card-contract docs, payload-contract docs, runtime docs, public StudyCard,
  DatasetCard, and ClaimCard file-ingest docs, and registry gateway
  create-planning/create contracts
- Public paths now:
  - `macro_veritas ingest study` is a thin adapter over the StudyCard bridge
  - `macro_veritas ingest study --from-file` is a thin adapter over the same StudyCard bridge after YAML file load and normalization
  - `macro_veritas ingest dataset` is a thin adapter over the DatasetCard bridge
  - `macro_veritas ingest dataset --from-file` is a thin adapter over the same DatasetCard bridge after YAML file load and normalization
  - `macro_veritas ingest claim` is a thin adapter over the ClaimCard bridge
  - `macro_veritas ingest claim --from-file` is a thin adapter over the same ClaimCard bridge after YAML file load and normalization
- Runtime status now:
  - public StudyCard create-only ingest is implemented through normalized
    command input, `plan_create_study_card(...)`, and `create_study_card(...)`
  - public DatasetCard create-only ingest is implemented through normalized
    command input, `plan_create_dataset_card(...)`, and `create_dataset_card(...)`
  - public ClaimCard create-only ingest is implemented through normalized
    command input, `plan_create_claim_card(...)`, and `create_claim_card(...)`
  - public StudyCard file-based ingest is implemented through YAML mapping load,
    file-input normalization, `plan_create_study_card(...)`, and
    `create_study_card(...)`
  - public DatasetCard file-based ingest is implemented through YAML mapping load,
    file-input normalization, `plan_create_dataset_card(...)`, and
    `create_dataset_card(...)`
  - public ClaimCard file-based ingest is implemented through YAML mapping load,
    file-input normalization, `plan_create_claim_card(...)`, and
    `create_claim_card(...)`
  - missing parent `StudyCard` failures for DatasetCard and ClaimCard ingest
    are translated to a clean command-level `missing_reference` result
  - missing referenced `DatasetCard` failures for ClaimCard ingest are
    translated to a clean command-level `missing_reference` result
- Still deferred inside `ingest`: StudyCard update/patch ingest, DatasetCard
  update/patch ingest, ClaimCard update/patch ingest, batch file ingest, and
  broader identifier allocation
  behavior
- Non-goals in this milestone: no StudyCard, DatasetCard, or ClaimCard
  update/patch ingest; no StudyCard or DatasetCard `--from-file` ingest; no
  batch ingest; no scientific logic; no evidence grading

### `show`

- Owning module: `macro_veritas.commands.show`
- Owning domain: Registry Department / 户部, read boundary
- Purpose: execute the current StudyCard, DatasetCard, and ClaimCard by-id
  read bridges while keeping list/search/update/delete semantics deferred
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: read-only `StudyCardPayload`,
  `DatasetCardPayload`, and `ClaimCardPayload`
- Expected primary inputs: internal by-id StudyCard, DatasetCard, or ClaimCard
  input carrying a target card-family label plus one canonical ID
- Expected primary outputs: StudyCard, DatasetCard, or ClaimCard gateway
  get-by-id request plus either the raw hydrated card mapping or a narrow
  command failure result
- Expected dependency boundary: registry governance read descriptors,
  card-contract docs, gateway-contract docs, and registry gateway get-by-id
  contracts
- Public paths now:
  - `macro_veritas show study` is a thin adapter over the StudyCard bridge
  - `macro_veritas show dataset` is a thin adapter over the DatasetCard bridge
  - `macro_veritas show claim` is a thin adapter over the ClaimCard bridge
- Runtime status now:
  - public StudyCard by-id show is implemented through normalized command
    input and `get_study_card(...)`
  - public DatasetCard by-id show is implemented through normalized command
    input and `get_dataset_card(...)`
  - public ClaimCard by-id show is implemented through normalized command
    input and `get_claim_card(...)`
  - missing target card failures are translated to a clean command-level
    `missing_reference` result
  - unsafe identifiers are translated to a clean command-level
    `unsupported_operation` result
- Still deferred inside `show`: list behavior, search behavior, filtering,
  relationship expansion, reverse lookups, and any update/delete semantics
- Non-goals in this milestone: no list/search/filter, no relationship
  expansion, no update/delete, no scientific logic, and no evidence grading

### `list`

- Owning module: `macro_veritas.commands.listing`
- Owning domain: Registry Department / 户部, discovery boundary
- Purpose: execute the current StudyCard, DatasetCard, and ClaimCard
  family-level discovery bridges while keeping search/filter/update/delete
  semantics deferred
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: read-only `StudyCardPayload`,
  `DatasetCardPayload`, and `ClaimCardPayload`
- Expected primary inputs: internal family-level StudyCard, DatasetCard, or
  ClaimCard input carrying the target card-family label only
- Expected primary outputs: StudyCard, DatasetCard, or ClaimCard gateway
  list-by-family request plus either compact summary output or a narrow
  command failure result
- Expected dependency boundary: registry governance discovery descriptors,
  card-contract docs, gateway-contract docs, and registry gateway list-by-family
  contracts
- Public paths now:
  - `macro_veritas list studies` is a thin adapter over the StudyCard bridge
  - `macro_veritas list datasets` is a thin adapter over the DatasetCard bridge
  - `macro_veritas list claims` is a thin adapter over the ClaimCard bridge
- Runtime status now:
  - public StudyCard family listing is implemented through normalized command
    input and `list_study_cards(...)`
  - public DatasetCard family listing is implemented through normalized command
    input and `list_dataset_cards(...)`
  - public ClaimCard family listing is implemented through normalized command
    input and `list_claim_cards(...)`
  - success output is a stable JSON array of compact summary entries rather than
    raw card payloads
  - registry list failures are translated to clean command-level failures
- Still deferred inside `list`: search behavior, filtering, pagination,
  relationship expansion, reverse lookups, and any update/delete semantics
- Non-goals in this milestone: no show expansion, no search/filter/query, no
  relationship expansion, no update/delete, no scientific logic, and no
  evidence grading

### `delete`

- Owning module: `macro_veritas.commands.delete`
- Owning domain: Registry Department / 户部, mutation boundary
- Purpose: execute the current StudyCard, DatasetCard, and ClaimCard by-id
  delete bridges while keeping force/cascade/filter/update semantics deferred
- Payload contract source: none; delete consumes narrow by-id command input and
  does not prepare full-card payloads
- Expected primary inputs: internal by-id StudyCard, DatasetCard, or ClaimCard
  input carrying a target card-family label plus one canonical ID
- Expected primary outputs: StudyCard, DatasetCard, or ClaimCard gateway delete
  request plus a narrow command result
- Expected dependency boundary: registry governance mutation descriptors,
  registry-io docs, gateway-contract docs, public delete doc, and registry
  gateway delete contracts
- Public paths now:
  - `macro_veritas delete study` is a thin adapter over the StudyCard bridge
  - `macro_veritas delete dataset` is a thin adapter over the DatasetCard bridge
  - `macro_veritas delete claim` is a thin adapter over the ClaimCard bridge
- Runtime status now:
  - public StudyCard by-id delete is implemented through normalized command
    input and `delete_study_card(...)`
  - public DatasetCard by-id delete is implemented through normalized command
    input and `delete_dataset_card(...)`
  - public ClaimCard by-id delete is implemented through normalized command
    input and `delete_claim_card(...)`
  - dependency-blocked deletes are translated to a clean command-level
    `dependency_exists` result
  - missing target cards are translated to a clean command-level
    `missing_reference` result
- Still deferred inside `delete`: force delete, cascade delete, delete by
  search/filter, restore, trash/archive, and update semantics
- Non-goals in this milestone: no force delete, no cascade delete, no
  delete-by-filter, no restore/trash semantics, no scientific logic, and no
  evidence grading

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
- runtime execution exists only for the StudyCard, DatasetCard, and ClaimCard
  ingest bridges, the StudyCard, DatasetCard, and ClaimCard by-id show
  bridges, the StudyCard, DatasetCard, and ClaimCard family-level list
  bridges, and the StudyCard, DatasetCard, and ClaimCard by-id delete bridges;
  other command families remain descriptor/skeleton-only
- file IO is allowed through the registry gateway for registry mutations and
  through the documented single-file YAML intake paths at `ingest study
  --from-file`, `ingest dataset --from-file`, and `ingest claim --from-file`
- raw `argparse.Namespace` objects remain outside the command-to-gateway
  boundary
- no silent side effects

Interpretation:

- the public CLI adapts parsed `ingest study`, `ingest study --from-file`,
  `ingest dataset`, `ingest dataset --from-file`, `ingest claim`,
  `ingest claim --from-file`, `show study`, `show dataset`, `show claim`,
  `list studies`, `list datasets`, `list claims`, `delete study`,
  `delete dataset`, and `delete claim` commands into typed mappings and then
  into normalized internal inputs before calling the gateway
- the command layer does not write canonical registry files directly
- the command layer does not bypass the gateway
- `handle_ingest_command(...)` accepts mapping-based internal input and
  supports StudyCard, DatasetCard, and ClaimCard
- `handle_show_command(...)` accepts mapping-based internal input and supports
  StudyCard, DatasetCard, and ClaimCard by-id reads
- `handle_list_command(...)` accepts mapping-based internal input and supports
  StudyCard, DatasetCard, and ClaimCard family-level discovery reads
- `handle_delete_command(...)` accepts mapping-based internal input and
  supports StudyCard, DatasetCard, and ClaimCard by-id delete execution
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
- `python -m macro_veritas ingest claim` is public for create-only `ClaimCard`
  ingest.
- `python -m macro_veritas ingest study --from-file` is public for single-file
  YAML `StudyCard` create ingest.
- `python -m macro_veritas ingest dataset --from-file` is public for single-file
  YAML `DatasetCard` create ingest.
- `python -m macro_veritas ingest claim --from-file` is public for single-file
  YAML `ClaimCard` create ingest.
- `python -m macro_veritas show study` is public for by-id `StudyCard` read.
- `python -m macro_veritas show dataset` is public for by-id `DatasetCard`
  read.
- `python -m macro_veritas show claim` is public for by-id `ClaimCard` read.
- `python -m macro_veritas list studies` is public for compact `StudyCard` discovery.
- `python -m macro_veritas list datasets` is public for compact `DatasetCard` discovery.
- `python -m macro_veritas list claims` is public for compact `ClaimCard` discovery.
- `python -m macro_veritas delete study` is public for referentially-aware
  by-id `StudyCard` delete.
- `python -m macro_veritas delete dataset` is public for referentially-aware
  by-id `DatasetCard` delete.
- `python -m macro_veritas delete claim` is public for by-id `ClaimCard`
  delete.
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` remain non-public.
