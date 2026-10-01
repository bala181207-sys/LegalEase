from utils.text_utils import (
    sanitize_text,
    split_terms,
    safe_filename,
)

from utils.document_formatter import (
    format_docx,
    format_pdf,
)


def test_sanitize_text():

    result = sanitize_text(
        "Hello\u2014world\u2019s"
    )

    assert result == "Hello-world's"


def test_split_terms():

    result = split_terms(
        "First term; Second term; Third term"
    )

    assert result == [
        "First term",
        "Second term",
        "Third term",
    ]


def test_safe_filename():

    result = safe_filename(
        "NDA / Contract"
    )

    assert result == "NDA_Contract"


def test_docx_generation():

    result = format_docx(
        text=(
            "NON-DISCLOSURE AGREEMENT\n\n"
            "1. Confidentiality\n"
            "The parties agree."
        ),
        doc_type="NDA",
        terms=(
            "Keep information confidential;"
            "No third-party disclosure"
        ),
    )

    assert result[:2] == b"PK"


def test_pdf_generation():

    result = format_pdf(
        text=(
            "NON-DISCLOSURE AGREEMENT\n\n"
            "1. Confidentiality\n"
            "The parties agree."
        ),
        doc_type="NDA",
        terms=(
            "Keep information confidential;"
            "No third-party disclosure"
        ),
    )

    assert result.startswith(
        b"%PDF"
    )