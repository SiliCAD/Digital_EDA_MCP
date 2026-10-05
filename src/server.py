import os
import sys
import time
import json
import shlex
import logging
import subprocess
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP, Context
from src.core.ssh_client import RemoteSession
from src.core.scp_client import SCPClient
from src.clients.workboard_client import WorkBoardClient
from src.issue_reporter import IssueReporter

# Get absolute path to base dir (repo root) and setup logs logging folder
base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
logs_dir = os.path.join(base_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Generate unique log file for each server instance (timestamp + PID)
session_timestamp = time.strftime("%Y%m%d_%H%M%S")
log_filename = f"digital_eda_mcp_{session_timestamp}_{os.getpid()}.log"
log_filepath = os.path.join(logs_dir, log_filename)

# Configure logger
logger = logging.getLogger("Digital_EDA_MCP")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")

# File handler for saving logs in logs/
file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Attach file handler to digital_eda_mcp module logger as well
logging.getLogger("digital_eda_mcp").addHandler(file_handler)
logging.getLogger("digital_eda_mcp").setLevel(logging.INFO)

# Stderr handler for stdio output
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)

logger.info(f"Digital_EDA_MCP Server logging initialized. Log file: {log_filepath}")

# Initialize FastMCP named Digital_EDA_MCP
mcp = FastMCP("Digital_EDA_MCP")

# Get tool-specific config paths inside config/ directory
config_dir = os.path.join(base_dir, "config")
remote_control_config = os.path.join(config_dir, "config_remote_control.json")

# Dedicated SSH session for remote execution
remote_session = RemoteSession(config_path=remote_control_config)

# WorkBoard client for local-remote file synchronization
workboard_client = WorkBoardClient(base_workboard_dir=os.path.join(base_dir, "workboard"))

def _format_result_summary(res: str, max_len: int = 300) -> str:
    """Formats tool return result on a single line for clean, full lifecycle logging."""
    if not res:
        return "<empty>"
    lines = [line.strip() for line in res.strip().splitlines() if line.strip()]
    clean = " || ".join(lines)
    if len(clean) > max_len:
        return f"{clean[:max_len]}... [{len(res)} bytes total]"
    return clean

@mcp.tool()
def remote_control(action: str, command: str = "", path: str = "", content: str = "", timeout: float = 60.0) -> str:
    """
    Execute shell commands and perform file operations on the remote EDA server.
    
    Args:
        action: The operation to perform ('run_command', 'read_file', or 'write_file')
        command: Shell command to execute when action='run_command' (e.g., irun, xrun, jg, vcs, yosys)
        path: Remote file path when action='read_file' or action='write_file'
        content: Text content to write when action='write_file'
        timeout: Maximum wait time in seconds for execution (default: 60.0)
    """
    logger.info(f"[TOOL CALL] remote_control: action={action!r}, command={command!r}, path={path!r}, content_len={len(content)}, timeout={timeout}")
    start_time = time.time()
    act = action.lower().strip()
    
    try:
        if act in ("run_command", "run_remote_command", "run", "exec", "execute"):
            if not command.strip():
                return "Error: 'command' argument is required when action='run_command'."
            exit_code, stdout, stderr = remote_session.execute_command(command, timeout=timeout)
            output = []
            output.append(f"Exit Status: {exit_code}")
            if stdout.strip():
                output.append(f"\n--- STDOUT ---\n{stdout}")
            if stderr.strip():
                output.append(f"\n--- STDERR ---\n{stderr}")
            res = "\n".join(output)
            
        elif act in ("read_file", "read_remote_file", "read"):
            if not path.strip():
                return "Error: 'path' argument is required when action='read_file'."
            res = remote_session.read_file(path, timeout=timeout)
            
        elif act in ("write_file", "write_remote_file", "write"):
            if not path.strip():
                return "Error: 'path' argument is required when action='write_file'."
            write_res = remote_session.write_file(path, content, timeout=timeout)
            res = write_res or f"Successfully wrote {len(content)} bytes to remote file '{path}'."
            
        else:
            res = f"Error: Unknown action '{action}'. Valid actions are 'run_command', 'read_file', 'write_file'."
            
        duration = time.time() - start_time
        logger.info(f"[TOOL RESULT] remote_control (action={act}) finished in {duration:.2f}s | Result: {_format_result_summary(res)}")
        return res
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[TOOL ERROR] remote_control (action={action}) failed in {duration:.2f}s: {e}")
        return f"Error in remote_control tool: {str(e)}"

