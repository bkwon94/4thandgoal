"""
The analyzer package: the proposed trade, the fact sheet, the Advisor, the Finder, the grade limits, and the routes.
RULE_PROMPTS is the folder of its rule prompts, which facts.writer.load_prompt reads with the voice of the client.
"""
from pathlib import Path

# The rule prompts of the analyzer: advisor.md, finder_pick.md, finder_pick_repair.md, and sell_high.md. A client
# never changes a rule prompt.
RULE_PROMPTS = Path(__file__).parent / "prompts"
