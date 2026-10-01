from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
    GeminiGenerationError,
)

from backend.config import get_settings


router = APIRouter()


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=8000,
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000,
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )


class DocumentResponse(BaseModel):

    document_type: str

    content: str


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    request: DocumentRequest,
) -> DocumentResponse:

    settings = get_settings()

    total_length = (
        len(request.document_type)
        + len(request.parties)
        + len(request.terms)
        + len(request.dates)
    )

    if total_length > settings.max_input_chars:

        raise HTTPException(
            status_code=413,
            detail=(
                "Input is too large. "
                "Please shorten the supplied details."
            ),
        )

    generator = GeminiDocumentGenerator(settings)

    try:

        content = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )

    except GeminiGenerationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return DocumentResponse(
        document_type=request.document_type,
        content=content,
    )