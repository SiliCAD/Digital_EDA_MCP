---
name: digital-eda-mcp-context-router
description: Autonomous task-routing and context-loading directive for AI agents in Digital_EDA_MCP. Directs the agent to execute view_file on context/designer/README.md for digital design, UVM verification, formal proofs, simulation, and regressions, and context/coder/README.md for MCP codebase development before taking any action.
---

# SYSTEM_DIRECTIVE: MANDATORY PRE-TASK CONTEXT ROUTING

> **STRICT AGENT EXECUTION INSTRUCTION**: Before generating code, proposing terminal commands, or invoking any MCP tool in this repository, you MUST execute `view_file` on the target context specification mapped to your current task intent.

---

## 1. Task Classification & Context Mapping

```text
TASK INTENT CLASSIFICATION                  MANDATORY SPECIFICATION TO READ (view_file)
──────────────────────────────────────────  ──────────────────────────────────────────
[DIGITAL DESIGN / VERIFICATION / MCP TOOLS] ──> context/designer/README.md
• Writing / modifying Verilog/SystemVerilog RTL
• Generating UVM testbenches (uvm-architect)
• Running Cadence Incisive/Xcelium simulations
• Executing JasperGold formal property proofs
• Running regressions & merging IMC coverage
• Synchronizing files via WorkBoard
• Running Cadence HAL static linting

[CODEBASE DEV / BUG FIXING / GITHUB]       ──> context/coder/README.md
• Resolving GitHub issues & fixing bugs
• Implementing new Digital MCP tool features
• Modifying Python server/client backends
• Editing SSH, SCP, or WorkBoard sync logic
• Creating git branches, commits, & PRs
```

---

## 2. Track 1 Directives: Digital Design & Verification

**Trigger Intent:** User requests digital RTL design, UVM testbench authoring, simulation, formal verification, coverage closure, or WorkBoard synchronization.

### Pre-Execution Requirement:
Read the context specification file at this relative path before taking any action:
`context/designer/README.md`

### Core Invariants Enforced:
1. `TOOL_SCHEMA`: Use `remote_control` and `workboard` according to their defined schemas in `context/designer/mcp_tools_spec.md`.
2. `WORKBOARD_SYNC`: Synchronize RTL, testbenches, assertions, coverage reports, and logs between local workstations and the remote EDA cluster via `workboard`.
3. `DRIVER_RESET`: Never bypass UVM drivers by toggling `vif.cb.reset` in test sequences. The driver must manage reset phases via `apply_reset(cycles)`.
4. `LOCKSTEP_CHECKING`: Retirement checkers must verify Program Counter, Instruction Word, Opcode, Destination Register, Source Register, and Cycle Latency.
5. `FORMAL_PROOF`: Formal verification must prove 100% of safety properties with Infinite Bounds (unbounded) and check cover properties for vacuity.
6. `COVERAGE_CLOSURE`: Achieve 100% functional covergroup closure and 100% reachable code coverage with documented waivers for unreachable default clauses.
7. `MUTATION_TESTING`: Validate testbench defect detection against a 100% mutation kill rate with baseline verification.

---

## 3. Track 2 Directives: Codebase Dev, Issue Resolution & PRs

**Trigger Intent:** User requests fixing a bug, resolving a GitHub issue, modifying Python source code, or updating server logic.

### Pre-Execution Requirement:
Read the context specification file at this relative path before taking any action:
`context/coder/README.md`

### Core Invariants Enforced:
1. `BRANCH_NAMING`: Create feature branch: `<agent_name>/issue-<issue_number>-<description>`.
2. `AGENT_COMMITS`: Author commits with agent metadata: `git -c user.name="<AgentName>" -c user.email="<agent>@ai.local" commit -m "..."`.
3. `PR_CREATION`: Open PR via `gh pr create` with metadata header banner (`Resolved by Agent`, `agent_model`, `session_id`, `log_file`), root cause explanation, test proof, and `Fixes #<id>`.
4. `NO_AUTOMERGE`: NEVER push to `main` or merge PRs. Halt immediately after `gh pr create` and request human review.
