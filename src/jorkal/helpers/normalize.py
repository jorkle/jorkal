import re


async def sanitize_title(title: str) -> str:
    """
    Sanitize the passed in job `title` by applying regular expressions (find and replace).

    Args:
        title (str): The job title to sanitize.

    Returns:
        title (str): The sanitized job title.
    """
    # TODO: Have sanitization regular expressions passed in as a parameter in a list of strings.
    sanitizations = [
        {"find": r"Jr.?\s?", "replace": "Junior "},
        {"find": r"Sr.?\s?", "replace": "Senior "},
    ]
    for sanitization in sanitizations:
        title = re.sub(
            sanitization["find"],
            sanitization["replace"],
            title,
            flags=re.IGNORECASE,
        )
    return title


async def sanitize_company(company: str) -> str:
    """
    Sanitize the passed in job `company` name by applying regular expressions (find and replace).

    Args:
        title (str): The company name to sanitize.

    Returns:
        title (str): The sanitized company name.
    """
    # TODO: Have sanitization regular expressions passed in as a parameter in a list of strings.
    sanitizations = [
        {"find": r",?\s?LLC", "replace": " LLC"},
        {"find": r",?\s?INC", "replace": " INC"},
        {"find": r",?\s?Incorporated", "replace": " INC"},
    ]
    for sanitization in sanitizations:
        company = re.sub(
            sanitization["find"], sanitization["replace"], company, re.IGNORECASE
        )
    return company
