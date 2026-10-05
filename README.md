# Digital_EDA_MCP

**Model Context Protocol (MCP) Server for Digital IC Design, Formal Property Verification, and Production UVM Verification on Remote Linux EDA Clusters.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-Standard%20v1.0-orange.svg)](https://modelcontextprotocol.io/)
[![Organization](https://img.shields.io/badge/Organization-SiliCAD-blueviolet.svg)](https://github.com/SiliCAD)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview

`Digital_EDA_MCP` connects local AI coding assistants (Antigravity, Claude Code, Cursor, Windsurf) to remote Linux EDA computing clusters over persistent, secure SSH and SCP channels. Designed specifically for **Digital IC Design, SystemVerilog/UVM Verification, Formal Property Verification, and Static Analysis**, it eliminates context bloat and provides lean, purpose-built tools and directives for digital chip design engineers.

```
┌────────────────────────────────────────────────────────┐
│             Local AI Agent / Copilot                   │
│         (Antigravity, Claude Code, Cursor)             │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON-RPC (FastMCP / Stdio)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Digital_EDA_MCP                      │
├────────────────────┬───────────────────┬───────────────┤
│   remote_control   │     workboard     │  report_issue │
└─────────┬──────────┴─────────┬─────────┴───────┬───────┘
          │ Persistent SSH     │ Git + SCP       │ GitHub API
          ▼                    ▼                 ▼
┌──────────────────┐  ┌──────────────────┐  ┌────────────┐
│ Linux EDA Server │  │ Remote Workspace │  │   GitHub   │
│ (irun, xrun, jg, │  │ (~/Desktop/UVM/  │  │   Issues   │
│  hal, vcs, imc)  │  │   or design dir) │  │  Tracking  │
└──────────────────┘  └──────────────────┘  └────────────┘
```

---

## 2. Core Capabilities & Toolset

### 2.1 `remote_control`
Low-latency shell execution and atomic file I/O on the remote Linux EDA server over a persistent, managed SSH session.
- **`run_command`**: Runs digital tool suites (`irun`, `xrun`, `ncsim`, `imc`, `jg`, `hal`, `vcs`, `yosys`, `verilator`) with environment auto-sourcing (`source /cadence/cshrc`), timeout management, and stdout/stderr capture.
- **`read_file`**: Reads remote files (RTL, logs, testbenches, reports) up to 10MB cleanly.
- **`write_file`**: Atomically creates and updates remote files.

### 2.2 `workboard`
Git-backed local-remote workspace synchronization and version control engine.
- Prevents manual SCP file copying and keeps local and remote repositories in lockstep.
- Actions:
  - `initialize`: Creates a local WorkBoard workspace backed by a dedicated local Git repository.
  - `add`: Downloads remote RTL or testbench files via SCP and registers them for tracking.
  - `export`: Uploads local files to the remote cluster and registers Git tracking.
  - `pull`: Pulls the latest remote versions of tracked files (e.g., simulation logs, IMC coverage reports).
  - `push`: Uploads local edits to the remote cluster and automatically creates a local Git commit.
  - `diff`: Computes unified diffs between the local working copy and the remote server copy.
  - `status`: Summarizes tracking state (`SYNCHRONIZED`, `MODIFIED_LOCALLY`, `MODIFIED_REMOTELY`, `CONFLICT`).
  - `history`: Retrieves the local Git commit log for files or workspaces.

### 2.3 `report_issue`
Autonomous GitHub issue creation tool with full session context, agent model identity, logs, and automatic label normalization.

### 2.4 `uvm-architect` Skill & Synthesizer
Built-in production UVM architecture skill located in [`.agents/skills/uvm-architect/`](.agents/skills/uvm-architect/):
- Enforces the **12 Golden Tenets of Production UVM Testbenches** (clean driver reset routing, lockstep instruction-identity checks, dual-domain coverage sampling, STORE-at-reset commits).
- Includes [`uvm_generator.py`](.agents/skills/uvm-architect/scripts/uvm_generator.py) for automatically synthesizing complete, production-grade UVM environments from simple YAML/JSON specifications.

---

## 3. Repository Structure

```text
Digital_EDA_MCP/
├── server.py                   # Root entrypoint shim for MCP clients
├── daemon.py                   # Local FastAPI background daemon for HTTP automation
├── requirements.txt            # Python dependencies (FastMCP, Paramiko, FastAPI)
│
├── src/
│   ├── server.py               # FastMCP server definition & tool registration
│   ├── issue_reporter.py       # Autonomous GitHub issue reporter
│   │
│   ├── core/                   # Core Infrastructure Layer
│   │   ├── ssh_client.py       # Persistent CSH subshell, sentinels, interactive streams
│   │   └── scp_client.py       # OpenSSH SCP direct transfer engine
│   │
│   └── clients/                # Domain Tool Clients
│       ├── workboard_client.py # Git-backed local-remote workspace synchronizer
│       └── eda_client.py       # Digital EDA daemon client Python SDK
│
├── .agents/                    # Agent Customizations & Skills
│   ├── mcp_config.json         # MCP server configuration
│   └── skills/
│       ├── uvm-architect/      # Production UVM environment generator & verification tenets
│       └── eda-mcp-context-router/ # Pre-task context routing directive
│
├── context/                    # Operational Agent Specifications
│   ├── designer/               # Digital design & verification execution specifications
│   │   ├── README.md           # Designer fast-agent contract & routing
│   │   ├── digital_simulation_guide.md # Incisive/Xcelium, VCS & IMC coverage merge
│   │   ├── formal_verification_guide.md # JasperGold SVA & unbounded proofs
│   │   ├── uvm_architecture_guide.md   # Production UVM tenets & reference models
│   │   ├── static_lint_guide.md        # Cadence HAL static lint analysis
│   │   ├── workboard_sync_guide.md     # WorkBoard file synchronization guide
│   │   └── mcp_tools_spec.md           # Tool argument schemas & modes
│   └── coder/                  # Server codebase maintenance specifications
│
├── demo/                       # Verified Production Demos
│   └── or_Gate/                # Complete UVM verification suite (100% formal, 100% coverage, 100% mutation)
│
├── config/                     # Connection configurations (SSH, SCP)
└── tests/                      # Unit & integration test suites
```

---

## 4. Getting Started

### 4.1 Prerequisites
- Python 3.10+
- OpenSSH client installed (`ssh`, `scp`)

### 4.2 Installation
```bash
git clone https://github.com/SiliCAD/Digital_EDA_MCP.git
cd Digital_EDA_MCP
pip install -r requirements.txt
```

### 4.3 Configuration
Copy the configuration template and specify your remote EDA host and SSH config:
```bash
cp config/config.json.template config/config.json
```

Edit `config/config.json`:
```json
{
  "ssh_host": "eda-uni",
  "ssh_config_path": "~/.ssh/config",
  "env_setup_cmd": "source /cadence/cshrc"
}
```

### 4.4 Registering with MCP Clients
In your MCP settings (e.g. `mcp_config.json` for Antigravity, Claude Code, or Cursor):
```json
{
  "mcpServers": {
    "digital-eda-mcp": {
      "command": "python",
      "args": [
        "/path/to/Digital_EDA_MCP/server.py"
      ]
    }
  }
}
```

### 4.5 Running the Background Daemon (Optional)
To share remote sessions across external Python automation scripts or test harnesses:
```bash
python daemon.py
```
The daemon starts an HTTP REST gateway at `http://127.0.0.1:8765`.

---

## 5. Running Tests

Execute the unit test suite:
```bash
python -m unittest tests/test_workboard.py tests/test_issue_reporter.py
```

---

## 6. License & Contributing

- Distributed under the [MIT License](LICENSE).
- Contributions, issues, and feature requests welcome under the [SiliCAD](https://github.com/SiliCAD) organization.
