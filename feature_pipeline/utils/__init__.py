from typing import List


def flatten(nested_list: List) -> List:
    """Flatten a list of lists into a single list."""

    return [item for sublist in nested_list for item in sublist]
