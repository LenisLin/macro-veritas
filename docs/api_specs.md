# API Specifications

## Scope

Despite the filename, the current public interface is a local CLI contract only.

MacroVeritas v0.1 does not expose a web API.

- No FastAPI service
- No REST or HTTP endpoints
- No SQL-backed service layer

The current CLI can be reached through the installed console script or via
`python -m macro_veritas` from the repository checkout.

`docs/cli_command_contracts.md` is the source of truth for the reserved
command-family contracts and the current public-vs-internal split.

## Stable Public CLI Commands

The following commands are the current stable public CLI surface.

### `macro_veritas status`

- Purpose: report the current scaffold stage, project identity, config path,
  data root, and layout-path presence.
- Expected effect: reads the resolved project configuration and prints a
  human-readable status summary to standard output.
- What it should not do: create directories, write registry objects, run
  scientific logic, or mutate configuration.

### `macro_veritas show-config`

- Purpose: show the resolved project configuration and derived layout paths.
- Expected effect: reads the project configuration and prints a JSON display
  view to standard output.
- What it should not do: change configuration, inspect scientific content,
  contact external services, or create filesystem artifacts.

### `macro_veritas init-layout`

- Purpose: initialize the placeholder filesystem layout under the configured
  data root.
- Expected effect: creates only missing top-level scaffold directories; with
  `--dry-run`, reports planned creations without writing.
- What it should not do: delete or overwrite existing content, populate
  registry cards, infer scientific metadata, or run analysis logic.

### `macro_veritas ingest study`

- Purpose: create one canonical `StudyCard` from explicit CLI fields.
- Expected effect: converts explicit CLI flags into normalized StudyCard ingest
  input, prepares one `StudyCardPayload`, calls StudyCard create planning,
  calls StudyCard create execution, and writes one canonical YAML file through
  the registry gateway.
- What it should not do: update an existing `StudyCard`, ingest from a batch,
  infer scientific content, or bypass the gateway.
- Source of truth:
  [`docs/public_ingest_studycard_cli.md`](public_ingest_studycard_cli.md)

### `macro_veritas ingest study --from-file <path>`

- Purpose: create one canonical `StudyCard` from one YAML mapping file.
- Expected effect: loads one YAML mapping, normalizes it into the same
  StudyCard ingest input used by the flag-based path, prepares one
  `StudyCardPayload`, calls StudyCard create planning, calls StudyCard create
  execution, and writes one canonical YAML file through the registry gateway.
- What it should not do: scan directories, accept batches, update an existing
  `StudyCard`, or bypass the gateway.
- Source of truth:
  [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md)

### `macro_veritas ingest dataset`

- Purpose: create one canonical `DatasetCard` from explicit CLI fields.
- Expected effect: converts explicit CLI flags into normalized DatasetCard
  ingest input, prepares one `DatasetCardPayload`, calls DatasetCard create
  planning, calls DatasetCard create execution, and writes one canonical YAML
  file through the registry gateway.
- What it should not do: update an existing `DatasetCard`, ingest from a
  batch, infer scientific content, or bypass the gateway.
- Source of truth:
  [`docs/public_ingest_datasetcard_cli.md`](public_ingest_datasetcard_cli.md)

### `macro_veritas ingest dataset --from-file <path>`

- Purpose: create one canonical `DatasetCard` from one YAML mapping file.
- Expected effect: loads one YAML mapping, normalizes it into the same
  DatasetCard ingest input used by the flag-based path, prepares one
  `DatasetCardPayload`, calls DatasetCard create planning, calls DatasetCard
  create execution, and writes one canonical YAML file through the registry
  gateway.
- What it should not do: scan directories, accept batches, update an existing
  `DatasetCard`, or bypass the gateway.
- Source of truth:
  [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md)

### `macro_veritas ingest claim`

