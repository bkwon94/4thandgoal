"""
Cornerstone Weekly package.
It builds the weekly fantasy football report page from Sleeper data.
"""
from pathlib import Path

# The rule prompts of the analyzer. The writer and the verifier keep theirs in the facts package, and the research
# step keeps its own in the waiver package.
RULE_PROMPTS = Path(__file__).parent / "prompts"
