"""
The egg draft step: it runs the claude CLI in headless mode with the draft prompt of the eggs package.
The eggs package checks the answer and writes the spots, so this module holds only the agent call.
"""
import subprocess
from pathlib import Path

from eggs.draft import DraftError, Propose, draft_prompt, draft_week
from eggs.eggfile import Spot
from eggs.values import EggsValues
from league.client import Client
from league.paths import build_dir, site_week_dir

# The agent may only read the repo. It answers with the JSON list of spots and changes no file.
READ_TOOLS = "Read,Glob,Grep"


def claude_propose(root: Path) -> Propose:
    """The agent of the draft: one headless run of the claude CLI at the repo root."""

    def propose(prompt: str) -> str:
        try:
            done = subprocess.run(["claude", "-p", prompt, "--allowedTools", READ_TOOLS, "--output-format", "text"],
                                  cwd=root, check=True, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError) as err:
            raise DraftError(f"The claude CLI failed, so the draft writes nothing: {err}") from None
        return done.stdout

    return propose


def run_egg_draft(client: Client, season: int, week: int, egg_file: Path, root: Path) -> list[Spot]:
    """Draft the spots of the week into the egg file with the agent. The built week page must exist."""
    page = site_week_dir(build_dir(client.folder), season, week) / "page.json"
    if not page.is_file():
        raise FileNotFoundError(2, "No built week page", str(page))
    size = client.values.package(EggsValues).drop_size
    prompt = draft_prompt(egg_file, week, page, size)
    return draft_week(egg_file, week, claude_propose(root), prompt, size)