- Purpose: create one canonical `ClaimCard` from explicit CLI fields.
- Expected effect: converts explicit CLI flags into normalized ClaimCard ingest
  input, prepares one `ClaimCardPayload`, calls ClaimCard create planning,
  calls ClaimCard create execution, and writes one canonical YAML file through
  the registry gateway.
- What it should not do: update an existing `ClaimCard`, ingest from a batch,
  infer scientific content, bypass the gateway, or widen into evidence-grading
  or extraction workflow.
- Source of truth:
  [`docs/public_ingest_claimcard_cli.md`](public_ingest_claimcard_cli.md)

### `macro_veritas ingest claim --from-file <path>`

- Purpose: create one canonical `ClaimCard` from one YAML mapping file.
- Expected effect: loads one YAML mapping, normalizes it into the same
  ClaimCard ingest input used by the flag-based path, prepares one
  `ClaimCardPayload`, calls ClaimCard create planning, calls ClaimCard create
  execution, and writes one canonical YAML file through the registry gateway.
- What it should not do: scan directories, accept batches, update an
  existing `ClaimCard`, or bypass the gateway.
- Source of truth:
  [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md)

### `macro_veritas show study`

- Purpose: read one canonical `StudyCard` by explicit ID.
- Expected effect: converts the explicit `--study-id` flag into a narrow by-id
  input mapping, calls `get_study_card`, and prints the raw hydrated card
  mapping as JSON.
- What it should not do: list studies, search studies, expand related records,
  or bypass the gateway.
- Source of truth:
  [`docs/public_show_cli.md`](public_show_cli.md)

### `macro_veritas show dataset`

- Purpose: read one canonical `DatasetCard` by explicit ID.
- Expected effect: converts the explicit `--dataset-id` flag into a narrow
  by-id input mapping, calls `get_dataset_card`, and prints the raw hydrated
  card mapping as JSON.
- What it should not do: list datasets, search datasets, expand related
  records, or bypass the gateway.
- Source of truth:
  [`docs/public_show_cli.md`](public_show_cli.md)

### `macro_veritas show claim`

- Purpose: read one canonical `ClaimCard` by explicit ID.
- Expected effect: converts the explicit `--claim-id` flag into a narrow by-id
  input mapping, calls `get_claim_card`, and prints the raw hydrated card
  mapping as JSON.
- What it should not do: list claims, search claims, expand related records,
  or bypass the gateway.
- Source of truth:
  [`docs/public_show_cli.md`](public_show_cli.md)

### `macro_veritas list studies`

- Purpose: discover existing `StudyCard` identifiers through compact summaries.
- Expected effect: converts the public collection command into a narrow
  family-level input mapping, calls `list_study_cards`, and prints a JSON array
  of compact study summaries.
- What it should not do: return full raw StudyCard payloads, search, filter,
  expand related records, or bypass the gateway.
- Source of truth:
  [`docs/public_list_cli.md`](public_list_cli.md)

### `macro_veritas list datasets`

- Purpose: discover existing `DatasetCard` identifiers through compact summaries.
- Expected effect: converts the public collection command into a narrow
  family-level input mapping, calls `list_dataset_cards`, and prints a JSON
  array of compact dataset summaries.
- What it should not do: return full raw DatasetCard payloads, search, filter,
  expand related records, or bypass the gateway.
- Source of truth:
  [`docs/public_list_cli.md`](public_list_cli.md)

### `macro_veritas list claims`

- Purpose: discover existing `ClaimCard` identifiers through compact summaries.
- Expected effect: converts the public collection command into a narrow
  family-level input mapping, calls `list_claim_cards`, and prints a JSON array
  of compact claim summaries.
- What it should not do: return full raw ClaimCard payloads, search, filter,
  expand related records, or bypass the gateway.
- Source of truth:
  [`docs/public_list_cli.md`](public_list_cli.md)

### `macro_veritas delete study`

