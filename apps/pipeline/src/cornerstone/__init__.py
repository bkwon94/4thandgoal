"""
Cornerstone Weekly package.
It builds the weekly fantasy football report page from Sleeper data.
"""
from pathlib import Path

# The rule prompts of the analyzer and the waiver board. The writer and the verifier keep theirs in the facts package.
RULE_PROMPTS = Path(__file__).parent / "prompts"
