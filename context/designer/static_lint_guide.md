# Static Lint & Design Rule Checking Guide

This guide describes static analysis, linting, and design rule checking flows using Cadence HAL and industry static lint engines via `Digital_EDA_MCP`.

---

## 1. Cadence HAL Static Linting Flow

### 1.1 Invocations
```bash
hal -64bit \
    -sv \
    -timescale 1ns/1ps \
    -f filelists/filelist.f \
    -log verification/lint/hal.log
```

### 1.2 Key Rule Checks:
- **LATCH_INFER**: Accidental latch inference in combinational `always @(*)` blocks due to missing `default` or incomplete `if/else` paths.
- **MULTI_DRIVE**: Signals driven by multiple concurrent drivers or continuous assignments.
- **UNDEF_NET**: Implicit undeclared wires or missing port connections.
- **WIDTH_MISMATCH**: Vector bit-width truncation or zero-extension warnings in expressions and port bindings.
- **ASYNC_RESET**: Glitch hazards and improper polarity on asynchronous reset trees.

---

## 2. Static Lint Waivers Protocol

When static lint rules flag benign RTL structures (e.g., intentional bit truncations, unused upper address bits, or synthesis-safe default branches):
1. **Rule Classification**: Document the exact tool rule ID (e.g. `HAL-W-01`, `STARC-2.1.1`).
2. **File & Line Citation**: Record the exact RTL filename and source code line numbers.
3. **Architectural Justification**: Explain why the flagged structure is safe and mathematically or logically bounded.
4. **Permanent Logging**: Preserve raw lint logs (`verification/lint/hal.log`) in the repository for audit reproducibility.