- Purpose: delete one canonical `StudyCard` by explicit ID.
- Expected effect: converts the explicit `--study-id` flag into a narrow by-id
  delete input mapping, calls `delete_study_card`, and removes the canonical
  YAML file only when no dependent `DatasetCard` or `ClaimCard` records exist.
- What it should not do: force delete, cascade delete, search, filter, update,
  or bypass the gateway.
- Source of truth:
  [`docs/public_delete_cli.md`](public_delete_cli.md)

### `macro_veritas delete dataset`

- Purpose: delete one canonical `DatasetCard` by explicit ID.
- Expected effect: converts the explicit `--dataset-id` flag into a narrow
  by-id delete input mapping, calls `delete_dataset_card`, and removes the
  canonical YAML file only when no dependent `ClaimCard` records exist.
- What it should not do: force delete, cascade delete, search, filter, update,
  or bypass the gateway.
- Source of truth:
  [`docs/public_delete_cli.md`](public_delete_cli.md)

### `macro_veritas delete claim`

- Purpose: delete one canonical `ClaimCard` by explicit ID.
- Expected effect: converts the explicit `--claim-id` flag into a narrow by-id
  delete input mapping, calls `delete_claim_card`, and removes the canonical
  YAML file when the target exists.
- What it should not do: force delete, cascade delete, search, filter, update,
  or bypass the gateway.
- Source of truth:
  [`docs/public_delete_cli.md`](public_delete_cli.md)

There is still no public search, filter, update, force delete, cascade delete,
or delete-by-filter capability for any card family.

## Command Families

The following command-family names are recognized in the current codebase.

| CLI Group | Intended Purpose | Current Status | Internal Module | Governance Domain Alignment |
| --- | --- | --- | --- | --- |
| `ingest` | Add initial study, dataset, or claim records into the planned registry. | Public for create-only `StudyCard` at `ingest study`, single-file `StudyCard` create at `ingest study --from-file`, create-only `DatasetCard` at `ingest dataset`, single-file `DatasetCard` create at `ingest dataset --from-file`, create-only `ClaimCard` at `ingest claim`, and single-file `ClaimCard` create at `ingest claim --from-file`; update semantics remain non-public. | `macro_veritas.commands.ingest` | Registry Department / 户部 |
| `show` | Read one study, dataset, or claim record by canonical ID. | Public for by-id `StudyCard` at `show study`, by-id `DatasetCard` at `show dataset`, and by-id `ClaimCard` at `show claim`; list/search/update/delete semantics remain non-public. | `macro_veritas.commands.show` | Registry Department / 户部 |
| `list` | Discover existing study, dataset, or claim identifiers by family. | Public for compact `StudyCard` summaries at `list studies`, compact `DatasetCard` summaries at `list datasets`, and compact `ClaimCard` summaries at `list claims`; search/filter/update/delete semantics remain non-public. | `macro_veritas.commands.listing` | Registry Department / 户部 |
| `delete` | Remove one study, dataset, or claim record by canonical ID. | Public for by-id `StudyCard` at `delete study`, by-id `DatasetCard` at `delete dataset`, and by-id `ClaimCard` at `delete claim`; force/cascade/search/filter/update semantics remain non-public. | `macro_veritas.commands.delete` | Registry Department / 户部 |
| `bind` | Associate registry records with concrete raw, processed, or run-facing artifact locations. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.bind` | Registry Department / 户部 |
| `extract` | Capture structured claim or metadata fragments from curated sources into project records. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.extract` | Registry Department / 户部 |
| `audit` | Record routine review outcomes such as `pass`, `return`, or `escalate`. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.audit` | Review Department / 刑部 |
| `review` | Hold the future escalated review / prosecution lane after a routine audit escalation. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.review` | Prosecution / 检察院 |
| `run` | Manage declared run or bundle boundaries around future reanalysis work. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.run` | Operations Department / 兵部 |
| `grade` | Assemble a lightweight evidence judgment view for a claim. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.grade` | Review-adjacent; provisionally aligned to Review Department / 刑部 |
