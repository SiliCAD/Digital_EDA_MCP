# DIGITAL_EDA_TOOL_CLIENTS_SPEC

## 1. WorkBoard Client ([`workboard_client.py`](../../src/clients/workboard_client.py))

### Git-Backed Workspace Synchronization State Machine
```
   [Agent / User Action]
           │
           ▼
   _resolve_workboard_name() (Finds active WorkBoard directory)
           │
           ▼
   _load_registry() (Reads .workboard.json metadata & tracked paths)
           │
           ▼
   SCPClient / RemoteSession File Transfer
           │
           ▼
   Local Git Operation (Commit, Diff, Log, Status)
```

### Core WorkBoard Capabilities:
- `initialize(workboard_name)`: Creates `workboard/<name>/` directory, creates `.workboard.json` registry, and initializes a dedicated local Git repository (`git init`).
- `add(remote_path, local_path, workboard_name)`: Fetches a remote Verilog/SystemVerilog RTL file, UVM testbench, or report via SCP and registers it for tracking in the WorkBoard.
- `export(local_path, remote_path, workboard_name)`: Copies a local file into the WorkBoard, pushes it via SCP to the remote EDA cluster, and commits it locally in Git.
- `pull(local_path, workboard_name)`: Re-fetches the latest remote server version of a tracked file (e.g. simulation logs, IMC coverage reports) and updates the local copy.
- `push(local_path, workboard_name, message)`: Uploads local modifications back to the mapped remote server path and records a Git commit with the provided commit message.
- `diff(local_path, workboard_name)`: Computes a unified diff between the local working copy and the remote server copy using SHA-256 and Git diffs.
- `status(workboard_name)`: Inspects all tracked files, reporting synchronization state (`SYNCHRONIZED`, `MODIFIED_LOCALLY`, `MODIFIED_REMOTELY`, `CONFLICT`).
- `history(local_path, workboard_name)`: Retrieves the local Git commit history for a tracked file or entire WorkBoard workspace.

---

## 2. Digital EDA Daemon Client SDK ([`eda_client.py`](../../src/clients/eda_client.py))

### HTTP REST Client Architecture
- Provides a clean Python SDK (`EDADaemonClient`) communicating with `daemon.py` on `http://127.0.0.1:8765`.
- Enables external automation scripts, regression runners, and autonomous subagents to interact with remote EDA clusters and WorkBoard storage without spinning up redundant SSH connections.
- Methods:
  - `health()`: Validates daemon liveness and retrieves process ID.
  - `workboard(action, local_path, remote_path, ...)`: Dispatches WorkBoard synchronization operations.
  - `remote_control(action, command, path, content, ...)`: Dispatches remote shell execution or file I/O operations.

---

## 3. Remote Session Core Client ([`ssh_client.py`](../../src/core/ssh_client.py))

- Persistent Paramiko SSH connection to Linux EDA servers (`eda-uni` or custom hosts).
- Auto-sources EDA environment scripts (e.g., `source /cadence/cshrc`) on every command execution.
- Features:
  - `execute_command(command, timeout)`: Runs digital tool suites (`irun`, `xrun`, `ncsim`, `imc`, `jg`, `vcs`, `hal`, `genus`, `innovus`).
  - `read_file(path, timeout)`: Reads remote files up to 10MB cleanly.
  - `write_file(path, content, timeout)`: Writes remote files atomically using SFTP/SCP.
  - `execute_interactive_stream(command, match_pattern)`: Provides interactive terminal streaming for long-running or interactive tools.
