"""
The Writer port: the one Claude call that the writer, the verifier, the analyzer, the chart read, and the research use.
ClaudeWriter in writer.py implements it. FakeWriter in tests/fakes.py is its one fake.
"""
from typing import Protocol

from pydantic import BaseModel


# The port sits in the provider layer beside claude_errors, so a module of any layer above can take a Writer.
class Writer(Protocol):
    def parse(
        self, content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
        cache_ttl: str | None = None, effort: str = "high", tools: list[dict] | None = None,
    ) -> BaseModel:
        """One user message to Claude, parsed into the output model.

        The system prompt goes out as one cached block. `cache_ttl` None keeps the default five-minute lifetime.
        `effort` sets the depth of the answer. `tools` adds server tools, such as web search.
        Raises RefusalError on a refusal and WriterError when there is no parsed output.
        """
        ...
