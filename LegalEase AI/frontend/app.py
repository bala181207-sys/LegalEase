import html
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.document_formatter import (
    format_docx,
    format_pdf,
)

from utils.text_utils import (
    sanitize_text,
    safe_filename,
)


load_dotenv()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "120"
    )
)


# --------------------------------------------------
# HTML PREVIEW
# --------------------------------------------------

def preview_html(text: str) -> str:

    escaped = html.escape(
        sanitize_text(text)
    )

    escaped = escaped.replace(
        "\n\n",
        "</p><p>"
    )

    escaped = escaped.replace(
        "\n",
        "<br>"
    )

    return f"""
    <div style="
        background:#111827;
        color:#f9fafb;
        padding:24px;
        border-radius:14px;
        border:1px solid #374151;
        max-height:650px;
        overflow-y:auto;
        line-height:1.7;
        font-family:Georgia,serif;
        font-size:16px;
    ">
        <p>{escaped}</p>
    </div>
    """


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("⚖️ LegalEase")

st.caption(
    "AI-Powered Legal Document Generator"
)

st.info(
    "LegalEase creates AI-assisted legal document drafts. "
    "Review the generated document with a qualified legal "
    "professional before relying on it."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Document Settings")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "NDA (Non-Disclosure Agreement)",
            "Lease Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "General Agreement",
        ],
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    logo_file = st.file_uploader(
        "Upload Company Logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
        help="Optional logo for DOCX and PDF.",
    )


# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

st.subheader("Document Information")


parties = st.text_area(
    "Parties Involved",
    placeholder=(
        "Jane Doe (Service Provider); "
        "TechNova Inc. (Client)"
    ),
    height=120,
)


terms = st.text_area(
    "Terms & Conditions",
    placeholder=(
        "Payment to be made within 30 days of invoice; "
        "Confidentiality must be maintained; "
        "Either party may terminate with 15 days notice"
    ),
    height=160,
    help="Separate each term using a semicolon (;).",
)


# --------------------------------------------------
# GENERATE
# --------------------------------------------------

generate_button = st.button(
    "✨ Generate Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    else:

        payload = {

            "document_type": document_type,

            "parties": parties,

            "terms": terms,

            "effective_date":
                effective_date.isoformat(),
        }

        with st.spinner(
            "Generating document with Gemini..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=TIMEOUT,
                )

                if response.ok:

                    data = response.json()

                    st.session_state[
                        "generated_text"
                    ] = data["generated_text"]

                    st.session_state[
                        "document_type"
                    ] = data["document_type"]

                    st.session_state[
                        "terms"
                    ] = terms

                    st.session_state[
                        "editing"
                    ] = False

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error "
                        f"({response.status_code}): "
                        f"{detail}"
                    )

            except requests.RequestException as error:

                st.error(
                    "Could not connect to the FastAPI backend.\n\n"
                    f"Backend URL: {BACKEND_URL}\n\n"
                    f"Error: {error}"
                )


# --------------------------------------------------
# GENERATED DOCUMENT
# --------------------------------------------------

if "generated_text" in st.session_state:

    st.divider()

    st.subheader(
        "Generated Document"
    )

    st.markdown(
        preview_html(
            st.session_state[
                "generated_text"
            ]
        ),
        unsafe_allow_html=True,
    )

    st.write("")

    edit_button = st.button(
        "✏️ Edit Document",
        use_container_width=True,
    )

    if edit_button:

        st.session_state[
            "editing"
        ] = True


# --------------------------------------------------
# EDIT DOCUMENT
# --------------------------------------------------

if st.session_state.get(
    "editing",
    False
):

    edited_text = st.text_area(
        "Edit Your Document",
        value=st.session_state[
            "generated_text"
        ],
        height=600,
    )

    save_button = st.button(
        "💾 Save Changes",
        use_container_width=True,
    )

    if save_button:

        st.session_state[
            "generated_text"
        ] = edited_text

        st.session_state[
            "editing"
        ] = False

        st.rerun()


# --------------------------------------------------
# DOWNLOAD SECTION
# --------------------------------------------------

if "generated_text" in st.session_state:

    st.divider()

    st.subheader(
        "Download Document"
    )

    current_text = sanitize_text(
        st.session_state[
            "generated_text"
        ]
    )

    current_type = st.session_state[
        "document_type"
    ]

    current_terms = st.session_state.get(
        "terms",
        ""
    )

    logo_bytes = None

    if logo_file:

        logo_bytes = logo_file.getvalue()


    filename = safe_filename(
        current_type.lower()
    )


    col1, col2, col3 = st.columns(3)


    # TXT

    with col1:

        st.download_button(
            label="⬇️ Download TXT",
            data=current_text.encode(
                "utf-8"
            ),
            file_name=f"{filename}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # DOCX

    with col2:

        docx_data = format_docx(
            text=current_text,
            doc_type=current_type,
            terms=current_terms,
            logo_bytes=logo_bytes,
        )

        st.download_button(
            label="⬇️ Download DOCX",
            data=docx_data,
            file_name=f"{filename}.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )


    # PDF

    with col3:

        pdf_data = format_pdf(
            text=current_text,
            doc_type=current_type,
            terms=current_terms,
            logo_bytes=logo_bytes,
        )

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_data,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

else:

    st.divider()

    st.subheader(
        "How LegalEase Works"
    )

    st.markdown(
        """
        **Step 1:** Enter the document information.

        **Step 2:** LegalEase sends the information to the FastAPI backend.

        **Step 3:** The backend sends a structured prompt to Gemini.

        **Step 4:** Gemini generates the legal document draft.

        **Step 5:** You can preview and edit the document.

        **Step 6:** Download it as TXT, DOCX or PDF.
        """
    )