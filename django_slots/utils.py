import re


def pascalcase_to_snakecase(string: str) -> str:
    """
    Convert string from PascalCase to snake_case
    """
    return (
        re.sub("(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))", "_\\1", string)
        .lower()
        .strip("_")
    )
