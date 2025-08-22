import os
from dotenv import load_dotenv
import subprocess

from langchain_openai import ChatOpenAI

from langchain.agents import initialize_agent, AgentType, tool
from langchain_core.messages import SystemMessage, HumanMessage

# --- Load environment ---
load_dotenv()

# --- Setup LLM ---
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# --- Safety wrapper for git commands ---
SAFE_COMMANDS = {"status", "diff", "log", "branch"}
DANGEROUS_COMMANDS = {"reset", "push", "rebase", "merge", "checkout"}

def safe_run(args: list[str]) -> str:
    """Run git command with safety checks."""
    cmd = " ".join(args)
    if any(d in args for d in DANGEROUS_COMMANDS):
        return f"[BLOCKED] Command '{cmd}' is considered unsafe. Confirm manually."
    try:
        result = subprocess.check_output(["git"] + args, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running git {cmd}:\n{e.output}"

@tool("git_status", return_direct=True)
def git_status(dummy_input: str) -> str:
    """Check the working tree status."""
    return safe_run(["status"])

@tool("git_branch", return_direct=True)
def git_branch(dummy_input: str) -> str:
    """Show current branch info."""
    return safe_run(["branch"])

@tool("git_log", return_direct=True)
def git_log(dummy_input: str) -> str:
    """Show recent commit history."""
    return safe_run(["log", "--oneline", "-5"])

@tool("git_diff", return_direct=True)
def git_diff(dummy_input: str) -> str:
    """Show unstaged changes."""
    return safe_run(["diff"])

# --- Create Agent ---
tools = [git_status, git_branch, git_log, git_diff]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# --- Example Run ---
if __name__ == "__main__":
    user_query = "what branch am I on"
    response = agent.run(user_query)
    print("\n🤖 Agent Response:\n", response)
