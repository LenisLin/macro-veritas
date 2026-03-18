## {{ title }}

{{ one_liner }}

### Project Overview

MacroVeritas is a docs-first, CLI-first Python project scaffold for a future claim-centered evidence grading and data-level verification system focused on melanoma, immune checkpoint inhibition, and macrophage literature.

This repository is only the initialization step. No scientific system, evidence grading engine, registry business logic, or analysis pipeline is implemented yet.

### Current Status

- Stage: {{ stage }}
- Package name: `{{ package_name }}`
- Repository name: `{{ name }}`
- Implemented now:
  - lightweight Python package scaffold
  - minimal CLI commands for status, config inspection, and layout initialization
  - docs describing scope, constraints, and intended architecture
  - committed project config with explicit external data root
- Not implemented now:
{% for item in non_goals %}
  - {{ item }}
{% endfor %}

### Design Principles

{% for item in design_principles %}
- {{ item }}
{% endfor %}

### Repository Layout

```text
{% for item in repo_layout %}
{{ item }}
{% endfor %}
```

### Local Paths

- Project root: `{{ project_root }}`
- Data root: `{{ data_root }}`
- Default config file: `config/project.yaml`

### Initialization Notes

{% for item in initialization_notes %}
- {{ item }}
{% endfor %}

### Next Milestone

{{ next_milestone }}
