# Digital_EDA_MCP Tools Specification

This document defines the functional interface, arguments, operational semantics, and error handling for all tools exposed by the `Digital_EDA_MCP` server.

---

## 1. `remote_control`

Execute shell commands and perform remote file operations on the remote Linux EDA server over an isolated, persistent SSH session.

### Schema
```json
{
  "name": "remote_control",
  "description": "Execute shell commands and perform file operations on the remote EDA server.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["run_command", "read_file", "write_file"],
        "description": "The operation to perform"
      },
      "command": {
        "type": "string",
        "description": "Shell command to execute when action='run_command'"
      },
      "path": {
        "type": "string",
        "description": "Remote file path when action='read_file' or action='write_file'"
      },
      "content": {
        "type": "string",
        "description": "Text content to write when action='write_file'"
      },
      "timeout": {
        "type": "number",
        "default": 60.0,
        "description": "Maximum execution timeout in seconds"
      }
    },
    "required": ["action"]
  }
}
```

### Action Modes
- **`run_command`**: Runs a shell command in the remote CSH/BASH environment where EDA environment scripts (e.g. `/cadence/cshrc`) are sourced. Captures exit code, stdout, and stderr.
  - Typical use cases: Running `irun`, `xrun`, `ncsim`, `imc`, `jg`, `hal`, `pytest`, regression scripts, mutation frameworks.
- **`read_file`**: Reads text content from a remote server file path (supports `~` expansion and absolute paths).
- **`write_file`**: Writes text content to a remote server file path atomically.

---

## 2. `workboard`

Git-backed workspace synchronization and file transfer engine between local developer workspace and the remote EDA cluster.

### Schema
```json
{
  "name": "workboard",
  "description": "Git-backed WorkBoard tool for local-remote file synchronization and version control.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["initialize", "add", "export", "pull", "push", "diff", "status", "history"],
        "description": "The synchronization action to perform"
      },
      "workboard_name": {
        "type": "string",
        "default": "default",
        "description": "Name of the target WorkBoard workspace"
      },
      "remote_path": {
        "type": "string",
        "description": "Target file or directory path on the remote server"
      },
      "local_path": {
        "type": "string",
        "description": "Target relative file or directory path within the WorkBoard"
      },
      "message": {
        "type": "string",
        "default": "Agent sync",
        "description": "Git commit message for push and export actions"
      },
      "overwrite": {
        "type": "boolean",
        "default": false,
        "description": "Allow overwriting existing remote files during export"
      },
      "timeout": {
        "type": "number",
        "default": 60.0,
        "description": "Transfer timeout in seconds"
      }
    },
    "required": ["action"]
  }
}
```

### Action Modes
- **`initialize`**: Initializes a new WorkBoard workspace with a dedicated local Git repo and `.workboard.json` tracking registry.
- **`add`**: Downloads a remote file/folder via SCP and registers it under WorkBoard tracking.
- **`export`**: Copies a local file/folder into the WorkBoard, uploads it via SCP to the remote server, and commits it locally.
- **`pull`**: Refreshes the local copy of a tracked file with the latest version from the remote server.
- **`push`**: Uploads local edits of a tracked file back to the remote server and creates a Git commit.
- **`diff`**: Shows a unified diff between the local WorkBoard file and the remote server copy.
- **`status`**: Summarizes the tracking and synchronization state of all registered files in the WorkBoard.
- **`history`**: Shows the local Git commit log for a file or workspace.

---

## 3. `report_issue`

Autonomous GitHub issue reporter with full agent session tracking, automatic label management, and fallback recovery.

### Schema
```json
{
  "name": "report_issue",
  "description": "Report an issue, bug, or feature request directly to GitHub.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": { "type": "string", "description": "Issue title" },
      "body": { "type": "string", "description": "Issue description in Markdown" },
      "label": { "type": "string", "default": "bug", "description": "Issue label" },
      "agent_model": { "type": "string", "description": "Model identifier of the agent" },
      "session_id": { "type": "string", "default": "unknown", "description": "Agent session ID" }
    },
    "required": ["title"]
  }
}
```
