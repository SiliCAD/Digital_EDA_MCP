# CODER_CONTEXT_SPEC (Python Digital MCP Server Implementation)

## Component Map & File References

| Component | Source File | Class / Function | Description |
| :--- | :--- | :--- | :--- |
| **MCP Entrypoint** | [`server.py`](../../src/server.py) | `FastMCP("Digital_EDA_MCP")` | Registers 3 core MCP tools (`remote_control`, `workboard`, `report_issue`), initializes persistent SSH sessions, configures logger (`logs/digital_eda_mcp_*.log`). |
| **SSH Transport** | [`ssh_client.py`](../../src/core/ssh_client.py) | `RemoteSession` | Manages persistent `csh` subshell over SSH, sentinel execution (`_read_until_sentinel`), environment sourcing (`source /cadence/cshrc`), and interactive stream reading (`execute_interactive_stream`). |
| **SCP Transport** | [`scp_client.py`](../../src/core/scp_client.py) | `SCPClient` | Executes OpenSSH `scp -O` for direct binary/folder transfer without shell escaping overhead. |
| **WorkBoard Engine** | [`workboard_client.py`](../../src/clients/workboard_client.py) | `WorkBoardClient` | Manages `./workboard/<name>/` local Git repositories, `.workboard.json` manifests, SHA-256 checksums, and unified diffs. |
| **Daemon SDK** | [`eda_client.py`](../../src/clients/eda_client.py) | `EDADaemonClient` | HTTP REST client allowing external automation scripts and subagents to invoke remote execution and WorkBoard sync. |
| **Issue Reporter** | [`issue_reporter.py`](../../src/issue_reporter.py) | `IssueReporter` | Autonomous GitHub issue reporting with smart label normalization, random-color creation, and fallback recovery. |

---

## Repository Architecture (`src/` Modular Layout)

```text
Digital_EDA_MCP/
├── server.py                   # Backward-compatible entrypoint shim for MCP runners
├── daemon.py                   # Local FastAPI background daemon for HTTP automation
├── src/
│   ├── __init__.py             # Exports IssueReporter
│   ├── server.py               # FastMCP server definition & tool registration
│   ├── issue_reporter.py       # Autonomous GitHub issue & smart label reporter
│   │
│   ├── core/                   # Infrastructure & Transport Layer
│   │   ├── __init__.py         # Exports RemoteSession, SCPClient
│   │   ├── ssh_client.py       # Persistent CSH subshell, sentinels, interactive streams
│   │   └── scp_client.py       # OpenSSH SCP direct transfer engine
│   │
│   └── clients/                # High-Level Domain Tool Clients
│       ├── __init__.py         # Exports WorkBoardClient, EDADaemonClient
│       ├── workboard_client.py # Local-remote Git workspace synchronizer
│       └── eda_client.py       # Digital EDA daemon client SDK
│
├── .agents/skills/             # Specialized Agent Skills
│   ├── uvm-architect/          # Production UVM environment generator & verification tenets
│   └── eda-mcp-context-router/ # Autonomous context routing directive
├── demo/                       # Verified Production Demos (e.g. or_Gate UVM environment)
├── tests/                      # Unit and integration test suites
├── config/                     # Remote SSH / tool JSON configs
└── context/                    # Dual-track agent directives (designer & coder)
```

---

## Agent Operational Invariants

1. **AGENT_IDENTITY_BRANCHING**: Every issue fix or enhancement MUST be created on a feature branch named `<agent_name>/issue-<issue_number>-<description>` (e.g., `antigravity/issue-1-uvm-generator-enhancement`).
2. **AGENT_IDENTITY_COMMITS**: All commits MUST explicitly declare custom agent author metadata: `git -c user.name="<AgentName>" -c user.email="<agent>@ai.local" commit -m "..."`.
3. **PULL_REQUEST_EXPLANATION & SCOPING**: Pull Requests MUST be created via `gh pr create` with Metadata Header Banner (`Resolved by Agent`, `agent_model`, `session_id`, `log_file`), PR label auto-creation, attached `--label "<agent_name>"`, root cause explanation, fix details, test verification, and issue linkage (`Fixes #<issue_number>`).
   - **Avoid Low-Scoped PRs**: PRs must **not** be artificially low-scoped. A PR can and should contain a complete, coherent set of related fixes, enhancements, tests, and accompanying documentation together if they are related to the same functional milestone or issue set.
4. **STRICT_NO_AUTOMERGE_POLICY**: Coder Agents MUST NEVER merge PRs or push directly to `main`. Stop execution immediately after `gh pr create` and request Human Code Review.
5. **HUMAN_REVIEW_GATE**: Do not force-merge or bypass code reviews.
