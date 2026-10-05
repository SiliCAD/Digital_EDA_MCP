# WORKBOARD_SYNC_SPEC

## 1. Local-Remote Workspace Mapping
- **Local WorkBoard Root**: `./workboard/<workboard_name>/`
- **Registry File**: `./workboard/<workboard_name>/.workboard.json`
- **Sync Baseline**: `last_sync_commit` (SHA of local Git commit at last synchronized state $C_{\text{sync}}$)

`local_path` is relative to the selected WorkBoard root, not an arbitrary workspace path. To create a new simulation deck, first initialize/select a board, then create the file at `./workboard/<workboard_name>/<local_path>` before calling `export`.

### Local File Authoring & Export Protocol
To synchronize a local RTL or testbench file into `./workboard/<name>/<subpath>`:
- Use `write_to_file` WITHOUT `ArtifactMetadata` (ArtifactMetadata is strictly for artifact directory files; passing it for workspace files causes validation errors).
- Export: `workboard(action="export", workboard_name="<name>", local_path="rtl/alu.v", remote_path="~/Desktop/digital/rtl/alu.v")`.

Example lifecycle:

```text
workboard(action="initialize", workboard_name="alu_verification")
# write ./workboard/alu_verification/rtl/alu.v
workboard(action="export", workboard_name="alu_verification",
          local_path="rtl/alu.v", remote_path="~/Desktop/digital/rtl/alu.v")
```

When more than one WorkBoard exists, pass `workboard_name` on every operation unless the current server session has already selected one. That selection is session-local; do not assume it persists across MCP server restarts.

---

## 2. Action State Matrix

| Action | Target Input | Local Git Effect | Sync Baseline ($C_{\text{sync}}$) |
| :--- | :--- | :--- | :--- |
| `initialize` | `workboard_name` | `git init`, write `.gitignore` | Created |
| `add` | `remote_path`, `local_path` | Download via SCP, `git commit` | Updated to `HEAD` |
| `pull` | `local_path` | Re-download via SCP, `git commit` | Advanced to `HEAD` |
| `push` | `local_path` | Upload via SCP, `git commit` | Advanced to `HEAD` |
| `diff` | `local_path` | Compare local vs remote bytes | Auto-advanced if 100% match |
| `status` | None | Read-only state report | Read-only |
| `history` | `local_path` | `git log -n 10` execution | Read-only |

---

## 3. Native Git Shell Navigation Commands
Agent can execute terminal commands inside `./workboard/<name>/`:
- Commit log: `git log -n 10 --oneline -- <local_path>`
- Baseline state view: `git show <commit_sha>:<local_path>`
- Revert file to baseline: `git checkout <commit_sha> -- <local_path>`
- Diff baselines: `git diff <commit_sha_1> <commit_sha_2> -- <local_path>`

---

## 4. Local Tooling & Verification Scripting Authorization
- Agents may use local tools to author SystemVerilog assertions, generate randomized stimulus, parse regression logs, build coverage metrics, and construct UVM testbenches. RTL changes must be rigorously validated against formal and simulation regression baselines before deployment.

---

## 5. File Encoding & Non-UTF8 Character Handling
- EDA tool outputs (such as simulator compile logs, IMC coverage reports, or timing database dumps) occasionally contain non-UTF-8 characters.
- All WorkBoard diff, read, and pull operations automatically decode files using UTF-8 with fallback replacement (`errors="replace"`) to prevent decoder crashes (`UnicodeDecodeError`).
- When authoring local RTL, filelists, or SVA properties, ensure standard UTF-8/ASCII formatting.
