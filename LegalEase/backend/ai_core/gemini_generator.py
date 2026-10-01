from __future__ import annotations

from backend.config import Settings


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini cannot generate a document."""


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):
        self.settings = settings

        if not settings.gemini_api_key:
            self.client = None

        else:
            try:
                from google import genai

            except ImportError as exc:
                raise GeminiGenerationError(
                    "The google-genai package is missing. "
                    "Run: pip install -r requirements.txt"
                ) from exc

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        return f"""
You are the drafting engine for LegalEase,
an AI-assisted legal document generator.

Create a professional FIRST DRAFT of the requested
legal document using only the supplied facts.

Do not invent:
- Names
- Addresses
- Monetary amounts
- Dates
- Governing law
- Obligations
- Other material facts

If a material fact is missing, use a clear
bracketed placeholder such as:

[GOVERNING LAW]

DOCUMENT INFORMATION
--------------------

Document Type:
{document_type}

Parties:
{parties}

Terms and Conditions:
{terms}

Effective Date:
{dates}


REQUIREMENTS
------------

1. Use a formal legal-document structure.

2. Include a clear title.

3. Include the effective date.

4. Identify all supplied parties.

5. Organize clauses using numbered headings
   where appropriate.

6. Incorporate every supplied term faithfully.

7. Do not change the meaning of user-provided terms.

8. Include signature blocks when appropriate.

9. Do not claim that the document is legally valid.

10. Do not claim that the document is enforceable.

11. Do not claim that the document was reviewed
    by a lawyer.

12. Do not provide commentary outside the document.

13. Prefer clear and precise language over
    unnecessary legal jargon.

14. Return only the document text.
"""

    def _generation_config(self):

        from google.genai import types

        return types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8000,
        )

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        if not self.client:
            raise GeminiGenerationError(
                "GEMINI_API_KEY is not configured. "
                "Add it to the project's .env file."
            )

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

        try:

            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=self._generation_config(),
            )

        except Exception as exc:

            raise GeminiGenerationError(
                f"Gemini request failed: {exc}"
            ) from exc

        text = (response.text or "").strip()

        if not text:
            raise GeminiGenerationError(
                "Gemini returned an empty document."
            )

        if len(text) > self.settings.max_output_chars:

            text = text[
                : self.settings.max_output_chars
            ].rstrip()

        return text