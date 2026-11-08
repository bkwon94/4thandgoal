"""
AT-56 of easter-eggs: the real egg draft of a week refuses a hold on a blurb and writes nothing to the egg file.
The agent is the port of draft_week, so this run gives it a fixed answer with six test spots. No spot is real.
"""
import json
import sys
import tempfile
from pathlib import Path

from eggs.draft import DraftError, draft_week
from eggs.eggfile import read_spots

# Six test spots of week 8. The third spot is a hold on the target blurb-luck.
SPOTS = [{"page": "/2026/week-08/", "target": f"test-spot-{n}", "action": "tap2", "conditions": {},
          "reason": f"Test reason {n}."} for n in range(1, 7)]
SPOTS[2] = {"page": "/midseason/2026/", "target": "blurb-luck", "action": "hold", "conditions": {},
            "reason": "Test reason 3, a hold on a blurb."}
ANSWER = "Here are the six spots.\n```json\n" + json.dumps(SPOTS) + "\n```\n"

path = Path(tempfile.mkdtemp()) / "2026.toml"
path.write_text("# A temp egg file of the evidence of AT-56.\n", encoding="utf-8")
before = path.read_text(encoding="utf-8")
print(f"The temp egg file before the draft: {path.name}, {len(read_spots(path))} spots, {len(before)} bytes.")
print("The answer of the agent port, spot 3:", json.dumps(SPOTS[2]))
try:
    draft_week(path, 8, lambda prompt: ANSWER, prompt="the prompt")
    print("The draft wrote the spots.")
except DraftError as err:
    print(f"DraftError: {err}")
after = path.read_text(encoding="utf-8")
print(f"The temp egg file after the draft: {len(read_spots(path))} spots, {len(after)} bytes, unchanged {after == before}.")
sys.exit(0)
