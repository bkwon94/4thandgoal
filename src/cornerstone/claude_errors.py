"""
The errors of a Claude call that gives no parsed output: a refusal, or an output that does not fit the model.
They sit in the provider layer beside the chart read, so the writer raises them and the chart catches them.
"""


class RefusalError(Exception):
    """Claude refused the request, so there is no parsed output."""


class WriterError(Exception):
    """Claude gave no parsed output, for example when the output does not fit the model."""
