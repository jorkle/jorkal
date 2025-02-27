import re


async def sanitize_title(self, title):
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


async def sanitize_company(self, company):
    sanitizations = [
        {"find": r",?\s?LLC", "replace": " LLC"},
        {"find": r",?\s?INC", "replace": " INC"},
        {"find": r",?\s?Incorporated", "replace": " INC"},
    ]
    for sanitization in sanitizations:
        company_name = re.sub(
            sanitization["find"], sanitization["replace"], company, re.IGNORECASE
        )
    return company_name  # pyright: ignore
