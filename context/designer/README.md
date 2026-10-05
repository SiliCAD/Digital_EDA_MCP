# Digital_EDA_MCP Designer & Verification Context

This document is the operational specification and fast-agent execution contract for AI agents performing digital IC design, RTL synthesis, formal property verification, and production UVM verification using `Digital_EDA_MCP`.

---

## 1. Fast-Agent Execution Contract

Apply these defaults before consulting detailed subsystem guides:

1. **Live Schema Authority**: Read the live MCP tool schema (`remote_control`, `workboard`, `report_issue`); never invent parameters or tool actions.
2. **WorkBoard File Synchronization**: Always use `workboard` to pull and push RTL modules, testbenches, assertions, coverage reports, and simulation scripts between the local workstation and the remote EDA cluster.
3. **Remote Execution Safety**: Execute digital tools (`irun`, `xrun`, `ncsim`, `imc`, `jg`, `hal`, `pytest`) using `remote_control(action="run_command")`. Ensure environment setup (`source /cadence/cshrc`) is active.
4. **Clean Driver Reset Routing**: Never bypass the UVM driver by toggling `vif.cb.reset` in test sequences. The driver must strictly manage reset phases via `apply_reset(cycles)`.
5. **Instruction Lockstep Verification**: Retirement checkers must verify Program Counter, Instruction Word, Opcode, Destination Register, Source Register, and Cycle Latency.
6. **STORE-at-Reset Safety**: Handle reset interruptions during the WRITEBACK stage of a memory STORE by updating reference models to prevent false memory divergence.
7. **Coverage Closure**: Require 100% functional covergroup closure and 100% reachable structural code coverage before signoff. All unreachable defensive default clauses must be formally waived with JasperGold unbounded proofs.
8. **Formal Proofs**: Formal verification must prove 100% of safety properties with Infinite Bounds (unbounded proofs) and verify all cover properties to guarantee non-vacuous assertions.
9. **Mutation Testing**: Validate verification testbench efficacy against 100% mutation kill rates with pristine baseline verification and zero false compiler positives.
10. **Evidence Integrity**: Never hardcode coverage percentages or Git commit hashes in CSV results. Extract metrics dynamically from Cadence IMC and `git rev-parse --short HEAD`.

---

## 2. Context Routing Table

Read the smallest relevant guide before executing your task:

| Intent | Read First |
| :--- | :--- |
| Compile, simulate, or run UVM regressions | [`digital_simulation_guide.md`](digital_simulation_guide.md) |
| Merge code, FSM, and functional coverage in IMC | [`digital_simulation_guide.md`](digital_simulation_guide.md) |
| Author SVA assertions or run JasperGold formal proofs | [`formal_verification_guide.md`](formal_verification_guide.md) |
| Architect UVM components, scoreboards, and agents | [`uvm_architecture_guide.md`](uvm_architecture_guide.md) |
| Run Cadence HAL static linting or design rule checks | [`static_lint_guide.md`](static_lint_guide.md) |
| Transfer or synchronize files with remote EDA cluster | [`workboard_sync_guide.md`](workboard_sync_guide.md) |
| Report a bug, discrepancy, or feature request | [`issue_reporting_guide.md`](issue_reporting_guide.md) |
| Determine tool arguments, action modes, or defaults | [`mcp_tools_spec.md`](mcp_tools_spec.md) |

---

## 3. Guide Index

- [`digital_simulation_guide.md`](digital_simulation_guide.md): Invocations for `irun`, `xrun`, `ncsim`, and batch Cadence IMC coverage merging.
- [`formal_verification_guide.md`](formal_verification_guide.md): JasperGold formal property verification, unbounded proofs, and vacuity covers.
- [`uvm_architecture_guide.md`](uvm_architecture_guide.md): Production UVM architecture, reference models, and lockstep checking standards.
- [`static_lint_guide.md`](static_lint_guide.md): Cadence HAL static lint analysis, rule categories, and waiver standards.
- [`workboard_sync_guide.md`](workboard_sync_guide.md): Git-backed local-remote workspace synchronization semantics.
- [`mcp_tools_spec.md`](mcp_tools_spec.md): Exact parameters, action modes, and return schemas for all tools.
- [`issue_reporting_guide.md`](issue_reporting_guide.md): GitHub issue creation and session metadata tagging.