@mcp.tool()
def workboard(
    action: str = "status",
    workboard_name: str = "",
    remote_path: str = "",
    local_path: str = "",
    message: str = "Agent sync",
    recursive: bool = False,
    overwrite: bool = False,
    timeout: float = 60.0
) -> str:
    """
    Git-backed WorkBoard tool for local-remote file synchronization and version control.
    
    Actions:
      - 'initialize': Create a new local WorkBoard workspace and initialize a local Git repository.
      - 'add': Fetch a file/folder from remote server path and add it to a specific WorkBoard at local_path.
      - 'export': Upload a local WorkBoard file/folder to a specified remote server location and register tracking.
      - 'pull': Re-fetch latest remote server version of an added file to update the local WorkBoard.
      - 'push': Upload local edits from WorkBoard back to mapped remote server location and commit locally.
      - 'diff': Display unified diff between local WorkBoard file and remote server version.
      - 'status': List all tracked files and their status for a specific WorkBoard.
      - 'history': Display local Git commit history for a specific file or workspace.
    """
    logger.info(f"[TOOL CALL] workboard: action={action!r}, workboard_name={workboard_name!r}, remote_path={remote_path!r}, local_path={local_path!r}")
    start_time = time.time()
    try:
        act = action.lower().strip()
        if act == "initialize":
            res = workboard_client.initialize(workboard_name=workboard_name or "default")
        elif act in ("add", "add_file"):
            res = workboard_client.add(remote_path=remote_path, local_path=local_path, workboard_name=workboard_name, timeout=timeout)
        elif act in ("export", "export_file"):
            if not local_path.strip():
                return "Error: 'local_path' is required for export action."

            # Check if remote file exists using remote_session.execute_command
            wb_name, _ = workboard_client._resolve_workboard_name(workboard_name)
            wb_dir = workboard_client._get_workboard_dir(wb_name)
            registry = workboard_client._load_registry(wb_dir, wb_name)
            target_remote = remote_path.strip() or registry.get("files", {}).get(local_path.strip(), {}).get("remote_path", "")

            if target_remote and not overwrite:
                quoted_remote = f"$HOME{shlex.quote(target_remote[1:])}" if target_remote.startswith("~") else shlex.quote(target_remote)
                check_cmd = f"test -e {quoted_remote}"
                exit_code, _, _ = remote_session.execute_command(check_cmd, timeout=timeout)
                if exit_code == 0:
                    return f"Error: File at remote path '{target_remote}' already exists on the server. Set overwrite=True to overwrite it."

            res = workboard_client.export(local_path=local_path, remote_path=remote_path, workboard_name=workboard_name, message=message, timeout=timeout)
        elif act == "pull":
            res = workboard_client.pull(local_path=local_path, workboard_name=workboard_name, timeout=timeout)
        elif act == "push":
            res = workboard_client.push(local_path=local_path, workboard_name=workboard_name, message=message, timeout=timeout)
        elif act == "diff":
            res = workboard_client.diff(local_path=local_path, workboard_name=workboard_name)
        elif act == "status":
            res = workboard_client.status(workboard_name=workboard_name)
        elif act in ("history", "log"):
            res = workboard_client.history(local_path=local_path, workboard_name=workboard_name)
        else:
            res = f"Error: Unknown action '{action}'. Valid actions are 'initialize', 'add', 'export', 'pull', 'push', 'diff', 'status', 'history'."

        duration = time.time() - start_time
        logger.info(f"[TOOL RESULT] workboard (action={act}) finished in {duration:.2f}s | Result: {_format_result_summary(res)}")
        return res
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[TOOL ERROR] workboard (action={action}) failed in {duration:.2f}s: {e}")
        return f"Error in workboard tool: {str(e)}"

def get_client_agent_name(ctx: Context = None) -> str:
    """Extracts client agent name (e.g. 'Antigravity', 'claude-code') from MCP initialization clientInfo metadata."""
    try:
        if ctx and ctx.request_context and ctx.request_context.session:
            client_params = getattr(ctx.request_context.session, "_client_params", None)
            if client_params and hasattr(client_params, "clientInfo") and client_params.clientInfo:
                name = getattr(client_params.clientInfo, "name", None)
                if name and str(name).strip():
                    return str(name).strip()
    except Exception as e:
        logger.debug(f"Could not extract clientInfo from MCP context: {e}")
    return "unknown"

@mcp.tool()
def report_issue(
    title: str,
    body: str = "",
    label: str = "bug",
    agent_model: str = "",
    session_id: str = "unknown",
    ctx: Context = None
) -> str:
    """
    Report an issue, bug, or feature request directly to GitHub.
    
    Args:
        title: Issue Title describing the problem, bug, or feature request.
        body: Issue Content in Markdown format (bug report, feature request, tracebacks, proposals, etc.).
        label: Issue Label ('bug', 'enhancement', 'feature-request', etc.).
        agent_model: Model name/version of the agent (e.g. 'gemini-3.6-flash', 'claude-3.5-sonnet', 'opus').
        session_id: The conversation/session ID of the current agent turn.
    """
    detected_agent_name = get_client_agent_name(ctx)
    logger.info(f"[TOOL CALL] report_issue: title={title!r}, detected_agent={detected_agent_name!r}, model={agent_model!r}, label={label!r}")
    return IssueReporter.create_issue(
        title=title,
        body=body,
        label=label,
        agent_model=agent_model,
        session_id=session_id,
        agent_name=detected_agent_name,
        log_file=log_filename,
        cwd=base_dir
    )

if __name__ == "__main__":
    # Start the server on stdio transport (default)
    mcp.run()
