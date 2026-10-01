# LegalEase

AI-Powered Legal Document Generator

LegalEase is a full-stack AI-assisted legal document
generation application.

The application uses:

- Streamlit
- FastAPI
- Google Gemini
- python-docx
- FPDF2
- Pydantic

---

# Architecture

```text
User
 |
 v
Streamlit Frontend
 |
 | HTTP POST /generate
 v
FastAPI Backend
 |
 v
Gemini AI
 |
 v
Generated Legal Draft
 |
 +------> Editable Preview
 |
 +------> TXT
 |
 +------> DOCX
 |
 +------> PDF