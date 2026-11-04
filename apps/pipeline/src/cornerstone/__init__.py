"""
Cornerstone Weekly package.
It builds the weekly fantasy football report page from Sleeper data.
"""
from pathlib import Path

# The rule prompt of the waiver board. The facts package and the analyzer package keep theirs in their own folders.
RULE_PROMPTS = Path(__file__).parent / "prompts"
