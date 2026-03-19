# API Specifications

## Scope

Despite the filename, the current public interface is a local CLI contract only.

MacroVeritas v0.1 does not expose a web API.

- No FastAPI service
- No REST or HTTP endpoints
- No SQL-backed service layer

The current CLI can be reached through the installed console script or via `python -m macro_veritas` from the repository checkout. This document uses command family names as interface labels and does not claim that future groups already exist.

`docs/cli_command_contracts.md` is the source of truth for the reserved
internal command-family contracts. Those reserved families are not yet part of
the stable public CLI surface.

## Implemented CLI Commands

The following commands exist in the current scaffold.

### `macro_veritas status`

- Purpose: report the current scaffold stage, project identity, config path, data root, and layout-path presence.
- Expected effect: reads the resolved project configuration and prints a human-readable status summary to standard output.
- What it should not do: create directories, write registry objects, run scientific logic, or mutate configuration.

### `macro_veritas show-config`

- Purpose: show the resolved project configuration and derived layout paths.
- Expected effect: reads the project configuration and prints a JSON display view to standard output.
- What it should not do: change configuration, inspect scientific content, contact external services, or create filesystem artifacts.

### `macro_veritas init-layout`

- Purpose: initialize the placeholder filesystem layout under the configured data root.
- Expected effect: creates only missing top-level scaffold directories; with `--dry-run`, reports planned creations without writing.
- What it should not do: delete or overwrite existing content, populate registry cards, infer scientific metadata, or run analysis logic.

## Reserved Internal Command Families

The following names are reserved for internal skeletonization and future command
family work. They are not yet public CLI commands, do not currently define
flags or options, and should not be treated as exposed runtime behavior.

Their internal command-family contract is frozen in
[`docs/cli_command_contracts.md`](cli_command_contracts.md). Governance
alignment remains documentation-only and is not an implementation claim.

| CLI Group | Intended Purpose | Current Status | Internal Skeleton Module | Governance Domain Alignment |
| --- | --- | --- | --- | --- |
| `ingest` | Add initial study, dataset, or claim records into the planned registry. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.ingest` | Registry Department / 户部 |
| `bind` | Associate registry records with concrete raw, processed, or run-facing artifact locations. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.bind` | Registry Department / 户部 |
| `extract` | Capture structured claim or metadata fragments from curated sources into project records. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.extract` | Registry Department / 户部 |
| `audit` | Record routine review outcomes such as `pass`, `return`, or `escalate`. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.audit` | Review Department / 刑部 |
| `review` | Hold the future escalated review / prosecution lane after a routine audit escalation. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.review` | Prosecution / 检察院 |
| `run` | Manage declared run or bundle boundaries around future reanalysis work. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.run` | Operations Department / 兵部 |
| `grade` | Assemble a lightweight evidence judgment view for a claim. | Reserved internal skeleton only; not public CLI. | `macro_veritas.commands.grade` | Review-adjacent; provisionally aligned to Review Department / 刑部 |
