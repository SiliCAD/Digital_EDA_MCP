# Digital_EDA_MCP Architecture, Design Patterns & Gotchas Guide

This document captures key technical findings, architecture details, and critical gotchas for developers or AI agents extending this repository.

---

## 🏗️ 1. Core Architecture

```
                                  ┌───────────────────────────┐
                                  │         server.py         │
                                  │ (FastMCP: remote_control, │
                                  │   workboard, report_issue)│
                                  └──────────────┬────────────┘
                                                 │
          ┌──────────────────────────────────────┼──────────────────────────────────────┐
          ▼                                      ▼                                      ▼
┌───────────────────────────┐          ┌───────────────────────────┐          ┌───────────────────────────┐
│      remote_session       │          │     WorkBoardClient       │          │       IssueReporter       │
│(config_remote_control.json│          │  (Git + SCP Sync Engine)  │          │   (GitHub CLI Integration)│
│   isolated SSH session)   │          └─────────────┬─────────────┘          └───────────────────────────┘
└───────────────────────────┘                        │
                                                     ▼
                                       ┌───────────────────────────┐
                                       │         SCPClient         │
                                       │ (Binary & Tree Transfers) │
                                       └───────────────────────────┘
```

- **[server.py](../server.py)**: Exposes `@mcp.tool()` definitions (`remote_control`, `workboard`, `report_issue`) to MCP clients. Instantiates isolated `RemoteSession` and `WorkBoardClient` instances. Handles per-instance logging in `logs/` and `temp/`.
- **[config/](../config)**: Holds configuration files (`config_remote_control.json`). `RemoteSession.load_config()` automatically resolves tool-specific configs with a fallback to `config.json`.
- **[workboard_client.py](../src/clients/workboard_client.py)**: Git-backed local workspace synchronization engine with baseline tracking (`.workboard.json`), unified diff calculation, and commit history.
- **[ssh_client.py](../src/core/ssh_client.py)**: Low-level transport layer managing persistent, stateful `csh` shell sessions over SSH (`RemoteSession`).
- **[scp_client.py](../src/core/scp_client.py)**: Fast binary and directory transfer client executing OpenSSH SCP with batch mode and config resolution.

---

## ⚠️ 2. Critical Gotchas & Execution Rules

### 1. `csh` Shell & Tilde Expansion Quoting (CRITICAL)
- **Problem**: In `csh`, passing single-quoted tilde paths like `'~/Desktop/UVM'` to `cd` **disables shell tilde expansion**.
- **Symptom**: `csh` searches for a literal directory named `'~/Desktop/UVM'` and **hangs indefinitely waiting for input**, causing 3-minute MCP timeouts.
- **Rule**: Always format tilde paths starting with `~` as `$HOME` before passing to `csh` commands:
  ```python
  safe_dir = f"$HOME{path[1:]}" if path.startswith("~") else shlex.quote(path)
  cmd = f"cd {safe_dir}"
  ```

### 2. Persistent Shell Session & Sentinel Protocol
- `RemoteSession` in `ssh_client.py` uses a single long-running `csh` subprocess over SSH (`subprocess.Popen(['ssh', '-o', 'BatchMode=yes', host, 'csh'])`).
- Environment scripts (`/cadence/cshrc` or custom EDA module setup) are sourced **once** on startup.
- Sentinels (`__CMD_FINISHED_[random_hex]__`) are printed with `$status` to detect command completion and exit codes without closing the shell.
- `stderr` is merged into `stdout` (`stderr=subprocess.STDOUT`) to prevent pipe buffer deadlocks.

### 3. FastMCP Tool Return Type Contract
- All FastMCP tools annotated with `-> str` **must explicitly return a valid string**.
- Returning `None` (or omitting `return` in Python) causes the FastMCP stdio transport layer to hang or crash serialization.

### 4. Windows Path Escaping in Subprocess & JSON
- On Windows hosts, local file paths contain backslashes (`\`).
- When writing JSON configs, avoid raw string formatting like `f'{{"path": "{self.path}"}}'`.
- Always serialize using `json.dump()` or `json.dumps()` to properly escape backslashes as `\\`.

---

## 🔄 3. WorkBoard Version-Controlled Workspace Architecture

```
[Local Host]                                           [Remote EDA Cluster]
./workboard/<name>/                                     ~/Desktop/UVM/...
  ├── rtl/                                                 ├── rtl/
  ├── tb/                                                  ├── tb/
  ├── .workboard.json (Sync Manifest)                      └── cov_work/
  └── .git/ (Local Git Repository)
       │                                                         ▲
       │ 1. Download via SCP Client                              │
       │─────────────────────────────────────────────────────────│
       │ 2. Local git add & git commit (Records Baseline SHA)
       │ 3. Update .workboard.json {"last_synced_commit": "SHA"}
       ▼
  [WorkBoard Push / Export] ────────────────────────────────────► [Remote Update]
```

- **Manifest Sync Contract**: Every tracked file records:
  - `remote_path`: Cluster file location.
  - `last_synced_commit`: Local Git commit SHA at the time of synchronization.
  - `last_synced_timestamp`: ISO 8601 timestamp.
- **Unified Diff Engine**: Compares remote bytes with local working tree before pushing or pulling, preventing accidental clobbering of remote changes.

---

## 📜 4. Logging & Diagnostics

- **Session Activity Logs**: Saved automatically to `logs/eda_mcp_YYYYMMDD_HHMMSS_<PID>.log`.
- **Git Ignore**: The `logs/` and `temp/` folders are ignored by git (`.gitignore`).
- **Log Contents**: Logs contain timestamped records of every tool call (`[TOOL CALL]`), parameters, duration, and exit status (`[TOOL RESULT]`).
