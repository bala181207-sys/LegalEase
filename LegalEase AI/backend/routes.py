from fastapi import APIRouter, HTTPException

from ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import (
    DocumentRequest,
    DocumentResponse,
)


router = APIRouter(
    tags=["Documents"]
)


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest,
):

    try:

        generator = GeminiDocumentGenerator()

        generated_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        return DocumentResponse(
            document_type=request.document_type,
            generated_text=generated_text,
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {error}",
        )