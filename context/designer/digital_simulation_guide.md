# Digital Simulation & Regression Flow Guide

This guide details best practices and standardized command patterns for compiling, elaborating, simulating, and gathering coverage for digital SystemVerilog / UVM designs using `Digital_EDA_MCP`.

---

## 1. Cadence Incisive & Xcelium Simulation Flow

### 1.1 Canonical `irun` / `xrun` Invocation
When compiling and executing UVM testbenches on Linux EDA clusters:
```bash
irun -64bit \
     -uvm \
     -uvmhome CDNS-1.1d \
     -sv \
     -access +rw \
     -timescale 1ns/1ps \
     -coverage all \
     -covworkdir cov_work \
     -covoverwrite \
     -covtest <test_run_id> \
     -f filelists/filelist.f \
     +UVM_TESTNAME=<test_name> \
     -svseed <seed> \
     +SEED=<seed> \
     +UVM_VERBOSITY=UVM_LOW \
     -input scripts/ncsim_run.tcl \
     -l <log_path>
```

### 1.2 Essential Tool Flags:
- `-64bit`: Run in 64-bit architecture to prevent out-of-memory errors on large simulations.
- `-uvm -uvmhome CDNS-1.1d`: Load standard Cadence UVM package and macros.
- `-sv -access +rw`: Enable full SystemVerilog IEEE-1800 syntax and read/write visibility for waveforms and assertions.
- `-timescale 1ns/1ps`: Set explicit simulation time unit and precision.
- `-coverage all`: Enable Statement (block), Branch, Condition (expression), FSM, Toggle, and Functional covergroup instrumentation.
- `-covoverwrite`: Overwrite existing coverage databases when re-running test iterations to prevent `ncsim: *F,C58EXS` failures.
- `-input scripts/ncsim_run.tcl`: Supply headless simulation run script (`run; exit;`).

---

## 2. Cadence IMC Cumulative Coverage Merge Flow

### 2.1 Batch Mode TCL Command Script
To headlessly merge all regression test runs and dump unified coverage reports:
```tcl
# merge_coverage.tcl
merge * -initial_model union_all -out final_merged -overwrite
load cov_work/scope/final_merged
report -summary -out verification/coverage/final/final_summary.rpt
report -detail -metrics functional -both -out verification/coverage/final/final_functional.rpt
report -detail -metrics code -both -out verification/coverage/final/final_code.rpt
report -detail -metrics fsm -both -out verification/coverage/final/final_fsm.rpt
exit
```

### 2.2 Executing IMC Merge
```bash
imc -exec merge_coverage.tcl
```
> **Cadence Gotcha**: `imc -batch` and `imc -exec` are mutually exclusive in Cadence IMC 15.20. Always use `imc -exec <file.tcl>` for headless script-driven report generation.

---

## 3. Dynamic Regression Runner Principles

1. **Per-Test Code Coverage Extraction**: Never hardcode code coverage percentages in regression matrices. Extract genuine percentages dynamically from IMC per test run:
   ```python
   tmp_tcl = f"/tmp/cmd_{test_id}.tcl"
   with open(tmp_tcl, "w") as f:
       f.write(f"report -summary -out /tmp/cov_{test_id}.rpt\nexit\n")
   subprocess.run(f"imc -load cov_work/scope/{test_id} -exec {tmp_tcl}", shell=True)
   ```
2. **Dynamic Git Hash Retrieval**: Always query the real Git commit hash via `git rev-parse --short HEAD` rather than relying on stale fallback strings.
3. **Log & CSV Fidelity**: Ensure functional coverage, code coverage, runtime, and assertion outcomes recorded in CSV files strictly match the raw simulation logs.
