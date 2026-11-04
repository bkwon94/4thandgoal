"""
The analyzer package: the trade rubric, the analysis, the finder, the grade limits, and the analyzer routes of the API.
RULE_PROMPTS is the folder of its rule prompts, which facts.writer.load_prompt reads with the voice of the client.
"""
from pathlib import Path

# The rule prompts of the analyzer: analysis.md, finder.md, and rubric.md. A client never changes a rule prompt.
RULE_PROMPTS = Path(__file__).parent / "prompts"
