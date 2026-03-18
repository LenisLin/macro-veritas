# API Specifications

## Scope

Despite the filename, the current public interface is a local CLI contract only.

MacroVeritas v0.1 does not expose a web API.

- No FastAPI service
- No REST or HTTP endpoints
- No SQL-backed service layer

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

## Planned Next CLI Families

The following command families are design placeholders only. They are not implemented yet, and their exact arguments remain open.

- `ingest`: add new study, dataset, or claim records into the planned registry
- `bind`: associate registry records with concrete raw or processed artifact locations
- `extract`: capture claim or metadata fragments from curated sources into project records
- `grade`: assemble a lightweight evidence judgment view for a claim
- `audit`: record review outcomes such as pass, return, or escalate

No future command family in this section should be treated as a locked implementation contract yet.
