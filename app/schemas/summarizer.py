from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from .common import APIResponse, ProcessingStatus, FileType

class AIModel(str, Enum):
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
    GEMINI = "gemini-pro"
    MISTRAL_7B = "mistral:7b"

class SummaryType(str, Enum):
    PARAGRAPH = "detailed"
    BULLET_POINTS = "bullet"
    KEY_CONCEPTS = "key_concepts"
    OUTLINE = "outline"
    ACADEMIC = "academic"
    BRIEF = "brief"

class SummaryLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    CUSTOM = "custom"

class ExtractionType(str, Enum):
    TEXT = "text"
    IMAGES = "images"
    TABLES = "tables"
    ALL = "all"

class ParserType(str, Enum):
    AUTO = "auto"
    PYMUPDF = "pymupdf"
    PDF_PLUMBER = "pdf_plumber"
    PYTHON_DOCX = "python_docx"
    OCR = "ocr"

class DocumentUploadRequest(BaseModel):
    summary_type: SummaryType = Field(SummaryType.PARAGRAPH, description="Type of summary to generate")
    summary_length: SummaryLength = Field(SummaryLength.MEDIUM, description="Desired length of the summary")
    ai_model: AIModel = Field(AIModel.GPT_35_TURBO, description="AI model to use for summarization")
    focus_areas: Optional[str] = Field(None, description="Comma-separated list of topics to focus on")
    parser_type: ParserType = Field(ParserType.AUTO, description="Parser to use for the document")

class TextSummaryRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Text to summarize")
    summary_type: SummaryType = Field(SummaryType.PARAGRAPH, description="Type of summary to generate")
    summary_length: SummaryLength = Field(SummaryLength.MEDIUM, description="Desired length of the summary")
    ai_model: AIModel = Field(AIModel.GPT_35_TURBO, description="AI model to use for summarization")

class ExtractedContent(BaseModel):
    text: str = Field(..., description="Extracted text")
    images: List[Dict[str, Any]] = Field(default=[], description="Extracted images")
    tables: List[Dict[str, Any]] = Field(default=[], description="Extracted tables")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")
    page_count: Optional[int] = Field(None, description="Total pages")
    word_count: Optional[int] = Field(None, description="Word count")

class DocumentInfo(BaseModel):
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    file_type: FileType = Field(..., description="File type")
    size: int = Field(..., description="File size in bytes")
    upload_time: datetime = Field(default_factory=datetime.now, description="Upload time")
    processing_status: ProcessingStatus = Field(..., description="Processing status")

class SummaryContent(BaseModel):
    summary: str = Field(..., description="Generated summary")
    word_count: int = Field(..., description="Summary word count")
    keywords: Optional[List[str]] = Field(None, description="Extracted keywords")
    key_concepts: Optional[List[str]] = Field(None, description="Key concepts identified")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence")
    focus_areas_covered: Optional[List[str]] = Field(None, description="Focus areas addressed")
    citations: Optional[List[str]] = Field(None, description="Source citations")
    subject_classification: Optional[str] = Field(None, description="Detected subject")
    processing_time: float = Field(..., description="Processing time")

class DocumentProcessResponse(APIResponse):
    document: DocumentInfo = Field(..., description="Information about the processed document")
    summary: SummaryContent = Field(..., description="The generated summary")

class TextSummaryResponse(APIResponse):
    summary: SummaryContent = Field(..., description="The generated summary")

class SupportedFormatsResponse(BaseModel):
    file_formats: List[str] = Field(..., description="Supported file formats")
    ai_models: List[Dict[str, Any]] = Field(..., description="Available AI models")
    summary_types: List[Dict[str, Any]] = Field(..., description="Summary types")
    extraction_types: List[Dict[str, Any]] = Field(..., description="Extraction options")
    max_file_size: int = Field(..., description="Max file size in bytes")

class DocumentListResponse(APIResponse):
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total_count: int = Field(..., description="Total document count")
