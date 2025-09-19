import uuid
import time
import asyncio
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form
from typing import Optional, List, Dict, Any

from ..schemas.summarizer import (
    TextSummaryRequest,
    TextSummaryResponse,
    SupportedFormatsResponse,
    DocumentListResponse,
    SummaryContent,
    SummaryType,
    SummaryLength,
    AIModel
)
from ..schemas.common import APIResponse, ProcessingStatus, FileType

router = APIRouter(prefix="/api/summarizer", tags=["📄 Document Summarizer"])

# In-memory "database" for uploaded documents
documents_db: List[Dict[str, Any]] = []


@router.post("/upload")
async def upload_and_summarize(
    summary_type: SummaryType = Form(...),
    summary_length: SummaryLength = Form(...),
    ai_model: AIModel = Form(...),
    file: UploadFile = File(...)
):
    """Upload + mock summarize."""
    try:
        if file.content_type not in [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type.")

        # Normalize values (Enum or raw string if form bypassed Enum coercion)
        st_value = getattr(summary_type, 'value', summary_type)
        model_value = getattr(ai_model, 'value', ai_model)

        doc_id = f"doc_{len(documents_db) + 1}"
        filename = file.filename or "unnamed_document"
        word_limit = 250 if summary_length == SummaryLength.MEDIUM else 100 if summary_length == SummaryLength.SHORT else 500

        extracted_text = (
            f"Mock extracted content from {filename}. This document covers Operating Systems process scheduling: FCFS, SJF, Round Robin, with criteria like utilization, throughput, waiting time, and response time."
        )

        # Map to existing enum names: BULLET_POINTS, PARAGRAPH.
        if summary_type == SummaryType.BULLET_POINTS:
            summary_text = (
                "• Process scheduling manages CPU allocation efficiently\n"
                "• FCFS simple but can cause convoy effect\n"
                "• SJF minimizes average waiting time (needs prediction)\n"
                "• Round Robin ensures fairness via quantum\n"
                "• Priority scheduling may starve without aging"
            )
        elif summary_type == SummaryType.PARAGRAPH:
            summary_text = (
                "This document provides an overview of process scheduling algorithms including FCFS, SJF, and Round Robin. "
                "It compares their characteristics, highlights trade-offs like convoy effect and prediction needs, and explains how quantum size impacts fairness. "
                f"Generated using {model_value}."
            )
        else:
            summary_text = (
                f"Operating Systems scheduling overview (type={st_value}) covering FCFS, SJF, Round Robin, metrics and trade-offs. Generated using {model_value}."
            )

        summary_trimmed = summary_text[:word_limit]
        summary_content = SummaryContent(
            summary=summary_trimmed,
            word_count=len(summary_trimmed.split()),
            keywords=["process scheduling", "FCFS", "SJF", "round robin", "operating systems"],
            key_concepts=["CPU Scheduling", "Process Management", "Algorithm Comparison", "Time Quantum"],
            confidence_score=0.94,
            focus_areas_covered=["Scheduling Algorithms", "Performance Metrics"],
            citations=[filename],
            subject_classification="computer science",
            processing_time=1.2,
        )

        # Map mime type to FileType enum best-effort
        mime_map = {
            "application/pdf": FileType.PDF,
            "text/plain": FileType.TXT,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
        }
        file_type_enum = mime_map.get(file.content_type, FileType.TXT)

        documents_db.append({
            "id": doc_id,
            "filename": filename,
            "file_type": file_type_enum,
            "size": 1024,
            "upload_time": datetime.now(),  # datetime object per schema
            "processing_status": ProcessingStatus.COMPLETED,
            # store extras separately
            "_summary": summary_content.dict(),
            "_extracted_text": extracted_text,
        })

        return {
            "success": True,
            "message": "Document processed and summarized successfully",
            "document_id": doc_id,
            "filename": filename,
            "summary": summary_content,
            "processing_time": 1.2,
            "timestamp": time.time(),
        }
    except HTTPException:
        raise
    except Exception as e:
        # Provide structured error for easier debugging while avoiding 500 trace exposure
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {e.__class__.__name__}: {e}")


@router.post("/text", response_model=TextSummaryResponse)
async def summarize_text(request: TextSummaryRequest):
    """Summarize raw text (mock)."""
    start_time = time.time()
    
    # Simulate processing time
    await asyncio.sleep(2.0)
    
    # Mock summaries based on type - matching frontend patterns
    mock_summaries = {
        "brief": "This is a brief summary of the main points from your content. It captures the essential information in a concise format.",
        "detailed": "This is a detailed summary that provides a comprehensive overview of your content. It includes the main concepts, key arguments, and important details while maintaining the original context and meaning. The summary preserves the logical flow and highlights the most significant information.",
        "bullet": "• Main point one from your content\\n• Key concept or argument presented\\n• Important detail or finding\\n• Supporting evidence or example\\n• Conclusion or final thought",
        "outline": "I. Introduction\\n   A. Main topic overview\\n   B. Context and background\\n\\nII. Key Points\\n   A. Primary argument\\n   B. Supporting details\\n   C. Evidence presented\\n\\nIII. Conclusion\\n   A. Summary of findings\\n   B. Implications"
    }
    
    summary_text = mock_summaries.get(request.summary_type.value, mock_summaries["detailed"])
    
    summary_content = SummaryContent(
        summary=summary_text,
        word_count=len(summary_text.split()),
        keywords=["analysis", "information", "content"],
        key_concepts=["Text Analysis", "Content Processing", "Information Extraction"],
        confidence_score=0.92,
        focus_areas_covered=[],
        citations=None,
        subject_classification="general",
        processing_time=time.time() - start_time
    )
    
    processing_time = time.time() - start_time
    
    return TextSummaryResponse(
        success=True,
        message=f"Text summarized successfully using {request.ai_model.value}",
        summary=summary_content,
        processing_time=processing_time
    )


@router.get("/formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    return SupportedFormatsResponse(
        file_formats=["pdf", "docx", "doc", "txt", "pptx"],
        ai_models=[
            {
                "value": "gpt-3.5-turbo",
                "label": "GPT-3.5 Turbo",
                "description": "Fast and efficient for most summarization tasks",
                "max_tokens": 4096
            },
            {
                "value": "gpt-4",
                "label": "GPT-4",
                "description": "Most advanced model with superior understanding",
                "max_tokens": 8192
            },
            {
                "value": "claude-3",
                "label": "Claude 3",
                "description": "Excellent for academic content and detailed analysis",
                "max_tokens": 100000
            },
            {
                "value": "gemini-pro",
                "label": "Gemini Pro",
                "description": "Google's advanced model for complex reasoning",
                "max_tokens": 32000
            }
        ],
        summary_types=[
            {
                "value": "detailed",
                "label": "Detailed Summary",
                "description": "Comprehensive overview with main concepts"
            },
            {
                "value": "brief",
                "label": "Brief Summary",
                "description": "Key points in 2-3 sentences"
            },
            {
                "value": "bullet",
                "label": "Bullet Points",
                "description": "Organized list of important points"
            },
            {
                "value": "outline",
                "label": "Outline Format",
                "description": "Structured hierarchical summary"
            },
            {
                "value": "academic",
                "label": "Academic Summary",
                "description": "Formal academic style with precise terminology"
            }
        ],
        extraction_types=[
            {
                "value": "text",
                "label": "Text Only",
                "description": "Extract text content only"
            },
            {
                "value": "images",
                "label": "Images Only",
                "description": "Extract and describe images"
            },
            {
                "value": "tables",
                "label": "Tables Only",
                "description": "Extract and structure table data"
            },
            {
                "value": "all",
                "label": "Everything",
                "description": "Extract text, images, and tables"
            }
        ],
        max_file_size=10485760
    )

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    # Transform stored dicts into objects matching DocumentInfo + exclude internal keys
    cleaned = []
    for d in documents_db:
        cleaned.append({
            "id": d["id"],
            "filename": d["filename"],
            "file_type": d["file_type"],
            "size": d["size"],
            "upload_time": d["upload_time"],
            "processing_status": d["processing_status"],
        })
    return DocumentListResponse(
        success=True,
        message=f"Retrieved {len(cleaned)} documents",
        documents=cleaned,
        total_count=len(cleaned)
    )

@router.delete("/documents/{document_id}", response_model=APIResponse)
async def delete_document(document_id: str):
    document = next((d for d in documents_db if d["id"] == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents_db.remove(document)
    
    return APIResponse(
        success=True,
        message="Document deleted successfully"
    )