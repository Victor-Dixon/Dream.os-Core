# dream.os v7 — Modular Cognitive Swarm

A voice-triggered, remotely executable, multi-agent system for autonomous repo management.

## Quick Start

```bash
# Install
pip install -e ".[all]"

# Dry run (safe, default)
dreamos "update all repos"

# Live mode
DREAMOS_DRY_RUN=0 dreamos "fix lint"

# SSH from phone
ssh user@your-pc "DREAMOS_DRY_RUN=0 dreamos 'deploy'"
```

## CLI Flags

```
dreamos "goal"          Run a goal
dreamos --list-goals    Show all known goals
dreamos --list-repos    Show discovered repos
dreamos --list-tools    Show registered tools
dreamos --dry-run       Force dry-run mode
dreamos --live          Force live mode (real changes!)
dreamos --verbose       Debug logging
```

## Environment Variables

| Variable                | Default         | Description                        |
|-------------------------|-----------------|------------------------------------|
| `DREAMOS_GITHUB_DIR`    | `~/github`      | Root dir to scan for repos         |
| `DREAMOS_DRY_RUN`       | `1`             | `0` = live, `1` = dry-run          |
| `DREAMOS_WORKERS`       | `4`             | Parallel thread count              |
| `DREAMOS_RETRIES`       | `2`             | Failures before skipping a repo    |
| `DREAMOS_SAFE_REPOS`    | *(all)*         | Comma-separated repo name allowlist|
| `DREAMOS_LOG`           | `~/dreamos.log` | Log file path                      |

## Known Goals

| Goal          | Pipeline                              |
|---------------|---------------------------------------|
| `status`      | status                                |
| `update`      | pull → status                         |
| `check`       | status → lint                         |
| `sync`        | pull → status → diff                  |
| `test`        | pull → lint → test                    |
| `fix lint`    | pull → lint → fix → test → commit → push |
| `deploy`      | pull → lint → test → commit → push    |

## Add a New Tool

```python
# dreamos/tools/my_tools.py
from dreamos.tools.base import BaseTool, ToolResult

class MyTool(BaseTool):
    name = "mytool"
    description = "Does something useful"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        # your logic here
        return ToolResult.success("done!")
```

Then register it in `dreamos/tools/__init__.py`:
```python
from .my_tools import MyTool
registry.register(MyTool())
```

## Run Tests

```bash
pytest dreamos/tests/ -v
```

## Architecture

```
dreamos/
├── config/      — Settings, goal plans
├── core/        — Agent, Memory, RAGEngine, SwarmController
├── tools/       — Git, lint, test tool implementations
├── plans/       — Goal decomposer, veto engine
├── logging/     — Colored dual logger
├── cli/         — Entry point (argparse)
└── tests/       — Full test suite
```
