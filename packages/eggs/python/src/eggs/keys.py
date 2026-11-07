"""
The env name of the commissioner key of a client, and the live API URL, for the API app and the pipeline.
Both read them from here, so the egg drop and the egg undo never differ.
"""

# The API of the site, the same default as the site config. A local run sets CORNERSTONE_API_URL.
API_URL = "https://api.4thandgoal.app"


def commissioner_key_env(slug: str) -> str:
    """The env value of the commissioner key of the client `slug`, such as CORNERSTONE_COMMISSIONER_KEY_CPC for cpc."""
    return f"CORNERSTONE_COMMISSIONER_KEY_{slug.upper()}"
