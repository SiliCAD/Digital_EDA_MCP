# DIGITAL_SERVER_AND_MCP_SPEC

## 1. Instance & Logging Setup ([`src/server.py`](../../src/server.py))
- **FastMCP Server**: `mcp = FastMCP("Digital_EDA_MCP")`
- **Log Location**: `logs/digital_eda_mcp_<session_timestamp>_<pid>.log`
- **Log Handlers**:
  - `logging.FileHandler(log_filepath, encoding="utf-8")`
  - `logging.StreamHandler(sys.stderr)` (preserves stdout JSON-RPC stdio protocol)

---

## 2. Remote Session & Client Allocations

[`src/server.py`](../../src/server.py) instantiates dedicated backend managers:

```python
remote_control_config = os.path.join(config_dir, "config_remote_control.json")
remote_session = RemoteSession(config_path=remote_control_config)
workboard_client = WorkBoardClient(base_workboard_dir=os.path.join(base_dir, "workboard"))
```

---

## 3. Tool Dispatch Table

| Tool Name | Action Argument | Target Method Invocation | Description |
| :--- | :--- | :--- | :--- |
| `remote_control` | `"run_command"` | `remote_session.execute_command(command, timeout)` | Execute shell command on remote EDA cluster |
| `remote_control` | `"read_file"` | `remote_session.read_file(path, timeout)` | Read text file from remote server |
| `remote_control` | `"write_file"` | `remote_session.write_file(path, content, timeout)` | Write text content to remote server file |
| `workboard` | `"initialize"` | `workboard_client.initialize(workboard_name)` | Initialize local Git-backed WorkBoard workspace |
| `workboard` | `"add"` | `workboard_client.add(remote_path, local_path, workboard_name, timeout)` | Fetch remote file into local WorkBoard |
| `workboard` | `"export"` | `workboard_client.export(local_path, remote_path, workboard_name, message, timeout)` | Upload local file to remote and track in Git |
| `workboard` | `"pull"` | `workboard_client.pull(local_path, workboard_name, timeout)` | Pull remote updates for tracked file |
| `workboard` | `"push"` | `workboard_client.push(local_path, workboard_name, message, timeout)` | Push local modifications to remote server |
| `workboard` | `"diff"` | `workboard_client.diff(local_path, workboard_name)` | Display diff between local and remote copies |
| `workboard` | `"status"` | `workboard_client.status(workboard_name)` | List tracking status of all WorkBoard files |
| `workboard` | `"history"` | `workboard_client.history(local_path, workboard_name)` | Display Git commit history for workspace |
| `report_issue` | `(title, body, ...)`| `IssueReporter.create_issue(...)` | Create structured GitHub issue with session context |

---

## 4. Background Daemon Architecture ([`daemon.py`](../../daemon.py) & [`eda_client.py`](../../src/clients/eda_client.py))

- FastMCP stdio interface is supplemented by a FastAPI HTTP daemon on `http://127.0.0.1:8765`.
- Endpoints:
  - `GET /health`
  - `POST /remote_control`
  - `POST /workboard`
- External test harnesses, regression managers, and IDE extensions interact through `EDADaemonClient`.
