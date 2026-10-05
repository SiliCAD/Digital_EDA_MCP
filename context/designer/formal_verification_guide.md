# Formal Property Verification Guide (JasperGold)

This guide documents formal property verification methodology, SystemVerilog Assertions (SVA) authoring standards, and Cadence JasperGold execution patterns using `Digital_EDA_MCP`.

---

## 1. Cadence JasperGold Batch Execution

### 1.1 Command Pattern
```bash
rm -rf jgproject
jg -fpv -no_gui -allow_unsupported_OS -tcl formal/run.jg >& verification/formal/logs/jaspergold_formal.log
```
> **TCSH Shell Gotcha**: On tcsh, use `>&` rather than `> file 2>&1` to prevent `Ambiguous output redirect` errors.

### 1.2 Canonical JasperGold TCL Script (`run.jg`)
```tcl
# Clear and initialize formal environment
clear -all

# Analyze design files and assertion bindings
analyze -sv09 -f filelists/formal.f

# Elaborate top-level DUT with bound assertions
elaborate -top <top_module>

# Configure clock and reset
clock clk
reset -expression reset

# Set formal proof engine options
set_engine_mode {Hp Ht Tri B N}

# Prove all unbounded assertions and prove covers
prove -all

# Report formal results summary
report -summary
exit
```

---

## 2. SystemVerilog Assertions (SVA) Best Practices

### 2.1 External Binding Architecture
Do not embed verification assertions directly into production RTL. Bind assertion modules externally:
```systemverilog
bind <dut_module_name> <assertions_module_name> u_assertions (
    .clk(clk),
    .reset(reset),
    .state(state),
    .data(data)
);
```

### 2.2 Unbounded Safety Properties
Write properties with clean disable-on-reset conditions:
```systemverilog
property p_fsm_valid_transition;
    @(posedge clk) disable iff (reset)
    (state == FETCH) |=> (state == DECODE);
endproperty
assert_fsm_valid_transition: assert property (p_fsm_valid_transition);
```

### 2.3 Vacuity & Precondition Covers
Every formal property must have an accompanying cover property on its antecedent to mathematically verify that the precondition is reachable (non-vacuous proof):
```systemverilog
cover_fsm_fetch: cover property (@(posedge clk) disable iff (reset) (state == FETCH));
```
JasperGold will mark assertions as **proven (Infinite Bound)** and covers as **covered (Hit)**.
