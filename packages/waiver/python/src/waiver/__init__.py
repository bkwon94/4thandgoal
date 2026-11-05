"""
The waiver package: the waiver board, its price, its research step, and the waiver file of each week.
It imports only the league and the facts packages, so a client takes it or omits it with one line of client.toml.
"""
from pathlib import Path

# The rule prompt of the research step. load_prompt of the facts package reads it from this folder.
RULE_PROMPTS = Path(__file__).parent / "prompts"
