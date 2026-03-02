"""
PDF Report endpoint.
POST /reports/generate -> returns PDF file download.
"""

import io
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate")
async def generate_report(analysis_result: dict):
    """
    Takes the full analysis result from /analyze
    and returns a downloadable PDF report.

    Frontend calls this right after /analyze completes.
    Pass the entire analysis_result JSON as the body.
    """
    try:
        from src.reports.pdf_generator import generate_pdf_report

        pdf_bytes = generate_pdf_report(analysis_result)
        filename = f"skillevector_report_{analysis_result.get('request_id', 'report')}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except Exception as e:
        logger.error("PDF generation failed: %s", e)
        raise HTTPException(500, f"PDF generation failed: {str(e)}")
