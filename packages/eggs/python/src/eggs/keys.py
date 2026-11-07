"""
The env name of the commissioner key of a client, one function for the API app and for the egg drop of the pipeline.
"""


def commissioner_key_env(slug: str) -> str:
    """The env value of the commissioner key of the client `slug`, such as CORNERSTONE_COMMISSIONER_KEY_CPC for cpc."""
    return f"CORNERSTONE_COMMISSIONER_KEY_{slug.upper()}"
