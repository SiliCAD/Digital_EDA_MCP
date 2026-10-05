# Production UVM Architecture & Verification Methodology Guide

This guide establishes the architectural standards and verification tenets for production-grade UVM environments built and validated using `Digital_EDA_MCP`.

---

## 1. Golden Tenets of Production UVM Testbenches

1. **Clean Driver Reset Routing**: Never bypass the UVM driver by directly toggling `vif.cb.reset` in test sequences. The driver must own reset sequencing through `apply_reset(cycles)`, `assert_reset()`, and `deassert_reset()`.
2. **Strict Instruction-Identity Lockstep Checking**:
   Retirement checkers in scoreboards must verify:
   - Program Counter (`item.pc == exp_pc`)
   - Instruction Word (`item.instruction == exp_instr`)
   - Opcode (`item.opcode == exp_op`)
   - Destination Register (`item.rd == exp_rd`)
   - Source Register (`item.rs == exp_rs`)
   - Cycle Latency (`item.latency == exp_latency`)
3. **Dual-Domain Coverage Architecture**:
   To prevent clocking block race conditions and ensure 100% bin hits:
   - Sample cycle-level pipeline states (`cpu_fsm_cov`) at every active clock tick.
   - Sample architectural ISA instructions and register crosses (`cpu_isa_cov`) only upon instruction retirement.
4. **STORE-at-Reset Commit Handling**:
   If an asynchronous or synchronous reset asserts during the final WRITEBACK stage of a memory STORE operation, ensure the scoreboard updates the golden reference model before flushing state to prevent false memory divergence errors.
5. **Deterministic Watchdog Protection**:
   All drivers and monitors must incorporate watchdog timers with seed-aware timeout reporting:
   ```systemverilog
   $value$plusargs("SEED=%d", sim_seed);
   ```

---

## 2. Component Hierarchy Map

```
                  ┌──────────────────────────────────────────┐
                  │                 uvm_test                 │
                  └────────────────────┬─────────────────────┘
                                       │
                  ┌────────────────────▼─────────────────────┐
                  │                 uvm_env                  │
                  └─────────┬───────────────┬──────────────┬─┘
                            │               │              │
           ┌────────────────▼───┐   ┌───────▼──────┐  ┌────▼────────┐
           │     cpu_agent      │   │  scoreboard  │  │  coverage   │
           └──────┬───────┬─────┘   └──────────────┘  └─────────────┘
                  │       │
       ┌──────────▼──┐ ┌──▼──────────┐
       │ cpu_driver  │ │ cpu_monitor │
       └──────────┬──┘ └──┬──────────┘
                  │       │
                  ▼       ▼
          ┌───────────────────────┐
          │  virtual interface    │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │        DUT RTL        │
          └───────────────────────┘
```

---

## 3. Reference Model Architecture

- Maintain both a **step-level reference model** (advancing one retired instruction at a time) and a **full-program reference model** (executing to completion upon `HALT`).
- Compare register file contents (`R0`..`R3`) and memory words on every retired instruction and at end-of-test.
