# GitHub Issue Reporting for Designer Agents

`report_issue` creates a persistent external GitHub issue. Use it only when the user explicitly asks for a report or the project has explicitly authorized autonomous reporting. A failed tool call does not itself authorize issue creation.

## Before creating an issue

1. Preserve the returned tool output, relevant configuration, and a minimal reproduction.
2. Search open and recently closed issues for the tool name, action, error signature, and affected context file. Comment on or reference a matching issue instead of duplicating it when project policy allows comments.
3. Distinguish an environment problem, a design error, a tool bug, and a documentation defect. Do not report an unverified inference as a tool bug.
4. Remove secrets, proprietary netlists, credentials, and sensitive paths from the report.

## Documentation-bug report template

```markdown
## Summary
<one sentence>

## Affected context
- File and heading: `context/designer/<file>.md` — `<heading>`
- EDA-MCP/tool version or commit: <if known>

## Minimal reproduction
<exact valid MCP call and only the SKILL/deck needed to reproduce>

## Observed result
```text
<unmodified error or diagnostic>
```

## Expected result
<what the context promised>

## Proposed correction
<verified replacement, or explicitly say that a capability is missing>

## Duplicate check
- Related issues searched: #<n>, #<n>
```

## Valid API examples

For a digital regression run:

```text
remote_control(action="run_command", command="xrun -f filelists/filelist.f -covoverwrite -coverage all")
```

Use WorkBoard for version-controlled design artifacts: initialize a board, track RTL/TB files inside its local board directory, and export or push changes. Do not recommend unversioned direct remote writes merely for convenience.

## Report quality

Include the tool action, inputs relevant to the failure, exact returned diagnostic, expected behavior, and the smallest safe reproduction. State uncertainty plainly. `report_issue` adds agent/session/log metadata automatically; the report body should contain the engineering evidence.
