from __future__ import annotations

import os

from pathlib import Path

import requests
import streamlit as st

from backend.services.document_formatter import (
    format_docx,
    format_html_preview,
    format_pdf,
    sanitize_text,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


logo_environment_path = os.getenv(
    "LOGO_PATH",
    "assets/logo.png",
)


LOGO_PATH = (
    BASE_DIR / logo_environment_path
)


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .document-preview {
        background: #111827;
        color: #f9fafb;
        padding: 24px;
        border-radius: 14px;
        max-height: 620px;
        overflow-y: auto;
        line-height: 1.7;
        font-family: Georgia, serif;
    }

    .small-note {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .app-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .app-subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

if LOGO_PATH.exists():

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.image(
            str(LOGO_PATH),
            width=120,
        )


st.markdown(
    '<div class="app-title">LegalEase</div>',
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="app-subtitle">
        AI-Powered Legal Document Generator
    </div>
    """,
    unsafe_allow_html=True,
)


st.info(
    "LegalEase creates AI-assisted first drafts. "
    "Review the document for your jurisdiction "
    "with a qualified legal professional before "
    "signing or relying on it."
)


# --------------------------------------------------
# Input form
# --------------------------------------------------

with st.form("document_form"):

    st.subheader(
        "Document Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        document_type = st.text_input(
            "Document Type",
            placeholder=(
                "Example: "
                "Non-Disclosure Agreement"
            ),
        )

        dates = st.text_input(
            "Effective Date",
            placeholder=(
                "Example: "
                "October 1, 2026"
            ),
        )

    with col2:

        parties = st.text_area(
            "Parties Involved",
            placeholder=(
                "Jane Doe (Disclosing Party), "
                "TechNova Inc. (Receiving Party)"
            ),
            height=120,
        )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Separate clauses using semicolons.\n\n"
            "Example:\n"
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "15 days notice"
        ),
        height=160,
    )

    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# Generate document
# --------------------------------------------------

if submitted:

    missing = []

    if not document_type.strip():
        missing.append(
            "Document Type"
        )

    if not parties.strip():
        missing.append(
            "Parties"
        )

    if not terms.strip():
        missing.append(
            "Terms & Conditions"
        )

    if not dates.strip():
        missing.append(
            "Effective Date"
        )

    if missing:

        st.error(
            "Please complete: "
            + ", ".join(missing)
        )

    else:

        with st.spinner(
            "Generating your legal draft..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",

                    json={
                        "document_type": (
                            document_type
                        ),
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },

                    timeout=95,
                )

                response.raise_for_status()

                data = response.json()

                st.session_state[
                    "document_type"
                ] = data["document_type"]

                st.session_state[
                    "content"
                ] = data["content"]

                st.session_state[
                    "terms"
                ] = terms

                st.success(
                    "Document generated successfully."
                )

            except requests.RequestException as exc:

                detail = (
                    "Backend request failed. "
                    "Make sure FastAPI is running "
                    f"at {BACKEND_URL}."
                )

                if (
                    getattr(
                        exc,
                        "response",
                        None,
                    )
                    is not None
                ):

                    try:

                        detail = (
                            exc.response
                            .json()
                            .get(
                                "detail",
                                detail,
                            )
                        )

                    except Exception:
                        pass

                st.error(detail)


# --------------------------------------------------
# Document editor
# --------------------------------------------------

if "content" in st.session_state:

    st.divider()

    st.subheader(
        "Generated Document"
    )

    edited = st.text_area(
        "Edit Document",
        value=st.session_state[
            "content"
        ],
        height=550,
        key="editable_document",
    )

    st.session_state[
        "content"
    ] = edited


    # --------------------------------------------------
    # Styled preview
    # --------------------------------------------------

    st.subheader(
        "Document Preview"
    )

    preview_html = (
        format_html_preview(
            edited
        )
    )

    st.markdown(
        preview_html,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------
    # Generate download files
    # --------------------------------------------------

    clean_content = sanitize_text(
        edited
    )

    doc_type = st.session_state.get(
        "document_type",
        "Legal Document",
    )

    terms_value = st.session_state.get(
        "terms",
        "",
    )


    docx_bytes = format_docx(
        text=clean_content,
        doc_type=doc_type,
        terms=terms_value,
        logo_path=LOGO_PATH,
    )


    pdf_bytes = format_pdf(
        text=clean_content,
        doc_type=doc_type,
        logo_path=LOGO_PATH,
    )


    # --------------------------------------------------
    # Download buttons
    # --------------------------------------------------

    st.subheader(
        "Download Document"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.download_button(
            label="Download TXT",

            data=clean_content.encode(
                "utf-8"
            ),

            file_name=(
                "legalease_document.txt"
            ),

            mime="text/plain",

            use_container_width=True,
        )

    with c2:

        st.download_button(
            label="Download DOCX",

            data=docx_bytes,

            file_name=(
                "legalease_document.docx"
            ),

            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

            use_container_width=True,
        )

    with c3:

        st.download_button(
            label="Download PDF",

            data=pdf_bytes,

            file_name=(
                "legalease_document.pdf"
            ),

            mime="application/pdf",

            use_container_width=True,
        )