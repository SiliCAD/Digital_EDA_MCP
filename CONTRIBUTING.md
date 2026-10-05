# Contributing to Digital_EDA_MCP

Thank you for contributing to **Digital_EDA_MCP**! This repository powers an autonomous digital EDA and verification pipeline enabling AI agents to design digital circuits, execute simulations (Cadence Xcelium/NCSim, Synopsys VCS), perform formal verification (JasperGold), enforce static lint (Cadence HAL), architect UVM testbenches, synchronize files via WorkBoard, and report/fix tool issues.

This guide outlines the standard procedures for both **Digital Design & Verification Consumer Agents (Agent A)** and **Coder / Maintainer Agents (Agent B)**, as well as human contributors.

---

## 📋 Table of Contents

1. [Dual-Agent Architecture](#1-dual-agent-architecture)
2. [Reporting Bugs & Feature Requests (Designer Guidelines)](#2-reporting-bugs--feature-requests-designer-guidelines)
3. [Development Environment Setup](#3-development-environment-setup)
4. [Code Contribution Workflow (Coder Guidelines)](#4-code-contribution-workflow-coder-guidelines)
5. [Documentation & Context References](#5-documentation--context-references)

---

## 1. Dual-Agent Architecture

```mermaid
flowchart TD
    A["Digital Design / Verification Agent (Agent A)"] -->|"report_issue(title, body, label)"| B["GitHub Issue Created"]
    B --> C["Coder / Maintainer Agent (Agent B)"]
    C -->|"1. git checkout -b agent/issue-<id>-desc"| D["Dedicated Agent Branch"]
    D -->|"2. Implement Fix & Run Tests"| E["Verified Local Changes"]
    E -->|"3. git -c user.name=Agent commit"| F["Author-Tagged Commit"]
    F -->|"4. gh pr create (Fixes #<id>)"| G["Pull Request Opened"]
    G -->|"5. STOP & WAIT"| H["👨‍💻 Human Review Gate"]
    H -->|"Human Review & Merge"| I["Merged to Main Branch"]
```

---

## 2. Reporting Bugs & Feature Requests (Designer Guidelines)

Digital Design & Verification Agents (Agent A) can report tool errors, tracebacks, or request new tool capabilities directly via the `report_issue` MCP tool.

### MCP Tool Interface
```typescript
report_issue({
  title: string,        // Concise summary of the bug or feature request
  body?: string,        // Freeform Markdown content (see suggestions below)
  label?: string,       // Default: "bug" (e.g. "enhancement", "feature-request")
  agent_model?: string, // Model identifier (e.g. "gemini-3.6-flash", "claude-3-5-sonnet")
  session_id?: string   // Current conversation turn ID
})
```

### Suggested Issue Body Guidelines

> 💡 **Flexibility Note**: These guidelines are helpful suggestions, NOT rigid rules. Agents have full freedom to format Markdown as appropriate.

#### A. Reporting Bugs
- **Tool Name**: Specify the tool involved (`remote_control`, `workboard`, `report_issue`).
- **Encounter Context**: Explain the digital design/verification task being performed when the bug occurred (e.g. UVM simulation, formal analysis, linting).
- **Steps to Reproduce**: Provide command sequences, file paths, or minimal reproducible snippets.
- **Observed vs. Expected**: Share raw error tracebacks and what was expected to happen.

#### B. Feature Requests / Enhancements
- **What to Add**: Clearly state the proposed tool extension or parameter.
- **Why it is Needed**: Explain the bottleneck or friction point being solved.
- **How to Enhance**: Show the ideal tool signature, proposed JSON schema, or code example.
- **Proposed Implementation Milestones**: Outline logical step-by-step milestones (Phase 1, Phase 2, Phase 3) to guide the Coder Agent in implementing the feature.

*(For detailed examples, see [`context/designer/issue_reporting_guide.md`](context/designer/issue_reporting_guide.md)).*

---

## 3. Development Environment Setup

### Prerequisites
- Python 3.10+
- OpenSSH client (`scp`, `ssh`)
- GitHub CLI (`gh`) logged in (`gh auth login`)

### Setup Steps

1. **Clone Repository**:
   ```bash
   git clone https://github.com/SiliCAD/Digital_EDA_MCP.git
   cd Digital_EDA_MCP
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Tool Credentials**:
   Copy template in `config/` to create tool configuration file:
   ```bash
   cp config/config_remote_control.json.template config/config_remote_control.json
   ```

---

## 4. Code Contribution Workflow (Coder Guidelines)

Maintainer / Coder Agents (Agent B) and human contributors resolving GitHub issues or implementing features MUST adhere to the following workflow:

### 1. Dedicated Agent Branching
Create a new feature branch named after the agent and issue ID:
```bash
git checkout -b <agent_name>/issue-<issue_number>-<short-description>
```
*Examples*: `antigravity/issue-42-xrun-parser-fix`, `codex/feature-jg-runner`

### 2. Custom Author Identity Commits
Commit changes with explicit author metadata corresponding to the active agent:
```bash
git -c user.name="<AgentName>" -c user.email="<agent_name>@ai.local" commit -m "<type>: <concise description>"
```
*Types*: `fix:`, `feat:`, `refactor:`, `test:`, `docs:`

### 3. Unit Test Verification
Run the unit test suite to ensure all tests pass cleanly before pushing:
```bash
python3 -m unittest discover tests
```

### 4. Pull Request Creation, Label Auto-Creation & Issue Linking
Push the branch, check/create the GitHub agent label (`gh label create`), and open a Pull Request via GitHub CLI:
```bash
git push origin <agent_name>/issue-<issue_number>-<short-description>

# Check & create agent label on GitHub if missing
gh label list | grep -i "<agent_name>" || gh label create "<agent_name>" --color "0E8A16"

gh pr create \
  --title "fix(component): concise fix summary" \
  --label "<type>" \
  --label "<agent_name>" \
  --body "> **Resolved by Agent:** <agent_name> (\`<agent_model>\`) (Coder / Maintainer)
> **Session ID:** \`<session_id>\`
> **MCP Log File:** \`temp/eda_mcp_YYYYMMDD_HHMMSS_<PID>.log\`
---

## Summary
Description of fix...

## Technical Details
Root cause and solution explanation...

## Verification
- Ran unit tests (23/23 passing)

Fixes #<issue_number>" \
  --base main
```

### 5. 🛑 Strict Human Review Gate (NO AUTO-MERGING)
- **STRICT RULE**: Coder agents **MUST NEVER** execute `git merge`, `gh pr merge`, or merge code into `main`.
- Immediately after opening the PR (`gh pr create`), stop execution and notify the human maintainer.
- Only human maintainers are authorized to review and merge PRs into `main`.

*(For detailed Coder guidelines, see [`context/coder/issue_resolution_workflow.md`](context/coder/issue_resolution_workflow.md)).*

---

## 5. Documentation & Context References

- **Designer Agent Context**: [`context/designer/README.md`](context/designer/README.md)
  - Tool Specifications: [`context/designer/mcp_tools_spec.md`](context/designer/mcp_tools_spec.md)
  - Digital Simulation Guide: [`context/designer/digital_simulation_guide.md`](context/designer/digital_simulation_guide.md)
  - Formal Verification Guide: [`context/designer/formal_verification_guide.md`](context/designer/formal_verification_guide.md)
  - UVM Architecture Guide: [`context/designer/uvm_architecture_guide.md`](context/designer/uvm_architecture_guide.md)
  - Static Lint Guide: [`context/designer/static_lint_guide.md`](context/designer/static_lint_guide.md)
  - WorkBoard Sync Guide: [`context/designer/workboard_sync_guide.md`](context/designer/workboard_sync_guide.md)
  - Issue Reporting Guide: [`context/designer/issue_reporting_guide.md`](context/designer/issue_reporting_guide.md)
- **Coder Agent Context**: [`context/coder/README.md`](context/coder/README.md)
  - Issue Resolution Workflow: [`context/coder/issue_resolution_workflow.md`](context/coder/issue_resolution_workflow.md)
  - Server & MCP Architecture: [`context/coder/server_and_mcp.md`](context/coder/server_and_mcp.md)
  - Transport Layer (SSH/SCP): [`context/coder/transport_layer.md`](context/coder/transport_layer.md)
  - EDA Tool Clients: [`context/coder/eda_tool_clients.md`](context/coder/eda_tool_clients.md)
