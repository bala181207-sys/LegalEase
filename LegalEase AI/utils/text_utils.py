import re
import unicodedata


def sanitize_text(text: str) -> str:

    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u00a0": " ",
        "\u2026": "...",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    text = text.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def split_terms(terms: str) -> list[str]:

    cleaned = sanitize_text(terms)

    result = []

    for item in cleaned.split(";"):

        item = item.strip()

        item = item.lstrip("-")

        item = item.strip()

        if item:
            result.append(item)

    return result


def safe_filename(
    value: str,
    fallback: str = "legalease_document",
) -> str:

    value = value.strip()

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value
    )

    value = value.strip("._")

    return value or fallback